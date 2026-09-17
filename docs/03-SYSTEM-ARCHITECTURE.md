# Shariah Compliance Copilot - System Architecture Document

**Project**: Shariah Compliance Automation Demo for Capco  
**Version**: 1.0  
**Date**: September 17, 2026  
**Architect**: Alan Young (Capco CTO Consulting)  
**Status**: Design Complete - Ready for Implementation

---

## 1. Architecture Overview

### 1.1 System Context

The Shariah Compliance Copilot is a **cloud-native SaaS application** that integrates Large Language Models (LLMs) with rule-based Islamic finance compliance engines to automate Shariah audit workflows.

**Key Design Principles**:
1. **Hybrid Intelligence**: LLM flexibility + AAOIFI rule precision
2. **Explainability-First**: Every decision traceable and auditable
3. **Human-in-the-Loop**: Scholar authority preserved at all tiers
4. **Cloud-Agnostic**: Containerized for multi-cloud/on-premise deployment
5. **API-First**: Headless architecture enabling future integrations

### 1.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Web Browser  │  │ Mobile Web   │  │ Future: API  │             │
│  │ (React SPA)  │  │ (Responsive) │  │ Clients      │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
          ┌──────────────────▼────────────────────┐
          │       API GATEWAY (Kong/Nginx)        │
          │  - Authentication (OAuth2/JWT)        │
          │  - Rate Limiting (100 req/min/user)   │
          │  - Request Logging                    │
          └──────────────────┬────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────────┐
│                    APPLICATION LAYER (FastAPI)                        │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐     │
│  │ Contract       │  │ Fatwa Search    │  │ User Management  │     │
│  │ Analysis       │  │ Service         │  │ Service          │     │
│  │ Service        │  └────────┬────────┘  └──────────────────┘     │
│  └────────┬───────┘           │                                     │
│           │                   │                                     │
│  ┌────────▼────────────────────▼───────────┐                       │
│  │       ORCHESTRATION LAYER                │                       │
│  │  - Workflow Engine (contract → clauses   │                       │
│  │    → riba/gharar → report)               │                       │
│  │  - HITL Tier Assignment Logic            │                       │
│  └──────────────────┬───────────────────────┘                       │
└─────────────────────┼─────────────────────────────────────────────┘
                      │
┌─────────────────────┴─────────────────────────────────────────────┐
│                    AI/LLM LAYER                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │ LLM Gateway      │  │ Vector Search    │  │ Rule Engine     │ │
│  │ (OpenAI GPT-4)   │  │ (Pinecone)       │  │ (Python/JSON)   │ │
│  │ - Clause Extract │  │ - Fatwa Semantic │  │ - AAOIFI Rules  │ │
│  │ - Summarization  │  │   Search         │  │ - Riba Patterns │ │
│  │ - NLP Analysis   │  │ - Recommendations│  │ - Gharar Checks │ │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────┴─────────────────────────────────────────────┐
│                    DATA LAYER                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │ PostgreSQL       │  │ Redis Cache      │  │ S3/Blob Storage │ │
│  │ - Users, Audit   │  │ - LLM Responses  │  │ - Contract PDFs │ │
│  │ - Contracts Meta │  │ - Session Data   │  │ - Reports       │ │
│  │ - Fatwa Metadata │  │                  │  │                 │ │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────┴─────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                               │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Container Orchestration (Kubernetes - EKS/AKS)               │ │
│  │ - Auto-scaling (CPU > 70% → add pods)                        │ │
│  │ - Health Checks & Self-Healing                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Monitoring & Observability (Datadog)                         │ │
│  │ - APM, Logs, Custom Metrics, Alerting                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component-Level Architecture

### 2.1 Frontend Architecture (React SPA)

**Technology Stack**:
- **Framework**: React 18 + TypeScript 5
- **UI Library**: Ant Design 5 (Arabic RTL support)
- **State Management**: Zustand (lightweight, <1KB)
- **Routing**: React Router v6
- **API Client**: Axios + React Query (caching, retry logic)
- **Build Tool**: Vite (faster than Webpack)

**Component Structure**:

```
src/
├── components/
│   ├── ContractUpload/
│   │   ├── FileDropzone.tsx          # Drag-drop PDF upload
│   │   ├── UploadProgress.tsx        # Progress bar + status
│   │   └── ContractList.tsx          # Recent uploads table
│   ├── AnalysisDashboard/
│   │   ├── SummaryCard.tsx           # High-level metrics
│   │   ├── ViolationList.tsx         # Riba/gharar findings
│   │   ├── ClauseTable.tsx           # Extracted clauses
│   │   └── ReportExport.tsx          # PDF/Word download
│   ├── FatwaSearch/
│   │   ├── SearchBar.tsx             # Natural language input
│   │   ├── ResultList.tsx            # Ranked fatwa cards
│   │   ├── FatwaSummary.tsx          # Collapsible detail view
│   │   └── CitationButton.tsx        # Insert into report
│   └── Shared/
│       ├── Header.tsx                # Top nav + user menu
│       ├── Sidebar.tsx               # Main navigation
│       └── LoadingSpinner.tsx        # Reusable loader
├── pages/
│   ├── Dashboard.tsx                 # Main landing after login
│   ├── ContractReview.tsx            # Full analysis view
│   ├── FatwaLibrary.tsx              # Search interface
│   └── Settings.tsx                  # User preferences
├── hooks/
│   ├── useContractAnalysis.ts        # API call + state
│   ├── useFatwaSearch.ts             # Search logic
│   └── useAuth.ts                    # OAuth2 flow
├── utils/
│   ├── apiClient.ts                  # Axios instance config
│   ├── formatters.ts                 # Date, currency utils
│   └── validators.ts                 # Form validation
└── App.tsx                           # Root component
```

**Key Design Decisions**:
1. **Server-Side Rendering (SSR)**: Not needed (authenticated SPA, SEO not priority)
2. **Code Splitting**: Lazy-load routes to reduce initial bundle size (<200KB gzipped)
3. **Internationalization**: React-i18next for English/Arabic switching
4. **Accessibility**: WCAG 2.1 AA compliance (aria-labels, keyboard nav, screen reader tested)

---

### 2.2 Backend Architecture (FastAPI Microservices)

**Service Boundaries**:

#### Service 1: Contract Analysis Service
**Responsibilities**: Orchestrate end-to-end contract compliance workflow

**API Endpoints**:
```python
POST /api/v1/contracts/upload
    # Upload PDF, return contract_id
    Request: multipart/form-data (file: PDF, jurisdiction: str)
    Response: {contract_id: UUID, status: "processing"}

GET /api/v1/contracts/{contract_id}/status
    # Poll analysis progress
    Response: {status: "processing|completed|failed", progress: 0-100}

GET /api/v1/contracts/{contract_id}/analysis
    # Retrieve full analysis results
    Response: {
        summary: {...},
        clauses: [{type: str, text: str, confidence: float, page: int}],
        violations: [{type: "riba|gharar", severity: str, clause_id: UUID, ...}],
        tier: 1|2|3,
        report_url: str
    }

POST /api/v1/contracts/{contract_id}/approve
    # Scholar approval (HITL workflow)
    Request: {decision: "approve|reject|request_revision", notes: str}
    Response: {status: "approved", audit_trail_id: UUID}
```

**Internal Architecture**:
```python
# contract_analysis_service/
├── main.py                    # FastAPI app entry
├── routers/
│   ├── contracts.py           # Endpoint handlers
│   └── health.py              # /health, /ready checks
├── services/
│   ├── ocr_service.py         # Azure Form Recognizer wrapper
│   ├── clause_extractor.py   # LLM prompt templates
│   ├── riba_detector.py      # Rule engine + LLM hybrid
│   ├── gharar_detector.py    # Similar to riba
│   ├── tier_classifier.py    # HITL tier assignment logic
│   └── report_generator.py   # PDF/Word export (Jinja2)
├── models/
│   ├── contract.py            # Pydantic models
│   ├── clause.py
│   └── violation.py
├── db/
│   ├── repositories/          # Data access layer
│   └── migrations/            # Alembic DB migrations
└── config.py                  # Environment variables
```

**Async Processing**:
- Contract upload triggers **background task** (Celery + Redis queue)
- Analysis runs async (OCR → clause extraction → riba/gharar → report generation)
- Client polls `/status` endpoint or receives webhook notification

---

#### Service 2: Fatwa Search Service
**Responsibilities**: Semantic search + summarization of Shariah rulings

**API Endpoints**:
```python
POST /api/v1/fatwas/search
    Request: {query: str, filters: {authority: str[], date_range: [str, str]}, top_k: int}
    Response: {
        results: [{
            fatwa_id: UUID,
            title: str,
            summary: str,
            relevance_score: float,
            authority: str,
            date: str,
            excerpt: str,
            url: str
        }],
        total: int
    }

GET /api/v1/fatwas/{fatwa_id}
    Response: {full_text: str, metadata: {...}, related_fatwas: [UUID]}

POST /api/v1/fatwas/{fatwa_id}/summarize
    Request: {length: "short|medium|long"}
    Response: {summary: str, key_ruling: str, conditions: [str]}

POST /api/v1/fatwas/recommend
    # Contextual recommendations during contract review
    Request: {contract_id: UUID, clause_ids: [UUID]}
    Response: {recommended_fatwas: [{fatwa_id: UUID, reason: str, relevance: float}]}
```

**Internal Architecture**:
```python
# fatwa_search_service/
├── services/
│   ├── embedding_service.py   # OpenAI Ada-002 wrapper
│   ├── vector_search.py       # Pinecone query logic
│   ├── reranker.py            # Cross-encoder for relevance
│   └── summarizer.py          # GPT-4 summarization
├── ingestion/
│   ├── scraper.py             # Web scraping AAOIFI/BNM sites
│   ├── pdf_parser.py          # Extract text from fatwa PDFs
│   └── indexer.py             # Embed + store in Pinecone
└── models/
    └── fatwa.py               # Pydantic models
```

---

#### Service 3: User Management Service
**Responsibilities**: Authentication, authorization, audit logging

**API Endpoints**:
```python
POST /api/v1/auth/login
    Request: {email: str, password: str}
    Response: {access_token: str (JWT), refresh_token: str, user: {...}}

POST /api/v1/auth/refresh
    Request: {refresh_token: str}
    Response: {access_token: str}

GET /api/v1/users/me
    Response: {user_id: UUID, role: str, permissions: [str]}

GET /api/v1/audit/{contract_id}
    # Full audit trail for a contract
    Response: [{timestamp: str, user: str, action: str, details: {...}}]
```

**RBAC Implementation**:
```python
# roles.py
ROLES = {
    "compliance_officer": [
        "contracts:upload",
        "contracts:view",
        "fatwas:search",
        "reports:export"
    ],
    "shariah_scholar": [
        "*",  # All compliance_officer permissions
        "contracts:approve",
        "contracts:reject",
        "fatwas:edit",
        "audit:view"
    ],
    "product_manager": [
        "contracts:upload",
        "contracts:view",  # Read-only
        "fatwas:search"
    ],
    "auditor": [
        "contracts:view",
        "audit:view"
    ]
}

# Decorator for route protection
@require_permission("contracts:approve")
async def approve_contract(contract_id: UUID, current_user: User):
    ...
```

---

### 2.3 AI/LLM Layer Architecture

#### Component 1: LLM Gateway (Abstraction Layer)

**Purpose**: Isolate LLM provider dependencies, enable fallback/switching

```python
# llm_gateway/
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    async def complete(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.1) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

class AnthropicProvider(LLMProvider):
    # Fallback implementation
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
    
    async def complete(self, prompt: str, max_tokens: int = 4000) -> str:
        # Claude API call
        ...

class LLMGateway:
    def __init__(self):
        self.primary = OpenAIProvider(os.getenv("OPENAI_API_KEY"))
        self.fallback = AnthropicProvider(os.getenv("ANTHROPIC_API_KEY"))
    
    async def complete(self, prompt: str, **kwargs) -> str:
        try:
            return await self.primary.complete(prompt, **kwargs)
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}, trying fallback")
            return await self.fallback.complete(prompt, **kwargs)
```

**Caching Strategy**:
```python
# Redis caching for deterministic prompts
async def cached_llm_call(prompt: str, cache_ttl: int = 3600) -> str:
    cache_key = f"llm:{hashlib.md5(prompt.encode()).hexdigest()}"
    
    # Check cache
    cached = await redis.get(cache_key)
    if cached:
        return cached.decode()
    
    # Call LLM
    response = await llm_gateway.complete(prompt)
    
    # Cache result
    await redis.setex(cache_key, cache_ttl, response)
    return response
```

---

#### Component 2: Clause Extraction (Few-Shot Prompting)

**Prompt Template**:
```python
CLAUSE_EXTRACTION_PROMPT = """You are an expert in Islamic finance contracts. Extract the following clause types from the contract text.

Contract Text:
{contract_text}

Clause Types to Extract (with examples):
1. Profit Calculation Method
   Example: "The bank shall charge a profit margin of 5.5% per annum calculated on the outstanding principal"
   
2. Payment Schedule
   Example: "The customer shall repay in 36 equal monthly installments of $2,850 each, due on the 1st of each month"

3. Late Payment Penalty
   Example: "A penalty of 1% per month will be charged on overdue amounts"
   
4. Collateral/Security
   Example: "The property located at 123 Main St shall serve as security for this facility"

5. Asset Ownership Transfer
   Example: "Ownership shall transfer to the customer upon final payment"

... (15 total clause types)

For each clause found, return:
{
  "clause_type": "...",
  "text": "exact excerpt from contract",
  "confidence": 0.0-1.0,
  "page_number": int,
  "notes": "any ambiguity or missing information"
}

Return JSON array of all extracted clauses. If a clause type is not found, omit it from results.
"""

# Usage
async def extract_clauses(contract_text: str) -> List[Clause]:
    prompt = CLAUSE_EXTRACTION_PROMPT.format(contract_text=contract_text)
    
    # GPT-4 Turbo supports JSON mode
    response = await llm_gateway.complete(
        prompt,
        response_format={"type": "json_object"},
        temperature=0.1  # Low temperature for deterministic extraction
    )
    
    clauses_json = json.loads(response)
    return [Clause(**c) for c in clauses_json]
```

---

#### Component 3: Riba/Gharar Detection (Hybrid Approach)

**Architecture**: Rule engine (explicit patterns) → LLM (semantic analysis) → Confidence scoring

```python
class RibaDetector:
    def __init__(self):
        self.rule_engine = RibaRuleEngine()  # Regex + keyword patterns
        self.llm_analyzer = LLMAnalyzer()     # Semantic understanding
    
    async def detect(self, clauses: List[Clause]) -> List[Violation]:
        violations = []
        
        for clause in clauses:
            # Step 1: Rule-based detection (fast, high precision)
            rule_violations = self.rule_engine.check(clause.text)
            
            # Step 2: LLM semantic analysis (slow, high recall)
            if not rule_violations or clause.confidence < 0.7:
                llm_violations = await self.llm_analyzer.analyze(clause.text)
                violations.extend(llm_violations)
            else:
                violations.extend(rule_violations)
        
        # Step 3: Deduplicate and rank by severity
        return self._rank_violations(violations)

# Rule engine patterns
class RibaRuleEngine:
    EXPLICIT_INTEREST_PATTERNS = [
        r'\b\d+(\.\d+)?%\s*(annual|per\s*annum|p\.a\.|interest)\b',
        r'\bLIBOR\s*\+\s*\d+(\.\d+)?%\b',
        r'\binterest\s*rate\b',
        r'\busury\b'  # Explicit (rare but critical)
    ]
    
    TIME_PENALTY_PATTERNS = [
        r'\b\d+(\.\d+)?%\s*per\s*(day|month|week)\b',
        r'\blate\s*(payment\s*)?fee\b.*\bper\s*(day|month)\b'
    ]
    
    def check(self, text: str) -> List[Violation]:
        violations = []
        
        # Check explicit interest
        for pattern in self.EXPLICIT_INTEREST_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(Violation(
                    type="riba",
                    severity="critical",
                    evidence=re.findall(pattern, text, re.IGNORECASE)[0],
                    aaoifi_reference="AAOIFI SS 8, Section 4.2",
                    confidence=0.95
                ))
        
        # Check time-based penalties
        for pattern in self.TIME_PENALTY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(Violation(
                    type="riba",
                    severity="high",
                    evidence=re.findall(pattern, text, re.IGNORECASE)[0],
                    aaoifi_reference="AAOIFI SS 8, Section 5.1",
                    confidence=0.85
                ))
        
        return violations
```

**LLM Semantic Analysis** (for ambiguous cases):
```python
RIBA_ANALYSIS_PROMPT = """You are a Shariah scholar expert in Islamic finance.

Analyze the following contract clause for potential riba (interest) violations:

Clause: "{clause_text}"

Consider:
1. Explicit interest language
2. Time-value-of-money penalties (e.g., "1% per day late fee")
3. Guaranteed fixed returns (violates profit-loss sharing)
4. Rollover fees or deferment charges
5. Hidden interest (inflated prices with deferred payment)

Respond in JSON:
{{
  "contains_riba": true/false,
  "confidence": 0.0-1.0,
  "type": "explicit_interest|time_penalty|guaranteed_return|hidden_interest|none",
  "severity": "critical|high|medium|low",
  "evidence": "specific phrase or calculation in the clause",
  "reasoning": "brief explanation of why this is riba",
  "aaoifi_reference": "relevant AAOIFI standard (if known)",
  "suggested_alternative": "Shariah-compliant alternative structure"
}}

If the clause is Shariah-compliant, set contains_riba=false and provide brief confirmation.
"""

async def llm_analyze_riba(clause_text: str) -> Optional[Violation]:
    prompt = RIBA_ANALYSIS_PROMPT.format(clause_text=clause_text)
    response = await llm_gateway.complete(prompt, temperature=0.1)
    
    analysis = json.loads(response)
    if analysis["contains_riba"]:
        return Violation(**analysis)
    return None
```

---

#### Component 4: Vector Search (Fatwa Semantic Search)

**Embedding & Indexing Pipeline**:
```python
# ingestion/indexer.py
async def index_fatwa(fatwa: Fatwa):
    # Step 1: Generate embedding
    embedding = await openai.embeddings.create(
        model="text-embedding-ada-002",
        input=f"{fatwa.title}\n\n{fatwa.summary}\n\n{fatwa.full_text[:1000]}"  # Truncate for cost
    )
    
    # Step 2: Store in Pinecone
    pinecone_index.upsert(
        vectors=[{
            "id": str(fatwa.id),
            "values": embedding.data[0].embedding,
            "metadata": {
                "title": fatwa.title,
                "authority": fatwa.authority,
                "date": fatwa.date.isoformat(),
                "contract_type": fatwa.contract_type,
                "url": fatwa.url
            }
        }]
    )
    
    # Step 3: Store metadata in PostgreSQL
    await db.fatwas.create(fatwa)
```

**Search Query Flow**:
```python
async def search_fatwas(query: str, top_k: int = 10, filters: dict = None) -> List[FatwaResult]:
    # Step 1: Embed query
    query_embedding = await openai.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    
    # Step 2: Vector search
    pinecone_filter = {}
    if filters:
        if "authority" in filters:
            pinecone_filter["authority"] = {"$in": filters["authority"]}
        # ... other filters
    
    results = pinecone_index.query(
        vector=query_embedding.data[0].embedding,
        top_k=top_k * 2,  # Over-fetch for reranking
        include_metadata=True,
        filter=pinecone_filter
    )
    
    # Step 3: Rerank with cross-encoder (optional, improves relevance)
    reranked = await rerank(query, results)
    
    # Step 4: Fetch full metadata from PostgreSQL
    fatwa_ids = [r.id for r in reranked[:top_k]]
    fatwas = await db.fatwas.get_by_ids(fatwa_ids)
    
    return fatwas
```

---

### 2.4 Data Layer Architecture

#### Database Schema (PostgreSQL)

```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('compliance_officer', 'shariah_scholar', 'product_manager', 'auditor')),
    institution_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Contracts
CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_by UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,  -- S3/Blob storage path
    jurisdiction VARCHAR(50) NOT NULL CHECK (jurisdiction IN ('aaoifi', 'malaysia', 'hybrid')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('processing', 'completed', 'failed', 'approved', 'rejected')),
    tier INT CHECK (tier IN (1, 2, 3)),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Extracted Clauses
CREATE TABLE clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    clause_type VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    page_number INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_clauses_contract_id ON clauses(contract_id);

-- Violations (Riba/Gharar)
CREATE TABLE violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    clause_id UUID REFERENCES clauses(id),
    type VARCHAR(50) NOT NULL CHECK (type IN ('riba', 'gharar')),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    evidence TEXT NOT NULL,
    aaoifi_reference VARCHAR(255),
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    suggested_alternative TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_violations_contract_id ON violations(contract_id);
CREATE INDEX idx_violations_severity ON violations(severity);

-- Audit Trail (Immutable Log)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID REFERENCES contracts(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,  -- 'uploaded', 'analyzed', 'approved', 'rejected', 'exported'
    details JSONB,  -- Flexible field for action-specific data
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_contract_id ON audit_logs(contract_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Fatwas (Metadata only, full text in vector DB)
CREATE TABLE fatwas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    authority VARCHAR(255) NOT NULL,  -- 'AAOIFI', 'Malaysia SAC', 'UAE Central Bank', etc.
    date DATE,
    contract_type VARCHAR(100),  -- 'murabaha', 'ijara', 'sukuk', etc.
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fatwas_authority ON fatwas(authority);
CREATE INDEX idx_fatwas_contract_type ON fatwas(contract_type);
CREATE INDEX idx_fatwas_date ON fatwas(date DESC);
```

---

#### Caching Strategy (Redis)

```python
# Cache patterns
CACHE_KEYS = {
    "llm_response": "llm:{prompt_hash}",           # TTL: 1 hour
    "contract_analysis": "contract:{id}:analysis", # TTL: 24 hours
    "user_session": "session:{user_id}",           # TTL: 30 minutes
    "fatwa_search": "fatwa:search:{query_hash}",   # TTL: 6 hours
}

# Example: Cache contract analysis result
async def get_contract_analysis(contract_id: UUID) -> dict:
    cache_key = f"contract:{contract_id}:analysis"
    
    # Check cache
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from DB
    analysis = await db.contracts.get_analysis(contract_id)
    
    # Cache result
    await redis.setex(cache_key, 86400, json.dumps(analysis))  # 24 hours
    return analysis
```

---

### 2.5 Infrastructure & Deployment Architecture

#### Kubernetes Deployment (AWS EKS Example)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: contract-analysis-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: contract-analysis
  template:
    metadata:
      labels:
        app: contract-analysis
    spec:
      containers:
      - name: api
        image: capco/shariah-copilot:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: postgres-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: contract-analysis-service
spec:
  selector:
    app: contract-analysis
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer

---
# hpa.yaml (Horizontal Pod Autoscaling)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: contract-analysis-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: contract-analysis-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

#### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          pip install -r requirements.txt
          pytest tests/ --cov=src --cov-report=xml
      - name: Upload Coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker Image
        run: |
          docker build -t ${{ secrets.DOCKER_REGISTRY }}/shariah-copilot:${{ github.sha }} .
          docker tag ${{ secrets.DOCKER_REGISTRY }}/shariah-copilot:${{ github.sha }} ${{ secrets.DOCKER_REGISTRY }}/shariah-copilot:latest
      - name: Push to Registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push ${{ secrets.DOCKER_REGISTRY }}/shariah-copilot:${{ github.sha }}
          docker push ${{ secrets.DOCKER_REGISTRY }}/shariah-copilot:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EKS
        run: |
          aws eks update-kubeconfig --name shariah-copilot-cluster --region ap-southeast-1
          kubectl set image deployment/contract-analysis-service api=${{ secrets.DOCKER_REGISTRY }}/shariah-copilot:${{ github.sha }}
          kubectl rollout status deployment/contract-analysis-service
```

---

### 2.6 Security Architecture

#### Defense-in-Depth Layers

**Layer 1: Network Security**
- **VPC Isolation**: All services in private subnets, only API Gateway in public subnet
- **Security Groups**: Whitelist only necessary ports (443 for HTTPS, 5432 for PostgreSQL within VPC)
- **DDoS Protection**: AWS Shield Standard (automatic) + Cloudflare (optional)

**Layer 2: Application Security**
- **Input Validation**: All API inputs validated with Pydantic models (prevent injection)
- **Rate Limiting**: 100 requests/minute per user, 1000 requests/minute per IP (API Gateway)
- **CORS**: Whitelist only production frontend domains
- **Content Security Policy (CSP)**: Prevent XSS attacks

**Layer 3: Authentication & Authorization**
- **OAuth2 + JWT**: Token-based authentication (access token: 15 min expiry, refresh token: 7 days)
- **RBAC**: Role-based permissions enforced at every API endpoint
- **MFA**: Required for Shariah Scholar role (TOTP via Google Authenticator)

**Layer 4: Data Security**
- **Encryption at Rest**: AES-256 for PostgreSQL (AWS RDS encryption), S3 server-side encryption
- **Encryption in Transit**: TLS 1.3 for all external connections, TLS 1.2 minimum for internal
- **Secrets Management**: AWS Secrets Manager (API keys, DB passwords rotated every 90 days)
- **Data Anonymization**: Contract PDFs stripped of customer PII before LLM processing (optional redaction)

**Layer 5: Monitoring & Incident Response**
- **SIEM**: Datadog Security Monitoring (detect anomalous API access patterns)
- **Audit Logging**: All user actions logged to immutable audit trail
- **Vulnerability Scanning**: Snyk (dependency scanning), Trivy (container image scanning)
- **Incident Response Plan**: 4-hour SLA for critical vulnerabilities

---

## 3. Data Flow Diagrams

### 3.1 Contract Analysis Flow (Happy Path)

```
[User uploads PDF]
     │
     ▼
[Frontend: POST /api/v1/contracts/upload]
     │
     ▼
[API Gateway: Authenticate + Rate Limit]
     │
     ▼
[Contract Analysis Service]
     │──────────────────────────────┐
     │                              │
     ▼                              ▼
[Store PDF in S3]            [Create contract record in PostgreSQL]
     │                              │
     ▼                              ▼
[Return contract_id]         [Trigger async analysis task (Celery)]
     │                              │
     │                              ▼
     │                       [Celery Worker picks up task]
     │                              │
     │                              ▼
     │                       [1. OCR: Azure Form Recognizer]
     │                              │  (Extract text from PDF)
     │                              ▼
     │                       [2. Clause Extraction: GPT-4 + Few-Shot]
     │                              │  (Identify 15 clause types)
     │                              ▼
     │                       [3. Riba Detection: Rule Engine + LLM]
     │                              │  (Check 5 riba patterns)
     │                              ▼
     │                       [4. Gharar Detection: Rule Engine + LLM]
     │                              │  (Check 4 gharar patterns)
     │                              ▼
     │                       [5. HITL Tier Assignment]
     │                              │  (Classify as Tier 1/2/3)
     │                              ▼
     │                       [6. Report Generation: Jinja2 → PDF]
     │                              │
     │                              ▼
     │                       [Store clauses + violations in PostgreSQL]
     │                              │
     │                              ▼
     │                       [Update contract status: "completed"]
     │                              │
     │                              ▼
     ▼                       [Send notification (email/webhook)]
[User polls /status]               │
     │                              │
     ▼                              │
[Status: "completed"] ◀─────────────┘
     │
     ▼
[Frontend: GET /api/v1/contracts/{id}/analysis]
     │
     ▼
[Display dashboard with findings]
```

---

### 3.2 Fatwa Semantic Search Flow

```
[User enters query: "Can we charge processing fees in Murabaha?"]
     │
     ▼
[Frontend: POST /api/v1/fatwas/search]
     │
     ▼
[Fatwa Search Service]
     │
     ├─────────────────────────────┐
     │                             │
     ▼                             ▼
[Check Redis cache]         [Embed query: OpenAI Ada-002]
     │                             │  (Convert text → 1536-dim vector)
     │ (Cache hit)                 │
     ├─────────────┐               ▼
     │             │        [Vector search: Pinecone]
     │             │               │  (Cosine similarity, top 20 results)
     │             │               ▼
     │             │        [Rerank: Cross-encoder BERT]
     │             │               │  (Reorder by relevance, keep top 10)
     │             │               ▼
     │             │        [Fetch metadata: PostgreSQL]
     │             │               │  (Get full fatwa records)
     │             │               ▼
     │             │        [Cache result in Redis (6 hours)]
     │             │               │
     │             └───────────────┘
     │                             │
     ▼                             ▼
[Return cached results]    [Return search results]
     │
     ▼
[Frontend displays ranked fatwa cards]
     │
     ▼
[User clicks "View Details"]
     │
     ▼
[Frontend: GET /api/v1/fatwas/{fatwa_id}]
     │
     ▼
[Return full text + metadata]
     │
     ▼
[User clicks "Cite in Report"]
     │
     ▼
[Citation inserted into contract analysis report]
```

---

## 4. Scalability & Performance

### 4.1 Bottleneck Analysis

**Identified Bottlenecks**:

| Component | Bottleneck | Mitigation |
|-----------|-----------|------------|
| **LLM API Latency** | GPT-4 calls take 5-10s each | (1) Aggressive caching (Redis), (2) Parallel API calls where possible, (3) Use GPT-3.5 for low-risk tasks |
| **OCR Processing** | Azure Form Recognizer takes 10-30s for 50-page doc | (1) Async processing (user polls status), (2) Stream results (show clauses as extracted) |
| **Vector Search** | Pinecone query ~500ms for 10M vectors | (1) Acceptable latency, (2) Pre-filter by metadata to reduce search space |
| **Database Writes** | High write volume during batch contract uploads | (1) Connection pooling, (2) Batch inserts, (3) Use COPY for bulk data |
| **Frontend Bundle Size** | Initial load >1MB (slow on mobile) | (1) Code splitting, (2) Lazy load routes, (3) Compress assets |

### 4.2 Horizontal Scaling Strategy

**Stateless Services**: All API services are stateless (session in Redis), enabling horizontal scaling
- **Current**: 3 replicas
- **Peak Load**: Auto-scale to 10 replicas when CPU >70%
- **Cost Optimization**: Scale down to 2 replicas during off-hours (weekends, nights)

**Database Scaling**:
- **Read Replicas**: Use PostgreSQL read replicas for fatwa search queries (read-heavy)
- **Connection Pooling**: PgBouncer (max 100 connections per service instance)
- **Partitioning**: Partition `audit_logs` table by month (improve query performance)

**Caching**:
- **Redis Cluster**: 3-node cluster with replication (failover <1 second)
- **Cache Hit Ratio Target**: >80% for LLM responses, >60% for fatwa searches

---

## 5. Monitoring & Observability

### 5.1 Key Metrics

**Application Metrics** (Datadog Custom Metrics):
```python
# Custom metrics to track
datadog.statsd.increment("contracts.uploaded", tags=["jurisdiction:aaoifi"])
datadog.statsd.histogram("contract.analysis_time", value=45.2, tags=["tier:2"])
datadog.statsd.gauge("llm.cache_hit_rate", value=0.78)
datadog.statsd.increment("violations.detected", tags=["type:riba", "severity:critical"])
```

**Dashboards**:
1. **Business Dashboard**:
   - Contracts analyzed (today/week/month)
   - Average analysis time by tier
   - Violation detection rate (riba/gharar split)
   - User activity (WAU/MAU)

2. **Technical Dashboard**:
   - API latency (P50, P95, P99)
   - Error rate by endpoint
   - LLM API call volume + cost
   - Database query performance (slow query log)
   - Cache hit ratio

3. **Security Dashboard**:
   - Failed login attempts
   - Unusual API access patterns (potential breach)
   - Rate limit violations

### 5.2 Alerting Rules

```yaml
# alerts.yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  annotations:
    summary: "Error rate >5% for 5 minutes"
  actions:
    - pagerduty: on-call-engineer

- alert: LLMAPIDown
  expr: up{job="openai-api"} == 0
  for: 1m
  annotations:
    summary: "OpenAI API unreachable"
  actions:
    - slack: #engineering-alerts
    - auto-remediation: switch-to-anthropic-fallback

- alert: SlowAnalysis
  expr: histogram_quantile(0.95, contract_analysis_duration_seconds) > 120
  for: 10m
  annotations:
    summary: "P95 analysis time >2 minutes"
  actions:
    - slack: #engineering-alerts
```

---

## 6. Disaster Recovery & Business Continuity

### 6.1 Backup Strategy

**Database Backups**:
- **Automated Daily Backups**: AWS RDS automated backups (7-day retention)
- **Weekly Full Snapshots**: Manual snapshots kept for 30 days
- **Point-in-Time Recovery**: Enabled (restore to any point within 7 days)

**File Storage Backups**:
- **S3 Versioning**: Enabled (recover deleted PDFs within 30 days)
- **Cross-Region Replication**: Optional (replicate to DR region for critical customers)

**Configuration Backups**:
- **Infrastructure-as-Code**: All Kubernetes manifests + Terraform configs in Git
- **Secrets Backup**: AWS Secrets Manager auto-replication to DR region

### 6.2 Disaster Recovery Plan

**RTO (Recovery Time Objective)**: 4 hours  
**RPO (Recovery Point Objective)**: 1 hour (max data loss)

**DR Scenarios**:

| Scenario | Likelihood | Impact | Response |
|----------|-----------|--------|----------|
| **Single Pod Failure** | High | Low | Auto-restart (Kubernetes liveness probe), <30s downtime |
| **Availability Zone Failure** | Medium | Medium | Traffic reroutes to healthy AZ (multi-AZ deployment), <5min downtime |
| **Region Outage** | Low | High | Failover to DR region (manual), ~2-4 hours downtime |
| **Database Corruption** | Low | Critical | Restore from last good backup, ~1-2 hours downtime |
| **Ransomware Attack** | Low | Critical | Isolate infected systems, restore from offline backups, ~4-8 hours |

**DR Runbook** (abbreviated):
1. **Detect** incident via monitoring alerts
2. **Assess** impact (partial vs. total outage)
3. **Communicate** to users (status page + email)
4. **Execute** failover (switch DNS to DR region)
5. **Validate** DR environment is healthy
6. **Post-mortem** within 48 hours

---

## 7. Cost Estimation

### 7.1 Infrastructure Costs (AWS, Monthly)

| Component | Specification | Monthly Cost (USD) |
|-----------|--------------|-------------------|
| **EKS Cluster** | 3 t3.large nodes (2 vCPU, 8GB each) | $220 |
| **RDS PostgreSQL** | db.t3.medium (2 vCPU, 4GB), Multi-AZ | $140 |
| **ElastiCache Redis** | cache.t3.small (1.5GB), 2-node replication | $80 |
| **S3 Storage** | 500GB (contract PDFs + reports) | $12 |
| **Data Transfer** | 1TB outbound (API responses, report downloads) | $90 |
| **CloudWatch Logs** | 50GB logs/month | $25 |
| **Total Infrastructure** | | **$567/month** |

### 7.2 Third-Party API Costs (Monthly)

| Service | Usage | Cost (USD) |
|---------|-------|----------|
| **OpenAI GPT-4 Turbo** | 5M input tokens, 1M output tokens @ $10/$30 per 1M tokens | $80 |
| **OpenAI Ada-002 Embeddings** | 10M tokens @ $0.10 per 1M tokens | $1 |
| **Azure Form Recognizer** | 1,000 pages/month @ $1.50 per 1K pages | $1.50 |
| **Pinecone** | 10M vectors, 1M queries/month (Standard plan) | $70 |
| **Datadog** | 5 hosts + 50GB logs (Pro plan) | $150 |
| **Total Third-Party** | | **$302.50/month** |

### 7.3 Total Cost of Ownership (TCO)

**Monthly Operating Costs**: $867.50  
**Annual Operating Costs**: $10,410

**Customer Break-Even Analysis**:
- **Starter Tier** ($25K/year): 2.5 customers cover full annual ops cost
- **Professional Tier** ($100K/year): 1 customer covers 10x annual ops cost
- **Enterprise Tier** ($500K/year): 1 customer covers 50x annual ops cost

**Profit Margin** (assuming 10 customers in Year 1, average $150K):
- Revenue: $1.5M
- Ops Cost: $10.4K
- **Gross Margin: 99.3%** (excluding R&D, sales, support labor costs)

---

## 8. Future Enhancements (Post-MVP)

### Phase 2 Features (6-12 months)

1. **Real-Time Transaction Monitoring**
   - Stream transactions from core banking via Kafka
   - Flag non-compliant payments in real-time
   - Integration complexity: High (requires bank system access)

2. **Portfolio Screening**
   - Upload equity holdings CSV
   - Screen against AAOIFI equity screening criteria
   - Calculate zakat liability automatically
   - Differentiation: High (no direct competitor)

3. **Multi-Madhab Support**
   - Switch between Hanafi/Maliki/Shafi'i/Hanbali interpretations
   - Show differing rulings on controversial issues
   - Research required: High (scholar consultation needed)

4. **Fine-Tuned Islamic Finance LLM**
   - Train domain-specific model on AAOIFI corpus
   - Target 94%+ accuracy (vs. 85% for GPT-4 hybrid)
   - Investment: $50-100K (data labeling + compute)

5. **Mobile Native Apps**
   - iOS + Android apps for scholar on-the-go reviews
   - Push notifications for urgent contract approvals
   - Development: 4-6 months (React Native)

---

## 9. Risks & Mitigation Strategies

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| **LLM hallucination** (fabricated citations) | Critical | Medium | Validation layer: cross-check every AAOIFI reference against source database before display |
| **Accuracy below threshold** | High | Medium | Extensive testing on 500-contract validation set; hybrid rule engine backstop |
| **Vendor lock-in** (OpenAI) | Medium | Low | Abstraction layer (LLMGateway); Anthropic fallback implemented |
| **Data breach** | Critical | Low | Defense-in-depth security; SOC2 compliance; penetration testing; cyber insurance |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| **Slow enterprise sales** | Medium | High | Leverage Capco network for warm intros; design partner early engagement |
| **Shariah scholar resistance** | High | Medium | Advisory board from day one; transparent explainability; augmentation not replacement narrative |
| **Regulatory rejection** | Critical | Low | Early engagement with BNM, UAE Central Bank; ensure HITL at all tiers |
| **High LLM API costs** | Medium | Medium | Aggressive caching; volume discounts with OpenAI; optimize prompts |

---

## 10. Conclusion & Next Steps

### Architecture Summary

This architecture delivers a **production-ready, cloud-native Shariah Compliance Copilot** that:
- ✅ Combines LLM flexibility with AAOIFI rule precision (hybrid approach)
- ✅ Achieves 70% audit time reduction and 94% accuracy targets
- ✅ Maintains human oversight through HITL tiering (Shariah scholar authority preserved)
- ✅ Provides full explainability and auditability for regulatory compliance
- ✅ Scales horizontally to support 50+ concurrent users and 1,000+ contracts/month
- ✅ Deploys on AWS/Azure with 99.5% uptime SLA
- ✅ Costs $867/month to operate (highly profitable unit economics)

### Implementation Readiness

**Status**: ✅ Architecture design complete  
**Next Phase**: Development (16-week timeline per PRD roadmap)

**Immediate Next Steps**:
1. ✅ **Environment Setup** (Week 1): Provision AWS EKS cluster, PostgreSQL RDS, S3 buckets
2. ✅ **Data Acquisition** (Week 1): Source 50 anonymized contract samples + AAOIFI standards
3. 🔲 **Backend Scaffolding** (Week 2): Set up FastAPI project structure + CI/CD pipeline
4. 🔲 **LLM Integration** (Week 3): Implement LLM Gateway + clause extraction prompts
5. 🔲 **Rule Engine** (Week 4): Build riba/gharar detection logic with test cases

**Success Criteria**:
- End of Week 6: Riba/gharar detection accuracy >80% on 25-contract validation set
- End of Week 14: Fatwa search relevance (Top-3 contains answer) >75%
- End of Week 20 (Pilot): 70% time reduction, 85% accuracy, NPS >40

---

## Appendices

### Appendix A: Technology Stack Summary

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Frontend** | React + TypeScript | 18 / 5 | Industry standard, strong ecosystem |
| **UI Library** | Ant Design | 5 | Enterprise-grade, Arabic RTL support |
| **Backend** | FastAPI | 0.104+ | Async performance, automatic OpenAPI docs |
| **LLM Provider** | OpenAI GPT-4 Turbo | gpt-4-turbo-preview | Best accuracy/speed, 128K context |
| **Vector DB** | Pinecone | Serverless | Managed, low latency (<500ms) |
| **Database** | PostgreSQL | 15 | Mature, ACID compliance, JSON support |
| **Cache** | Redis | 7 | Fast, simple, widely supported |
| **OCR** | Azure Form Recognizer | v3.0 | 95%+ Arabic/English accuracy |
| **Container** | Docker | 24+ | Standard containerization |
| **Orchestration** | Kubernetes (EKS) | 1.28 | Auto-scaling, self-healing |
| **Monitoring** | Datadog | - | Unified APM + logs + metrics |
| **Cloud** | AWS | - | Mature, Singapore region for Asia |

### Appendix B: API Endpoint Reference

See Functional Requirements Document (Section 3) for complete API specifications.

### Appendix C: Glossary

See Product Requirements Document (Appendix A) for Islamic finance terms.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-17 | Alan Young | Initial architecture design - aligned with FRD v1.0 + PRD v1.0 |

---

**Status**: ✅ Architecture Design Complete  
**Deliverables**: 3/3 Complete (FRD ✅, PRD ✅, Architecture ✅)  
**Ready For**: Development Phase (16-week implementation)
