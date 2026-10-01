import math
from typing import Optional
from app.models.loan import EMICalculation


class EMICalculator:
    """Deterministic EMI calculator service"""
    
    @staticmethod
    def calculate_emi(
        principal: float,
        annual_interest_rate_percent: float,
        tenure_months: int
    ) -> EMICalculation:
        """
        Calculate EMI using standard formula
        
        EMI = [P x R x (1+R)^N] / [(1+R)^N-1]
        
        Where:
        P = Principal
        R = Monthly interest rate (annual rate / 12 / 100)
        N = Tenure in months
        """
        if principal <= 0:
            raise ValueError("Principal must be positive")
        if tenure_months <= 0:
            raise ValueError("Tenure must be positive")
        if annual_interest_rate_percent <= 0:
            raise ValueError("Interest rate must be positive")
        
        # Monthly interest rate
        monthly_rate = annual_interest_rate_percent / 12 / 100
        
        # Calculate EMI
        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            numerator = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
            denominator = (1 + monthly_rate) ** tenure_months - 1
            emi = numerator / denominator
        
        # Calculate totals
        total_amount = emi * tenure_months
        total_interest = total_amount - principal
        
        return EMICalculation(
            principal=principal,
            tenure_months=tenure_months,
            interest_rate_percent=annual_interest_rate_percent,
            emi=round(emi, 2),
            total_interest=round(total_interest, 2),
            total_amount=round(total_amount, 2),
            is_illustrative=True
        )
    
    @staticmethod
    def calculate_principal_from_emi(
        emi: float,
        annual_interest_rate_percent: float,
        tenure_months: int
    ) -> float:
        """
        Calculate principal from EMI
        
        P = [EMI x ((1+R)^N-1)] / [R x (1+R)^N]
        """
        monthly_rate = annual_interest_rate_percent / 12 / 100
        
        if monthly_rate == 0:
            return emi * tenure_months
        
        numerator = emi * ((1 + monthly_rate) ** tenure_months - 1)
        denominator = monthly_rate * (1 + monthly_rate) ** tenure_months
        
        return round(numerator / denominator, 2)
    
    @staticmethod
    def calculate_tenure_from_emi(
        principal: float,
        emi: float,
        annual_interest_rate_percent: float
    ) -> int:
        """
        Calculate tenure in months from EMI
        
        N = log(EMI / (EMI - P x R)) / log(1 + R)
        """
        monthly_rate = annual_interest_rate_percent / 12 / 100
        
        if monthly_rate == 0:
            return int(math.ceil(principal / emi))
        
        numerator = math.log(emi / (emi - principal * monthly_rate))
        denominator = math.log(1 + monthly_rate)
        
        months = numerator / denominator
        return int(math.ceil(months))
