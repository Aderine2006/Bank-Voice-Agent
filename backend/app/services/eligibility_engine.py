from typing import List, Dict, Any
from app.models.loan import LoanProduct, EligibilityResult, EligibilityStatus, EmploymentType
from app.models.conversation import CustomerProfile
import logging

logger = logging.getLogger(__name__)


class EligibilityEngine:
    """Deterministic eligibility engine based on configured rules"""
    
    @staticmethod
    def check_eligibility(
        product: LoanProduct,
        profile: CustomerProfile
    ) -> EligibilityResult:
        """
        Check if customer is eligible for a loan product
        
        Returns deterministic eligibility result with reasons
        """
        reasons = []
        missing_fields = []
        status = EligibilityStatus.ELIGIBLE
        
        # Check age
        if profile.age is not None:
            if profile.age < product.minimum_age:
                status = EligibilityStatus.DOES_NOT_MEET_CRITERIA
                reasons.append(f"Age {profile.age} is below minimum requirement of {product.minimum_age}")
            elif profile.age > product.maximum_age:
                status = EligibilityStatus.DOES_NOT_MEET_CRITERIA
                reasons.append(f"Age {profile.age} exceeds maximum requirement of {product.maximum_age}")
        else:
            missing_fields.append("age")
            status = EligibilityStatus.MORE_INFO_REQUIRED
        
        # Check income
        if profile.monthly_income is not None:
            if profile.monthly_income < product.minimum_monthly_income:
                status = EligibilityStatus.DOES_NOT_MEET_CRITERIA
                reasons.append(
                    f"Monthly income ₹{profile.monthly_income:,.0f} is below "
                    f"minimum requirement of ₹{product.minimum_monthly_income:,.0f}"
                )
        else:
            missing_fields.append("monthly_income")
            if status == EligibilityStatus.ELIGIBLE:
                status = EligibilityStatus.MORE_INFO_REQUIRED
        
        # Check employment type
        if profile.employment_type is not None:
            emp_type_lower = profile.employment_type.lower().replace(" ", "_")
            if emp_type_lower not in [et.value for et in product.employment_types]:
                status = EligibilityStatus.DOES_NOT_MEET_CRITERIA
                reasons.append(
                    f"Employment type '{profile.employment_type}' is not supported. "
                    f"Supported types: {[et.value for et in product.employment_types]}"
                )
        else:
            missing_fields.append("employment_type")
            if status == EligibilityStatus.ELIGIBLE:
                status = EligibilityStatus.MORE_INFO_REQUIRED
        
        # Check loan amount
        if profile.requested_loan_amount is not None:
            if profile.requested_loan_amount < product.minimum_amount:
                status = EligibilityStatus.DOES_NOT_MEET_CRITERIA
                reasons.append(
                    f"Requested amount ₹{profile.requested_loan_amount:,.0f} is below "
                    f"minimum of ₹{product.minimum_amount:,.0f}"
                )
            elif profile.requested_loan_amount > product.maximum_amount:
                status = EligibilityStatus.DOES_NOT_MEET_CRITERIA
                reasons.append(
                    f"Requested amount ₹{profile.requested_loan_amount:,.0f} exceeds "
                    f"maximum of ₹{product.maximum_amount:,.0f}"
                )
        else:
            missing_fields.append("requested_loan_amount")
            if status == EligibilityStatus.ELIGIBLE:
                status = EligibilityStatus.MORE_INFO_REQUIRED
        
        # Check purpose applicability
        if profile.loan_purpose is not None:
            purpose_lower = profile.loan_purpose.lower()
            supported_purposes_lower = [p.lower() for p in product.supported_purposes]
            
            if not any(purpose_lower in sp for sp in supported_purposes_lower):
                status = EligibilityStatus.NOT_APPLICABLE
                reasons.append(
                    f"Loan purpose '{profile.loan_purpose}' is not applicable for this product. "
                    f"Supported purposes: {product.supported_purposes}"
                )
        
        # Check tenure preference
        if profile.preferred_tenure_months is not None:
            if profile.preferred_tenure_months < product.minimum_tenure_months:
                reasons.append(
                    f"Preferred tenure {profile.preferred_tenure_months} months is below "
                    f"minimum of {product.minimum_tenure_months} months"
                )
            elif profile.preferred_tenure_months > product.maximum_tenure_months:
                reasons.append(
                    f"Preferred tenure {profile.preferred_tenure_months} months exceeds "
                    f"maximum of {product.maximum_tenure_months} months"
                )
        
        # Calculate match score if eligible
        match_score = None
        factors = {}
        
        if status in [EligibilityStatus.ELIGIBLE, EligibilityStatus.MORE_INFO_REQUIRED]:
            match_score, factors = EligibilityEngine._calculate_match_score(
                product, profile
            )
        
        return EligibilityResult(
            product_id=product.product_id,
            product_name=product.product_name,
            status=status,
            reasons=reasons,
            missing_fields=missing_fields,
            match_score=match_score,
            factors=factors
        )
    
    @staticmethod
    def _calculate_match_score(
        product: LoanProduct,
        profile: CustomerProfile
    ) -> tuple[int, Dict[str, Any]]:
        """
        Calculate transparent match score based on factors
        
        Score is 0-100 based on how well the product matches the profile
        """
        score = 100
        factors = {}
        
        # Purpose match (high weight)
        if profile.loan_purpose:
            purpose_lower = profile.loan_purpose.lower()
            supported_purposes_lower = [p.lower() for p in product.supported_purposes]
            purpose_match = any(purpose_lower in sp for sp in supported_purposes_lower)
            factors["purpose_match"] = purpose_match
            if not purpose_match:
                score -= 30
        
        # Amount match (medium weight)
        if profile.requested_loan_amount:
            amount_in_range = (
                product.minimum_amount <= profile.requested_loan_amount <= product.maximum_amount
            )
            factors["amount_match"] = amount_in_range
            if not amount_in_range:
                score -= 25
        
        # Income match (medium weight)
        if profile.monthly_income:
            income_sufficient = profile.monthly_income >= product.minimum_monthly_income
            factors["income_match"] = income_sufficient
            if not income_sufficient:
                score -= 20
        
        # Employment type match (low weight)
        if profile.employment_type:
            emp_type_lower = profile.employment_type.lower().replace(" ", "_")
            employment_match = emp_type_lower in [et.value for et in product.employment_types]
            factors["employment_match"] = employment_match
            if not employment_match:
                score -= 15
        
        # Tenure preference match (low weight)
        if profile.preferred_tenure_months:
            tenure_match = (
                product.minimum_tenure_months <= profile.preferred_tenure_months <= product.maximum_tenure_months
            )
            factors["tenure_match"] = tenure_match
            if not tenure_match:
                score -= 10
        
        return max(0, score), factors
