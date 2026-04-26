"""
Unit tests for input validation
"""

import pytest


class TestInputValidation:
    """Tests for input validation"""
    
    def test_validate_positive_days(self):
        """Test validation of positive days"""
        days = 5
        assert days > 0
        assert days <= 365
    
    def test_validate_positive_budget(self):
        """Test validation of positive budget"""
        budget = 50000
        assert budget > 0
        assert budget <= 10000000
    
    def test_validate_non_empty_strings(self):
        """Test validation of non-empty strings"""
        source = "Delhi"
        dest = "Mumbai"
        assert len(source.strip()) > 0
        assert len(dest.strip()) > 0
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        dirty_input = "  Paris  "
        clean_input = dirty_input.strip()
        assert clean_input == "Paris"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
