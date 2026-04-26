"""
Unit tests for service layer
"""

import pytest
from unittest.mock import patch, MagicMock


class TestIntentService:
    """Tests for IntentService"""
    
    def test_extract_valid_params(self, mock_intent_service):
        """Test extracting valid parameters"""
        message = "I want to travel to Paris for 5 days with 50000 budget"
        params = mock_intent_service.extract_params(message)
        
        assert params['dest'] == 'Mumbai'
        assert params['days'] == 5
        assert params['budget'] == 50000
    
    def test_extract_partial_params(self, mock_intent_service):
        """Test extracting partial parameters"""
        message = "I want to go to London"
        params = mock_intent_service.extract_params(message)
        
        assert 'dest' in params


class TestItineraryBuilder:
    """Tests for ItineraryBuilder"""
    
    def test_build_itinerary_success(self, mock_itinerary_builder):
        """Test successful itinerary building"""
        itinerary = mock_itinerary_builder.build(
            source='Delhi',
            dest='Mumbai',
            budget=50000,
            days=3,
            preferences='beach'
        )
        
        assert itinerary is not None
        assert len(itinerary) > 0
        assert 'Day' in itinerary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
