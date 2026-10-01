# BANKVOICE AI

**Conversational AI for smarter banking and loan discovery.**

A voice-first AI banking assistant designed for banks and financial institutions. Customers can speak naturally about loans, eligibility, and requirements while the system extracts financial information, matches products, and provides intelligent responses.

---

## 🎯 Product Vision

BANKVOICE AI enables natural voice conversations about:
- Personal loans, Home loans, Vehicle loans, Education loans, Business loans
- Loan eligibility and requirements
- Product comparison
- General banking FAQs

The system understands natural conversation instead of forcing customers through rigid forms.

**Example:**
> Customer: "I need around six lakh rupees. I earn about 55,000 a month and I'm looking for something for my house renovation."
>
> System extracts: purpose=home renovation, amount=600000, income=55000

---

## 🏗️ Architecture

```
CUSTOMER VOICE
       ↓
   STT ENGINE
       ↓
CONVERSATION MANAGER
       ↓
FINANCIAL EXTRACTION
       ↓
MISSING DATA DETECTOR
       ↓
   LOAN MATCHING
       ↓
PRODUCT DB + RAG
       ↓
ELIGIBILITY ENGINE
       ↓
RESPONSE GENERATOR
       ↓
   TTS ENGINE
       ↓
CUSTOMER HEARS RESPONSE
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI (Python)
- **LLM:** Gemini API (free tier)
- **STT:** Faster-Whisper (CPU, INT8 quantized)
- **TTS:** Kokoro-82M (local CPU)
- **Vector DB:** FAISS
- **Embeddings:** Sentence Transformers
- **Database:** SQLite
- **Validation:** Pydantic

### Frontend
- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Audio:** Web Audio API, MediaRecorder API

---

## 📋 Prerequisites

- Windows 11
- Python 3.9+
- Node.js 18+
- 8 GB RAM (CPU-only, no GPU required)
- Microphone for voice input

---

## 🚀 Installation (Windows PowerShell)

### 1. Clone the Repository
```powershell
cd "d:/Bank Voice Agent"
```

### 2. Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your GEMINI_API_KEY
# Get free API key from: https://makersuite.google.com/app/apikey
```

### 3. Frontend Setup

```powershell
# Navigate to frontend (new PowerShell window)
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local
```

### 4. Start Backend

```powershell
# In backend directory with venv activated
cd backend
.\venv\Scripts\activate
python -m app.main
```

Backend will run on: `http://localhost:8000`

### 5. Start Frontend

```powershell
# In frontend directory
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:3000`

---

## 🔑 Configuration

### Backend (.env)

```env
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
STT_PROVIDER=faster_whisper
STT_MODEL=tiny
TTS_PROVIDER=kokoro
DATABASE_URL=sqlite:///./data/bankvoice.db
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎬 Demo Flow

1. Open `http://localhost:3000`
2. Click the microphone button
3. Say: "I need a loan for my house renovation"
4. Ava will ask follow-up questions
5. Provide information: "About six lakh", "55,000 monthly income", "Salaried", "8,000 existing EMI"
6. System matches products and explains options

---

## 🏦 Demo Bank (NovaBank)

**IMPORTANT:** This is DEMO/FICTIONAL bank data. All rates, policies, and products are fictional examples for demonstration purposes only.

### Products
1. Nova Personal Loan (₹50K - ₹15L, 10.5% - 14.5%)
2. Nova Home Improvement Loan (₹1L - ₹50L, 9.5% - 12.5%)
3. Nova Vehicle Loan (₹1L - ₹30L, 9.0% - 13.0%)
4. Nova Education Loan (₹50K - ₹20L, 10.0% - 13.5%)
5. Nova Business Loan (₹2L - ₹1Cr, 11.0% - 15.0%)

---

## 🧪 Running Tests

```powershell
cd backend
.\venv\Scripts\activate
pytest tests/
```

---

## 📁 Project Structure

```
Bank Voice Agent/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI endpoints
│   │   ├── core/             # Configuration & logging
│   │   ├── models/           # Pydantic models
│   │   ├── providers/        # STT, LLM, TTS abstractions
│   │   └── services/         # Business logic
│   ├── data/
│   │   └── banks/
│   │       └── demo-bank/    # Demo bank data
│   ├── tests/                # Unit tests
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── components/       # React components
    │   ├── lib/              # API client
    │   └── page.tsx          # Main page
    └── package.json
```

---

## 🔒 Safety Principles

The system does NOT:
- Guarantee loan approval
- Claim guaranteed interest rates
- Fabricate financial products or policies
- Ask for passwords, OTPs, PINs, or CVV
- Store sensitive authentication credentials

The system clearly distinguishes:
1. Information
2. Eligibility based on configured rules
3. Estimated suitability
4. Final bank approval (belongs to bank's authorized process)

---

## 🎨 Design Principles

- Premium banking interface
- Dark/modern theme with green/lime accents
- Clean cards with rounded corners
- Smooth animations
- Strong typography
- Minimal clutter

---

## 📊 API Endpoints

### Conversation
- `POST /api/conversation/start` - Start new conversation
- `POST /api/conversation/message` - Send message
- `GET /api/conversation/{id}` - Get conversation state

### Voice
- `POST /api/voice/transcribe` - Transcribe audio
- `POST /api/voice/synthesize` - Synthesize speech

### Products
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get specific product

### Loans
- `POST /api/loans/calculate-emi` - Calculate EMI
- `POST /api/loans/eligibility` - Check eligibility

---

## 🔮 Future Extensibility

The architecture supports future additions:
- PostgreSQL database
- Redis caching
- Enterprise LLMs (OpenAI, Anthropic, etc.)
- Enterprise TTS
- Real-time WebRTC
- Telephony integration
- CRM integration
- Core Banking integration
- Multilingual support (Hindi, Tamil, etc.)
- Role-based access control
- Analytics dashboard

---

## 📝 License

This is a demonstration project. All bank data is fictional.

---

## 🤝 Contributing

This is an MVP demonstration. For production use, implement:
- Authentication & authorization
- Persistent database (PostgreSQL)
- Enterprise-grade security
- Comprehensive logging & monitoring
- Human agent handoff integration
- Real bank product data

---

## 📞 Support

For issues or questions, please refer to the code documentation or create an issue in the repository.

---

**Built with ❤️ for the future of conversational banking**
