from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.models.loan import EMICalculation, EligibilityResult
from app.services.emi_calculator import EMICalculator
from app.services.eligibility_engine import EligibilityEngine
from app.models.conversation import CustomerProfile
from app.models.loan import LoanProduct

router = APIRouter(prefix="/api/loans", tags=["loans"])


class EMICalculationRequest(BaseModel):
    principal: float
    annual_interest_rate_percent: float
    tenure_months: int


class EligibilityCheckRequest(BaseModel):
    product_id: str
    profile: CustomerProfile


def get_products() -> List[LoanProduct]:
    from app.main import products
    return products


@router.post("/calculate-emi", response_model=EMICalculation)
async def calculate_emi(request: EMICalculationRequest):
    """Calculate EMI for given parameters"""
    try:
        calculator = EMICalculator()
        return calculator.calculate_emi(
            request.principal,
            request.annual_interest_rate_percent,
            request.tenure_months
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/eligibility", response_model=EligibilityResult)
async def check_eligibility(
    request: EligibilityCheckRequest,
    products: List[LoanProduct] = Depends(get_products)
):
    """Check eligibility for a specific product"""
    # Find product
    product = None
    for p in products:
        if p.product_id == request.product_id:
            product = p
            break
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        engine = EligibilityEngine()
        return engine.check_eligibility(product, request.profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
