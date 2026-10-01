from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConversationStage(str, Enum):
    """Conversation workflow stages"""
    GREETING = "greeting"
    INTENT_DETECTION = "intent_detection"
    LOAN_DISCOVERY = "loan_discovery"
    PROFILE_COLLECTION = "profile_collection"
    PRODUCT_MATCHING = "product_matching"
    ELIGIBILITY_CHECK = "eligibility_check"
    PRODUCT_COMPARISON = "product_comparison"
    POLICY_QUESTION = "policy_question"
    DOCUMENT_QUESTION = "document_question"
    CLARIFICATION = "clarification"
    HANDOFF = "handoff"
    COMPLETED = "completed"


class Intent(str, Enum):
    """Detected conversation intents"""
    LOAN_DISCOVERY = "loan_discovery"
    LOAN_ELIGIBILITY = "loan_eligibility"
    PRODUCT_COMPARISON = "product_comparison"
    INTEREST_RATE_QUESTION = "interest_rate_question"
    EMI_QUESTION = "emi_question"
    DOCUMENT_QUESTION = "document_question"
    REPAYMENT_QUESTION = "repayment_question"
    APPLICATION_PROCESS = "application_process"
    EXISTING_LOAN = "existing_loan"
    GENERAL_BANKING_QUESTION = "general_banking_question"
    COMPLAINT = "complaint"
    HUMAN_AGENT_REQUEST = "human_agent_request"
    UNKNOWN = "unknown"


class CustomerProfile(BaseModel):
    """Customer financial profile"""
    age: Optional[int] = None
    employment_type: Optional[str] = None  # salaried, self-employed, business
    occupation: Optional[str] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    existing_emi: Optional[float] = None
    credit_score: Optional[int] = None
    requested_loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    preferred_tenure_months: Optional[int] = None
    preferred_emi: Optional[float] = None
    employment_duration_months: Optional[int] = None
    location: Optional[str] = None


class CustomerPreferences(BaseModel):
    """Customer preferences"""
    priority: Optional[str] = None
    prefer_low_emi: bool = False
    prefer_lower_cost: bool = False
    prefer_longer_tenure: bool = False
    prefer_higher_amount: bool = False


class ConversationState(BaseModel):
    """Conversation session state"""
    conversation_id: str
    current_stage: ConversationStage = ConversationStage.GREETING
    intent: Intent = Intent.UNKNOWN
    customer_profile: CustomerProfile = Field(default_factory=CustomerProfile)
    customer_preferences: CustomerPreferences = Field(default_factory=CustomerPreferences)
    missing_fields: List[str] = Field(default_factory=list)
    candidate_products: List[str] = Field(default_factory=list)
    eligible_products: List[str] = Field(default_factory=list)
    ineligible_products: List[str] = Field(default_factory=list)
    additional_information_required: List[str] = Field(default_factory=list)
    last_question: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    """Conversation message"""
    role: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    audio_url: Optional[str] = None


class ConversationRequest(BaseModel):
    """Request to send a message"""
    conversation_id: Optional[str] = None
    message: str
    audio_data: Optional[bytes] = None


class ConversationResponse(BaseModel):
    """Response from conversation"""
    conversation_id: str
    transcript: str
    intent: Intent
    assistant_response: str
    profile_updates: Dict[str, Any] = Field(default_factory=dict)
    missing_information: List[str] = Field(default_factory=list)
    loan_matches: List[Dict[str, Any]] = Field(default_factory=list)
    workflow_stage: ConversationStage
    audio_url: Optional[str] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
