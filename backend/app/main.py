from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.core.config import settings
from app.core.logging import logger
from app.api import conversation, voice, products, loans, knowledge
from app.providers.llm.gemini import GeminiLLM
from app.providers.stt.faster_whisper import FasterWhisperSTT
from app.providers.tts.kokoro import KokoroTTS
from app.services.conversation_manager import ConversationManager
from app.services.response_generator import ResponseGenerator
from app.services.loan_matching import LoanMatchingEngine
from app.services.financial_extraction import FinancialExtractor
from app.services.intent_detector import IntentDetector
from app.models.loan import LoanProduct, LoanType, EmploymentType
import json
import os

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Conversational AI for smarter banking and loan discovery"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversation.router)
app.include_router(voice.router)
app.include_router(products.router)
app.include_router(loans.router)
app.include_router(knowledge.router)


# Load demo bank products
def load_demo_products() -> List[LoanProduct]:
    """Load NovaBank demo products"""
    products_path = os.path.join(settings.BANK_DATA_PATH, settings.DEFAULT_BANK_ID, "products.json")
    
    if os.path.exists(products_path):
        with open(products_path, 'r') as f:
            products_data = json.load(f)
            return [LoanProduct(**p) for p in products_data]
    else:
        # Return default demo products if file doesn't exist
        return get_default_demo_products()


def get_default_demo_products() -> List[LoanProduct]:
    """Get default demo products for NovaBank"""
    return [
        LoanProduct(
            product_id="PL001",
            product_name="Nova Personal Loan",
            bank_id="demo-bank",
            loan_type=LoanType.PERSONAL,
            purpose="Personal expenses and needs",
            minimum_amount=50000,
            maximum_amount=1500000,
            minimum_age=21,
            maximum_age=58,
            minimum_monthly_income=25000,
            employment_types=[EmploymentType.SALARIED, EmploymentType.SELF_EMPLOYED],
            minimum_tenure_months=12,
            maximum_tenure_months=60,
            interest_rate_range="10.5% - 14.5%",
            processing_fee="1.5% of loan amount",
            required_documents=[
                "Identity proof (Aadhaar/PAN)",
                "Address proof",
                "Income proof (salary slips)",
                "Bank statements (last 6 months)",
                "Passport size photograph"
            ],
            eligibility_rules={
                "minimum employment_duration_months": 6,
                "minimum_credit_score": 650
            },
            supported_purposes=[
                "wedding", "travel", "medical", "education", "home renovation",
                "debt consolidation", "emergency", "personal"
            ],
            description="Flexible personal loan for various needs"
        ),
        LoanProduct(
            product_id="HL001",
            product_name="Nova Home Improvement Loan",
            bank_id="demo-bank",
            loan_type=LoanType.HOME,
            purpose="Home renovation and improvement",
            minimum_amount=100000,
            maximum_amount=5000000,
            minimum_age=23,
            maximum_age=60,
            minimum_monthly_income=40000,
            employment_types=[EmploymentType.SALARIED, EmploymentType.SELF_EMPLOYED],
            minimum_tenure_months=24,
            maximum_tenure_months=120,
            interest_rate_range="9.5% - 12.5%",
            processing_fee="1% of loan amount",
            required_documents=[
                "Identity proof",
                "Address proof",
                "Income proof",
                "Property documents",
                "Bank statements",
                "Photograph"
            ],
            eligibility_rules={
                "minimum employment_duration_months": 12,
                "minimum_credit_score": 700
            },
            supported_purposes=[
                "home renovation", "home improvement", "furniture", "interior",
                "repair", "extension"
            ],
            description="Loan for home renovation and improvement projects"
        ),
        LoanProduct(
            product_id="VL001",
            product_name="Nova Vehicle Loan",
            bank_id="demo-bank",
            loan_type=LoanType.VEHICLE,
            purpose="Vehicle purchase",
            minimum_amount=100000,
            maximum_amount=3000000,
            minimum_age=21,
            maximum_age=58,
            minimum_monthly_income=30000,
            employment_types=[EmploymentType.SALARIED, EmploymentType.SELF_EMPLOYED],
            minimum_tenure_months=12,
            maximum_tenure_months=84,
            interest_rate_range="9.0% - 13.0%",
            processing_fee="1.25% of loan amount",
            required_documents=[
                "Identity proof",
                "Address proof",
                "Income proof",
                "Bank statements",
                "Vehicle quotation",
                "Photograph"
            ],
            eligibility_rules={
                "minimum employment_duration_months": 12,
                "minimum_credit_score": 680
            },
            supported_purposes=[
                "car", "bike", "vehicle", "automobile"
            ],
            description="Loan for new and used vehicle purchase"
        ),
        LoanProduct(
            product_id="EL001",
            product_name="Nova Education Loan",
            bank_id="demo-bank",
            loan_type=LoanType.EDUCATION,
            purpose="Education and skill development",
            minimum_amount=50000,
            maximum_amount=2000000,
            minimum_age=18,
            maximum_age=35,
            minimum_monthly_income=20000,
            employment_types=[EmploymentType.SALARIED, EmploymentType.SELF_EMPLOYED],
            minimum_tenure_months=12,
            maximum_tenure_months=60,
            interest_rate_range="10.0% - 13.5%",
            processing_fee="1% of loan amount",
            required_documents=[
                "Identity proof",
                "Address proof",
                "Income proof",
                "Admission confirmation",
                "Fee structure",
                "Academic records"
            ],
            eligibility_rules={
                "minimum_employment_duration_months": 6,
                "minimum_credit_score": 650
            },
            supported_purposes=[
                "education", "course", "degree", "certification", "skill development",
                "training", "studies"
            ],
            description="Loan for education and professional courses"
        ),
        LoanProduct(
            product_id="BL001",
            product_name="Nova Business Loan",
            bank_id="demo-bank",
            loan_type=LoanType.BUSINESS,
            purpose="Business expansion and working capital",
            minimum_amount=200000,
            maximum_amount=10000000,
            minimum_age=25,
            maximum_age=65,
            minimum_monthly_income=50000,
            employment_types=[EmploymentType.BUSINESS, EmploymentType.SELF_EMPLOYED],
            minimum_tenure_months=12,
            maximum_tenure_months=60,
            interest_rate_range="11.0% - 15.0%",
            processing_fee="2% of loan amount",
            required_documents=[
                "Identity proof",
                "Address proof",
                "Business registration",
                "Financial statements",
                "Bank statements",
                "GST returns",
                "Photograph"
            ],
            eligibility_rules={
                "minimum_business_years": 2,
                "minimum_credit_score": 700
            },
            supported_purposes=[
                "business", "working capital", "expansion", "equipment",
                "inventory", "startup"
            ],
            description="Loan for business growth and working capital"
        )
    ]


# Initialize providers (lazy loading)
llm_provider: GeminiLLM = None
stt_provider: FasterWhisperSTT = None
tts_provider: KokoroTTS = None

# Initialize services
conversation_manager: ConversationManager = None
response_generator: ResponseGenerator = None
loan_matching_engine: LoanMatchingEngine = None

# Load products
products: List[LoanProduct] = []


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global llm_provider, stt_provider, tts_provider
    global conversation_manager, response_generator, loan_matching_engine
    global products
    
    logger.info("Starting BankVoice AI backend...")
    
    # Load products
    products = load_demo_products()
    logger.info(f"Loaded {len(products)} loan products")
    
    # Initialize LLM provider
    if settings.GEMINI_API_KEY:
        llm_provider = GeminiLLM(
            api_key=settings.GEMINI_API_KEY,
            model=settings.LLM_MODEL
        )
        logger.info("Gemini LLM provider initialized")
    else:
        logger.warning("GEMINI_API_KEY not set, LLM features will be limited")
    
    # Initialize STT provider (lazy load)
    stt_provider = FasterWhisperSTT(
        model_size=settings.STT_MODEL,
        device=settings.STT_DEVICE,
        compute_type=settings.STT_COMPUTE_TYPE
    )
    logger.info("Faster-Whisper STT provider initialized (model will load on first use)")
    
    # Initialize TTS provider (lazy load)
    tts_provider = KokoroTTS(
        voice=settings.TTS_VOICE,
        language=settings.TTS_LANGUAGE
    )
    logger.info("Kokoro TTS provider initialized (model will load on first use)")
    
    # Initialize services
    if llm_provider:
        financial_extractor = FinancialExtractor(llm_provider)
        intent_detector = IntentDetector(llm_provider)
        loan_matching_engine = LoanMatchingEngine()
        conversation_manager = ConversationManager(
            financial_extractor,
            intent_detector,
            loan_matching_engine
        )
        response_generator = ResponseGenerator(llm_provider)
        
        logger.info("All services initialized successfully")
    else:
        logger.warning("Services requiring LLM not initialized")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "stt_provider": settings.STT_PROVIDER,
        "tts_provider": settings.TTS_PROVIDER,
        "products_loaded": len(products)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
