import pytest
from app.services.eligibility_engine import EligibilityEngine
from app.models.loan import LoanProduct, LoanType, EmploymentType, EligibilityStatus
from app.models.conversation import CustomerProfile


class TestEligibilityEngine:
    """Unit tests for Eligibility Engine"""
    
    def test_eligible_profile(self):
        """Test profile that meets all criteria"""
        engine = EligibilityEngine()
        
        product = LoanProduct(
            product_id="TEST001",
            product_name="Test Loan",
            bank_id="demo-bank",
            loan_type=LoanType.PERSONAL,
            purpose="Test",
            minimum_amount=50000,
            maximum_amount=1000000,
            minimum_age=21,
            maximum_age=58,
            minimum_monthly_income=25000,
            employment_types=[EmploymentType.SALARIED],
            minimum_tenure_months=12,
            maximum_tenure_months=60,
            interest_rate_range="10% - 14%",
            processing_fee="1%",
            required_documents=[],
            eligibility_rules={},
            supported_purposes=["personal"]
        )
        
        profile = CustomerProfile(
            age=30,
            monthly_income=50000,
            employment_type="salaried",
            requested_loan_amount=500000,
            loan_purpose="personal"
        )
        
        result = engine.check_eligibility(product, profile)
        
        assert result.status == EligibilityStatus.ELIGIBLE
        assert len(result.reasons) == 0
    
    def test_age_rejection(self):
        """Test rejection due to age"""
        engine = EligibilityEngine()
        
        product = LoanProduct(
            product_id="TEST001",
            product_name="Test Loan",
            bank_id="demo-bank",
            loan_type=LoanType.PERSONAL,
            purpose="Test",
            minimum_amount=50000,
            maximum_amount=1000000,
            minimum_age=25,
            maximum_age=58,
            minimum_monthly_income=25000,
            employment_types=[EmploymentType.SALARIED],
            minimum_tenure_months=12,
            maximum_tenure_months=60,
            interest_rate_range="10% - 14%",
            processing_fee="1%",
            required_documents=[],
            eligibility_rules={},
            supported_purposes=["personal"]
        )
        
        profile = CustomerProfile(
            age=20,  # Below minimum
            monthly_income=50000,
            employment_type="salaried",
            requested_loan_amount=500000,
            loan_purpose="personal"
        )
        
        result = engine.check_eligibility(product, profile)
        
        assert result.status == EligibilityStatus.DOES_NOT_MEET_CRITERIA
        assert any("age" in reason.lower() for reason in result.reasons)
    
    def test_income_rejection(self):
        """Test rejection due to insufficient income"""
        engine = EligibilityEngine()
        
        product = LoanProduct(
            product_id="TEST001",
            product_name="Test Loan",
            bank_id="demo-bank",
            loan_type=LoanType.PERSONAL,
            purpose="Test",
            minimum_amount=50000,
            maximum_amount=1000000,
            minimum_age=21,
            maximum_age=58,
            minimum_monthly_income=50000,
            employment_types=[EmploymentType.SALARIED],
            minimum_tenure_months=12,
            maximum_tenure_months=60,
            interest_rate_range="10% - 14%",
            processing_fee="1%",
            required_documents=[],
            eligibility_rules={},
            supported_purposes=["personal"]
        )
        
        profile = CustomerProfile(
            age=30,
            monthly_income=30000,  # Below minimum
            employment_type="salaried",
            requested_loan_amount=500000,
            loan_purpose="personal"
        )
        
        result = engine.check_eligibility(product, profile)
        
        assert result.status == EligibilityStatus.DOES_NOT_MEET_CRITERIA
        assert any("income" in reason.lower() for reason in result.reasons)
    
    def test_more_information_required(self):
        """Test when more information is needed"""
        engine = EligibilityEngine()
        
        product = LoanProduct(
            product_id="TEST001",
            product_name="Test Loan",
            bank_id="demo-bank",
            loan_type=LoanType.PERSONAL,
            purpose="Test",
            minimum_amount=50000,
            maximum_amount=1000000,
            minimum_age=21,
            maximum_age=58,
            minimum_monthly_income=25000,
            employment_types=[EmploymentType.SALARIED],
            minimum_tenure_months=12,
            maximum_tenure_months=60,
            interest_rate_range="10% - 14%",
            processing_fee="1%",
            required_documents=[],
            eligibility_rules={},
            supported_purposes=["personal"]
        )
        
        profile = CustomerProfile(
            age=30,
            # Missing income and employment type
            requested_loan_amount=500000,
            loan_purpose="personal"
        )
        
        result = engine.check_eligibility(product, profile)
        
        assert result.status == EligibilityStatus.MORE_INFO_REQUIRED
        assert "monthly_income" in result.missing_fields
        assert "employment_type" in result.missing_fields
