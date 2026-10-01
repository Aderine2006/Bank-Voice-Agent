from typing import List, Dict, Any
from app.models.loan import LoanProduct, EligibilityResult, ProductMatch, EMICalculation
from app.models.conversation import CustomerProfile, CustomerPreferences
from app.services.eligibility_engine import EligibilityEngine
from app.services.emi_calculator import EMICalculator
import logging

logger = logging.getLogger(__name__)


class LoanMatchingEngine:
    """Deterministic loan product matching engine"""
    
    def __init__(self):
        self.eligibility_engine = EligibilityEngine()
        self.emi_calculator = EMICalculator()
    
    def match_products(
        self,
        products: List[LoanProduct],
        profile: CustomerProfile,
        preferences: CustomerPreferences
    ) -> List[ProductMatch]:
        """
        Match loan products to customer profile
        
        Returns sorted list of product matches
        """
        matches = []
        
        for product in products:
            # Check eligibility
            eligibility = self.eligibility_engine.check_eligibility(product, profile)
            
            # Calculate EMI if eligible and amount known
            emi_calc = None
            if (
                eligibility.status in ["ELIGIBLE_BASED_ON_PROVIDED_INFORMATION", "MORE_INFORMATION_REQUIRED"]
                and profile.requested_loan_amount
                and profile.preferred_tenure_months
            ):
                try:
                    # Use middle of interest rate range for estimate
                    rate_range = product.interest_rate_range.replace("%", "").split("-")
                    if len(rate_range) == 2:
                        avg_rate = (float(rate_range[0]) + float(rate_range[1])) / 2
                    else:
                        avg_rate = float(rate_range[0])
                    
                    emi_calc = self.emi_calculator.calculate_emi(
                        principal=profile.requested_loan_amount,
                        annual_interest_rate_percent=avg_rate,
                        tenure_months=profile.preferred_tenure_months
                    )
                except Exception as e:
                    logger.warning(f"EMI calculation failed for {product.product_id}: {e}")
            
            matches.append(ProductMatch(
                product=product,
                eligibility=eligibility,
                emi_calculation=emi_calc
            ))
        
        # Sort matches based on preferences
        return self._sort_matches(matches, preferences, profile)
    
    def _sort_matches(
        self,
        matches: List[ProductMatch],
        preferences: CustomerPreferences,
        profile: CustomerProfile
    ) -> List[ProductMatch]:
        """Sort matches based on customer preferences"""
        
        def sort_key(match: ProductMatch) -> tuple:
            score = 0
            
            # Prioritize eligible products
            if match.eligibility.status == "ELIGIBLE_BASED_ON_PROVIDED_INFORMATION":
                score += 1000
            elif match.eligibility.status == "MORE_INFORMATION_REQUIRED":
                score += 500
            
            # Use match score from eligibility
            if match.eligibility.match_score:
                score += match.eligibility.match_score
            
            # Apply preferences
            if preferences.prefer_low_emi and match.emi_calculation:
                # Lower EMI is better
                score -= match.emi_calculation.emi / 1000
            
            if preferences.prefer_lower_cost and match.emi_calculation:
                # Lower total interest is better
                score -= match.emi_calculation.total_interest / 1000
            
            if preferences.prefer_higher_amount and profile.requested_loan_amount:
                # Higher max amount is better
                score += match.product.maximum_amount / 10000
            
            return (-score,)  # Negative for descending sort
        
        return sorted(matches, key=sort_key)
    
    def get_missing_information(
        self,
        matches: List[ProductMatch],
        profile: CustomerProfile
    ) -> List[str]:
        """
        Get list of missing information needed for evaluation
        """
        missing_fields = set()
        
        # Add missing fields from all products
        for match in matches:
            missing_fields.update(match.eligibility.missing_fields)
        
        # Always need these basic fields
        if profile.requested_loan_amount is None:
            missing_fields.add("requested_loan_amount")
        if profile.loan_purpose is None:
            missing_fields.add("loan_purpose")
        if profile.monthly_income is None:
            missing_fields.add("monthly_income")
        if profile.employment_type is None:
            missing_fields.add("employment_type")
        
        return sorted(list(missing_fields))
