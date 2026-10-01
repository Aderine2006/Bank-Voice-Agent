from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class LoanType(str, Enum):
    """Loan product types"""
    PERSONAL = "personal"
    HOME = "home"
    VEHICLE = "vehicle"
    EDUCATION = "education"
    BUSINESS = "business"


class EmploymentType(str, Enum):
    """Employment types"""
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    BUSINESS = "business"


class EligibilityStatus(str, Enum):
    """Product eligibility status"""
    ELIGIBLE = "ELIGIBLE_BASED_ON_PROVIDED_INFORMATION"
    MORE_INFO_REQUIRED = "MORE_INFORMATION_REQUIRED"
    DOES_NOT_MEET_CRITERIA = "DOES_NOT_MEET_CONFIGURED_CRITERIA"
    NOT_APPLICABLE = "NOT_APPLICABLE_TO_PURPOSE"


class LoanProduct(BaseModel):
    """Bank loan product"""
    product_id: str
    product_name: str
    bank_id: str
    loan_type: LoanType
    purpose: str
    minimum_amount: float
    maximum_amount: float
    minimum_age: int
    maximum_age: int
    minimum_monthly_income: float
    employment_types: List[EmploymentType]
    minimum_tenure_months: int
    maximum_tenure_months: int
    interest_rate_range: str  # e.g., "10.5% - 14.5%"
    processing_fee: str
    required_documents: List[str]
    eligibility_rules: Dict[str, Any]
    supported_purposes: List[str]
    description: Optional[str] = None


class EligibilityResult(BaseModel):
    """Eligibility check result"""
    product_id: str
    product_name: str
    status: EligibilityStatus
    reasons: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    match_score: Optional[int] = None
    factors: Dict[str, Any] = Field(default_factory=dict)


class EMICalculation(BaseModel):
    """EMI calculation result"""
    principal: float
    tenure_months: int
    interest_rate_percent: float
    emi: float
    total_interest: float
    total_amount: float
    is_illustrative: bool = True


class ProductMatch(BaseModel):
    """Product matching result"""
    product: LoanProduct
    eligibility: EligibilityResult
    emi_calculation: Optional[EMICalculation] = None
