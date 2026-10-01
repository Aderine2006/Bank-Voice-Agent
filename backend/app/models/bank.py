from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BankConfig(BaseModel):
    """Bank configuration"""
    bank_id: str
    bank_name: str
    display_name: str
    is_demo: bool = True
    description: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BankPolicy(BaseModel):
    """Bank policy"""
    policy_id: str
    bank_id: str
    policy_name: str
    policy_type: str  # eligibility, document, repayment, etc.
    content: str
    effective_date: Optional[datetime] = None


class DocumentReference(BaseModel):
    """Document reference for RAG"""
    document_id: str
    bank_id: str
    title: str
    file_path: str
    document_type: str  # pdf, txt, docx
    chunk_count: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
