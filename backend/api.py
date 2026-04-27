"""
Flask Backend API for AI Travel Planner
Provides RESTful endpoints for trip planning operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os
from typing import Dict, Any, Tuple
# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.intent_service import IntentService
from services.itinerary_builder import ItineraryBuilder
from llm.llm_client import LLMClient
from config.settings import OPENAI_API_KEY, DEBUG_MODE
from backend.errors import ValidationError, ServiceError, handle_error

# LOGGER SETUP

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

# FLASK APP INITIALIZATION

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)  # Enable CORS for frontend communication

# GLOBAL SERVICE INITIALIZATION

try:
    llm_client = LLMClient(OPENAI_API_KEY)
    intent_service = IntentService(OPENAI_API_KEY)
    itinerary_builder = ItineraryBuilder(llm_client)
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

# REQUEST VALIDATION HELPERS

def validate_travel_params(params: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate travel parameters for completeness and correctness
    
    Args:
        params: Dictionary containing source, dest, days, budget, preferences
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    required_fields = ['source', 'dest', 'days', 'budget', 'preferences']
    
    # Check for missing fields
    missing_fields = [f for f in required_fields if f not in params or params[f] is None]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Validate days
    try:
        days = int(params['days'])
        if days <= 0 or days > 365:
            return False, "Days must be between 1 and 365"
    except (ValueError, TypeError):
        return False, "Days must be a valid integer"
    
    # Validate budget
    try:
        budget = float(params['budget'])
        if budget <= 0 or budget > 10000000:  # Max 10M
            return False, "Budget must be between 1 and 10,000,000"
    except (ValueError, TypeError):
        return False, "Budget must be a valid number"
    
    # Validate text fields
    for field in ['source', 'dest', 'preferences']:
        if not isinstance(params[field], str) or len(params[field].strip()) == 0:
            return False, f"{field} must be a non-empty string"
    
    return True, ""

# API ENDPOINTS

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns: Status and service availability
    """
    return jsonify({
        'status': 'healthy',
        'services': {
            'llm': 'active',
            'intent_service': 'active',
            'itinerary_builder': 'active'
        }
    }), 200


@app.route('/api/extract-intent', methods=['POST'])
def extract_intent():
    """
    Extract travel intent/parameters from user message
    
    Expected JSON: {"message": "I want to travel to Paris for 5 days with 50000 budget"}
    Returns: {"source": "...", "dest": "...", "days": ..., "budget": ..., "preferences": "..."}
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message field is required'}), 400
        
        user_message = data['message'].strip()
        
        if len(user_message) == 0:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if len(user_message) > 5000:
            return jsonify({'error': 'Message too long (max 5000 characters)'}), 400
        
        logger.info(f"Extracting intent from message: {user_message[:100]}...")
        
        # Extract parameters using intent service
        params = intent_service.extract_params(user_message)
        
        logger.info(f"Extracted parameters: {params}")
        
        return jsonify({
            'success': True,
            'parameters': params
        }), 200
        
    except ValueError as e:
        logger.error(f"Intent extraction error: {str(e)}")
        return jsonify({'error': f"Failed to extract intent: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error in extract_intent: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/plan-trip', methods=['POST'])
def plan_trip():
    """
    Generate complete travel itinerary based on parameters
    
    Expected JSON: {
        "source": "Delhi",
        "dest": "Mumbai", 
        "days": 5,
        "budget": 50000,
        "preferences": "beach and culture"
    }
    
    Returns: {"itinerary": "...", "success": true}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate parameters
        is_valid, error_msg = validate_travel_params(data)
        if not is_valid:
            logger.warning(f"Invalid parameters: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        logger.info(f"Planning trip: {data['source']} -> {data['dest']} for {data['days']} days")
        
        # Build itinerary
        itinerary = itinerary_builder.build(
            source=data['source'],
            dest=data['dest'],
            budget=float(data['budget']),
            days=int(data['days']),
            preferences=data['preferences']
        )
        
        logger.info("Itinerary built successfully")
        
        return jsonify({
            'success': True,
            'itinerary': itinerary,
            'parameters': {
                'source': data['source'],
                'dest': data['dest'],
                'days': data['days'],
                'budget': data['budget'],
                'preferences': data['preferences']
            }
        }), 200
        
    except ValueError as e:
        logger.error(f"Validation error in plan_trip: {str(e)}")
        return jsonify({'error': f"Invalid parameters: {str(e)}"}), 400
    except ServiceError as e:
        logger.error(f"Service error in plan_trip: {str(e)}")
        return jsonify({'error': f"Service error: {str(e)}"}), 503
    except Exception as e:
        logger.error(f"Unexpected error in plan_trip: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Multi-turn chat endpoint for conversational trip planning
    
    Expected JSON: {
        "message": "user message",
        "context": {"source": "...", "dest": "...", ...}  # Optional previous context
    }
    
    Returns: {"response": "...", "parameters": {...}, "next_steps": []}
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message field is required'}), 400
        
        user_message = data['message'].strip()
        context = data.get('context', {})
        
        if len(user_message) == 0:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        logger.info(f"Processing chat message: {user_message[:100]}...")
        
        # Extract new parameters
        new_params = intent_service.extract_params(user_message)
        
        # Merge with existing context
        merged_params = {**context, **{k: v for k, v in new_params.items() if v is not None}}
        
        # Check which parameters are still missing
        required_fields = ['source', 'dest', 'days', 'budget', 'preferences']
        missing_fields = [f for f in required_fields if f not in merged_params or merged_params[f] is None]
        
        response_data = {
            'success': True,
            'parameters': merged_params,
            'missing_fields': missing_fields,
            'is_complete': len(missing_fields) == 0
        }
        
        # If all parameters are complete, generate itinerary
        if len(missing_fields) == 0:
            logger.info("All parameters provided, generating itinerary...")
            itinerary = itinerary_builder.build(
                source=merged_params['source'],
                dest=merged_params['dest'],
                budget=float(merged_params['budget']),
                days=int(merged_params['days']),
                preferences=merged_params['preferences']
            )
            response_data['itinerary'] = itinerary
            response_data['status'] = 'complete'
        else:
            response_data['status'] = 'incomplete'
            response_data['message'] = f"Please provide: {', '.join(missing_fields)}"
        
        return jsonify(response_data), 200
        
    except ValueError as e:
        logger.error(f"Chat processing error: {str(e)}")
        return jsonify({'error': f"Processing error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

# APPLICATION ENTRY POINT

if __name__ == '__main__':
    logger.info("Starting AI Travel Planner Backend API")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=DEBUG_MODE,
        use_reloader=DEBUG_MODE
    )
