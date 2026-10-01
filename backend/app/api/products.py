from fastapi import APIRouter, HTTPException
from typing import List
from app.models.loan import LoanProduct

router = APIRouter(prefix="/api/products", tags=["products"])


def get_products() -> List[LoanProduct]:
    from app.main import products
    return products


@router.get("", response_model=List[LoanProduct])
async def list_products(products: List[LoanProduct] = Depends(get_products)):
    """List all available loan products"""
    return products


@router.get("/{product_id}", response_model=LoanProduct)
async def get_product(
    product_id: str,
    products: List[LoanProduct] = Depends(get_products)
):
    """Get a specific loan product"""
    for product in products:
        if product.product_id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
