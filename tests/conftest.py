"""
Pytest fixtures and configuration for test suite
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_intent_service():
    """Mock IntentService for testing"""
    class MockIntentService:
        def extract_params(self, message):
            return {
                "source": "Delhi",
                "dest": "Mumbai",
                "days": 5,
                "budget": 50000,
                "preferences": "beach"
            }
    return MockIntentService()


@pytest.fixture
def mock_itinerary_builder():
    """Mock ItineraryBuilder for testing"""
    class MockItineraryBuilder:
        def build(self, source, dest, budget, days, preferences):
            return "Day 1: Arrive in Mumbai\nDay 2: Visit Gateway of India\nDay 3: Explore Colaba..."
    return MockItineraryBuilder()


@pytest.fixture
def sample_travel_params():
    """Sample valid travel parameters"""
    return {
        "source": "Delhi",
        "dest": "Mumbai",
        "days": 5,
        "budget": 50000,
        "preferences": "beach and culture"
    }


@pytest.fixture
def invalid_travel_params():
    """Invalid travel parameters for testing"""
    return {
        "source": "",
        "dest": "Mumbai",
        "days": -1,
        "budget": -5000,
        "preferences": ""
    }
