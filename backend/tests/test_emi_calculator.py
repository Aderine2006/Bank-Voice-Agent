import pytest
from app.services.emi_calculator import EMICalculator


class TestEMICalculator:
    """Unit tests for EMI Calculator"""
    
    def test_calculate_emi_basic(self):
        """Test basic EMI calculation"""
        calculator = EMICalculator()
        result = calculator.calculate_emi(
            principal=100000,
            annual_interest_rate_percent=12,
            tenure_months=12
        )
        
        assert result.principal == 100000
        assert result.tenure_months == 12
        assert result.interest_rate_percent == 12
        assert result.emi > 0
        assert result.total_interest > 0
        assert result.total_amount > principal
        assert result.is_illustrative is True
    
    def test_calculate_emi_zero_interest(self):
        """Test EMI calculation with zero interest"""
        calculator = EMICalculator()
        result = calculator.calculate_emi(
            principal=120000,
            annual_interest_rate_percent=0,
            tenure_months=12
        )
        
        assert result.emi == 10000  # 120000 / 12
        assert result.total_interest == 0
    
    def test_calculate_emi_validation(self):
        """Test EMI calculation validation"""
        calculator = EMICalculator()
        
        # Negative principal
        with pytest.raises(ValueError):
            calculator.calculate_emi(-100000, 12, 12)
        
        # Zero tenure
        with pytest.raises(ValueError):
            calculator.calculate_emi(100000, 12, 0)
        
        # Negative interest
        with pytest.raises(ValueError):
            calculator.calculate_emi(100000, -12, 12)
    
    def test_calculate_principal_from_emi(self):
        """Test calculating principal from EMI"""
        calculator = EMICalculator()
        
        # First calculate EMI
        emi_result = calculator.calculate_emi(100000, 12, 12)
        
        # Then reverse calculate principal
        principal = calculator.calculate_principal_from_emi(
            emi_result.emi,
            12,
            12
        )
        
        assert abs(principal - 100000) < 1  # Allow small rounding error
    
    def test_calculate_tenure_from_emi(self):
        """Test calculating tenure from EMI"""
        calculator = EMICalculator()
        
        # First calculate EMI
        emi_result = calculator.calculate_emi(100000, 12, 12)
        
        # Then reverse calculate tenure
        tenure = calculator.calculate_tenure_from_emi(
            100000,
            emi_result.emi,
            12
        )
        
        assert tenure == 12
