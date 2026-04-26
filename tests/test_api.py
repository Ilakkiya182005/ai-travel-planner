"""
Unit tests for API endpoints
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from ai.api import app, validate_travel_params


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthCheck:
    """Tests for health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'services' in data


class TestExtractIntent:
    """Tests for intent extraction endpoint"""
    
    def test_extract_intent_valid_message(self, client):
        """Test intent extraction with valid message"""
        with patch('backend.api.intent_service') as mock_service:
            mock_service.extract_params.return_value = {
                'source': None,
                'dest': 'Paris',
                'days': 5,
                'budget': 50000,
                'preferences': 'museums'
            }
            
            response = client.post('/api/extract-intent',
                json={'message': 'I want to go to Paris for 5 days with 50000 budget'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['parameters']['dest'] == 'Paris'
    
    def test_extract_intent_missing_message(self, client):
        """Test intent extraction without message field"""
        response = client.post('/api/extract-intent', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_extract_intent_empty_message(self, client):
        """Test intent extraction with empty message"""
        response = client.post('/api/extract-intent', json={'message': '   '})
        assert response.status_code == 400
    
    def test_extract_intent_too_long_message(self, client):
        """Test intent extraction with message exceeding limit"""
        long_message = 'a' * 6000
        response = client.post('/api/extract-intent', json={'message': long_message})
        assert response.status_code == 400


class TestPlanTrip:
    """Tests for trip planning endpoint"""
    
    def test_plan_trip_valid_params(self, client, sample_travel_params):
        """Test trip planning with valid parameters"""
        with patch('backend.api.itinerary_builder') as mock_builder:
            mock_builder.build.return_value = "Your itinerary..."
            
            response = client.post('/api/plan-trip', json=sample_travel_params)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'itinerary' in data
    
    def test_plan_trip_missing_fields(self, client):
        """Test trip planning with missing required fields"""
        params = {
            'source': 'Delhi',
            'dest': 'Mumbai'
            # Missing days, budget, preferences
        }
        response = client.post('/api/plan-trip', json=params)
        assert response.status_code == 400
    
    def test_plan_trip_invalid_days(self, client, sample_travel_params):
        """Test trip planning with invalid days"""
        params = sample_travel_params.copy()
        params['days'] = 400  # Exceeds max
        response = client.post('/api/plan-trip', json=params)
        assert response.status_code == 400
    
    def test_plan_trip_invalid_budget(self, client, sample_travel_params):
        """Test trip planning with invalid budget"""
        params = sample_travel_params.copy()
        params['budget'] = -1000
        response = client.post('/api/plan-trip', json=params)
        assert response.status_code == 400


class TestChat:
    """Tests for multi-turn chat endpoint"""
    
    def test_chat_incomplete_params(self, client):
        """Test chat with incomplete parameters"""
        with patch('backend.api.intent_service') as mock_service:
            mock_service.extract_params.return_value = {
                'source': None,
                'dest': 'Bali',
                'days': 5,
                'budget': None,
                'preferences': None
            }
            
            response = client.post('/api/chat',
                json={'message': 'I want to go to Bali for 5 days'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['is_complete'] is False
            assert 'missing_fields' in data
    
    def test_chat_complete_params(self, client, sample_travel_params):
        """Test chat with complete parameters"""
        with patch('backend.api.intent_service') as mock_intent:
            with patch('backend.api.itinerary_builder') as mock_builder:
                mock_intent.extract_params.return_value = {
                    'source': sample_travel_params['source'],
                    'dest': sample_travel_params['dest'],
                    'days': sample_travel_params['days'],
                    'budget': sample_travel_params['budget'],
                    'preferences': sample_travel_params['preferences']
                }
                mock_builder.build.return_value = "Your itinerary..."
                
                response = client.post('/api/chat',
                    json={'message': 'Plan my trip'})
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['is_complete'] is True
                assert 'itinerary' in data
    
    def test_chat_missing_message(self, client):
        """Test chat without message"""
        response = client.post('/api/chat', json={})
        assert response.status_code == 400


# ============================================================================
# Validation Tests
# ============================================================================

class TestValidateTravelParams:
    """Tests for travel parameter validation"""
    
    def test_valid_params(self, sample_travel_params):
        """Test with valid parameters"""
        is_valid, error = validate_travel_params(sample_travel_params)
        assert is_valid is True
        assert error == ""
    
    def test_missing_source(self, sample_travel_params):
        """Test with missing source"""
        params = sample_travel_params.copy()
        params['source'] = None
        is_valid, error = validate_travel_params(params)
        assert is_valid is False
        assert 'source' in error
    
    def test_invalid_days_negative(self, sample_travel_params):
        """Test with negative days"""
        params = sample_travel_params.copy()
        params['days'] = -5
        is_valid, error = validate_travel_params(params)
        assert is_valid is False
        assert 'Days must be between 1 and 365' in error
    
    def test_invalid_days_too_high(self, sample_travel_params):
        """Test with days exceeding max"""
        params = sample_travel_params.copy()
        params['days'] = 400
        is_valid, error = validate_travel_params(params)
        assert is_valid is False
    
    def test_invalid_budget_negative(self, sample_travel_params):
        """Test with negative budget"""
        params = sample_travel_params.copy()
        params['budget'] = -5000
        is_valid, error = validate_travel_params(params)
        assert is_valid is False
    
    def test_invalid_budget_too_high(self, sample_travel_params):
        """Test with budget exceeding limit"""
        params = sample_travel_params.copy()
        params['budget'] = 20000000
        is_valid, error = validate_travel_params(params)
        assert is_valid is False
    
    def test_non_numeric_days(self, sample_travel_params):
        """Test with non-numeric days"""
        params = sample_travel_params.copy()
        params['days'] = "five"
        is_valid, error = validate_travel_params(params)
        assert is_valid is False
    
    def test_empty_source(self, sample_travel_params):
        """Test with empty source string"""
        params = sample_travel_params.copy()
        params['source'] = "   "
        is_valid, error = validate_travel_params(params)
        assert is_valid is False


# ============================================================================
# Error Handler Tests
# ============================================================================

class TestErrorHandlers:
    """Tests for error handlers"""
    
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error handling"""
        response = client.get('/api/plan-trip')  # Should be POST
        assert response.status_code == 405


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
