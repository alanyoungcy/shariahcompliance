# Shariah Compliance Copilot - Implementation Plan

**Project**: Shariah Compliance Automation Demo for Capco  
**Version**: 1.0  
**Date**: September 17, 2026  
**Project Manager**: Alan Young (Capco CTO Consulting)  
**Duration**: 16 weeks  
**Status**: Ready for Execution

---

## Executive Summary

This implementation plan operationalizes the Shariah Compliance Copilot design (FRD + PRD + Architecture) into a **16-week phased delivery roadmap**. The plan follows Superpowers methodology principles:

✅ **Specification-first**: All requirements documented before coding  
✅ **Phased delivery**: 4 phases with clear go/no-go gates  
✅ **Risk-driven**: High-risk components (LLM accuracy) tackled early  
✅ **Test-driven**: Acceptance criteria defined for every milestone  
✅ **Human-in-loop**: Shariah scholar validation at each phase  

**Key Milestones**:
- **Week 6**: Backend MVP complete (clause extraction + riba/gharar detection >80% accuracy)
- **Week 10**: Frontend MVP + end-to-end workflow operational
- **Week 14**: Fatwa search integrated, system feature-complete
- **Week 16**: Pilot deployment ready (polish + testing complete)

---

## Phase Breakdown

### Phase 0: Foundation (Weeks 1-2)

**Objective**: Establish development environment, tooling, and data assets before coding begins.

#### Week 1: Infrastructure & Tooling Setup

**Tasks**:
1. ✅ **AWS Environment Provisioning**
   - Create AWS account + VPC setup (public + private subnets)
   - Provision EKS cluster (3 t3.large nodes)
   - Set up RDS PostgreSQL (db.t3.medium, Multi-AZ)
   - Create S3 buckets (contracts, reports, backups)
   - Configure ElastiCache Redis (cache.t3.small, 2-node)
   - **Owner**: DevOps Engineer | **Duration**: 3 days

2. ✅ **Repository & CI/CD Setup**
   - Create GitHub repository (monorepo structure: /backend, /frontend)
   - Set up GitHub Actions workflows (lint, test, build, deploy)
   - Configure Docker registry (AWS ECR)
   - Create Kubernetes manifests (deployment, service, HPA, secrets)
   - **Owner**: DevOps Engineer | **Duration**: 2 days

3. ✅ **Third-Party Service Setup**
   - Obtain OpenAI API key (GPT-4 Turbo access)
   - Set up Azure Form Recognizer resource
   - Create Pinecone account + index (10M vectors, cosine similarity)
   - Configure Datadog APM + log forwarding
   - **Owner**: Tech Lead | **Duration**: 1 day

4. ✅ **Development Environment**
   - Set up local development environment (Docker Compose)
   - Create `.env.example` with all required environment variables
   - Document setup instructions in README.md
   - **Owner**: Tech Lead | **Duration**: 1 day

**Deliverables**:
- ✅ AWS infrastructure operational (EKS, RDS, S3, Redis)
- ✅ CI/CD pipeline functional (GitHub Actions → Docker → ECR)
- ✅ All third-party services provisioned and tested
- ✅ Local dev environment documented and reproducible

**Success Criteria**:
- [ ] Developer can clone repo, run `docker-compose up`, and see "Hello World" API response
- [ ] CI/CD deploys to EKS on `main` branch push (<10 minutes)
- [ ] All services accessible and monitored in Datadog

---

#### Week 2: Data Acquisition & Team Onboarding

**Tasks**:
1. ✅ **Contract Dataset Sourcing**
   - Source 50 anonymized Murabaha/Ijara contracts (PDF format)
   - Partner with Bank Islam Malaysia or use synthetic data generator
   - Ensure mix of compliant + non-compliant samples (for testing)
   - **Owner**: Product Manager | **Duration**: 3 days

2. ✅ **AAOIFI Standards Ingestion**
   - Download AAOIFI Shariah Standards (60+ standards)
   - Extract text from PDFs using Azure Form Recognizer
   - Create structured database of standards (title, section, full text)
   - **Owner**: Data Engineer | **Duration**: 2 days

3. ✅ **Fatwa Database Preparation**
   - Scrape public fatwa repositories (AAOIFI, Malaysia SAC, UAE)
   - Extract metadata (title, authority, date, contract type)
   - Store in PostgreSQL + generate embeddings (OpenAI Ada-002)
   - Index in Pinecone (initial 5,000 fatwas)
   - **Owner**: Data Engineer | **Duration**: 3 days

4. ✅ **Shariah Scholar Onboarding**
   - Recruit 1-2 Shariah scholars as advisors (part-time, $5K/month stipend)
   - Brief on project goals, HITL workflow, explainability requirements
   - Schedule weekly review sessions (Fridays after Jummah prayer)
   - **Owner**: Product Manager | **Duration**: 2 days

**Deliverables**:
- ✅ 50 annotated contracts (labeled with known riba/gharar violations)
- ✅ AAOIFI standards database loaded in PostgreSQL
- ✅ 5,000 fatwas indexed in Pinecone (searchable)
- ✅ Shariah advisor agreement signed

**Success Criteria**:
- [ ] Contract validation set: 25 compliant, 25 non-compliant (manually labeled by scholar)
- [ ] Fatwa search query returns Top-10 results in <3 seconds
- [ ] Scholar can articulate HITL workflow and approval criteria

---

### Phase 1: Backend MVP (Weeks 3-6)

**Objective**: Build core compliance engine (OCR → clause extraction → riba/gharar detection → report generation).

#### Week 3: Project Scaffolding & OCR Integration

**Tasks**:
1. ✅ **FastAPI Project Structure**
   ```
   backend/
   ├── src/
   │   ├── main.py                      # FastAPI app entry
   │   ├── routers/
   │   │   ├── contracts.py             # Contract endpoints
   │   │   └── health.py                # /health, /ready
   │   ├── services/
   │   │   ├── ocr_service.py           # Azure wrapper
   │   │   └── storage_service.py       # S3 uploads
   │   ├── models/
   │   │   ├── contract.py              # Pydantic models
   │   │   └── clause.py
   │   ├── db/
   │   │   ├── database.py              # SQLAlchemy setup
   │   │   ├── repositories/            # Data access
   │   │   └── migrations/              # Alembic
   │   └── config.py
   ├── tests/
   │   ├── test_ocr.py
   │   └── test_contracts.py
   └── requirements.txt
   ```
   - **Owner**: Backend Engineer 1 | **Duration**: 2 days

2. ✅ **OCR Service Implementation**
   - Integrate Azure Form Recognizer API
   - Handle PDF upload (multipart/form-data)
   - Extract text with page numbers + confidence scores
   - Unit tests: 3 sample contracts (English, Arabic, mixed)
   - **Owner**: Backend Engineer 1 | **Duration**: 3 days

3. ✅ **S3 Storage Integration**
   - Upload PDF to S3 with contract_id as key
   - Generate presigned URL for report downloads (24-hour expiry)
   - **Owner**: Backend Engineer 2 | **Duration**: 1 day

4. ✅ **Database Schema Implementation**
   - Create tables: users, contracts, clauses, violations, audit_logs, fatwas
   - Implement repositories (CRUD operations)
   - Alembic migrations
   - **Owner**: Backend Engineer 2 | **Duration**: 2 days

**Deliverables**:
- ✅ POST /api/v1/contracts/upload endpoint functional
- ✅ OCR extracts text with 90%+ accuracy (validated on 10 contracts)
- ✅ Database schema deployed to RDS
- ✅ 80%+ test coverage for Week 3 code

**Success Criteria**:
- [ ] Upload 10-page PDF → OCR completes in <30 seconds
- [ ] Extracted text matches manual review (spot-check 3 contracts)
- [ ] CI/CD pipeline passes all tests on every commit

---

#### Week 4: Clause Extraction (LLM Integration)

**Tasks**:
1. ✅ **LLM Gateway Implementation**
   - Create abstraction layer (OpenAI primary, Anthropic fallback)
   - Implement retry logic + exponential backoff
   - Add Redis caching for deterministic prompts
   - **Owner**: Backend Engineer 1 | **Duration**: 2 days

2. ✅ **Clause Extraction Prompt Engineering**
   - Design few-shot prompt template (15 clause types)
   - Test on 10 sample contracts, iterate on accuracy
   - Target: 85%+ clause extraction accuracy
   - Implement confidence scoring (0.0-1.0)
   - **Owner**: Backend Engineer 1 + ML Engineer | **Duration**: 3 days

3. ✅ **Clause Extraction Service**
   - Parse LLM JSON response (handle malformed JSON gracefully)
   - Store clauses in PostgreSQL with page references
   - Link clauses to source contract
   - **Owner**: Backend Engineer 1 | **Duration**: 2 days

**Deliverables**:
- ✅ Clause extraction achieves 85%+ accuracy on 25-contract validation set
- ✅ Extracted clauses stored in database with confidence scores
- ✅ LLM response caching reduces API costs by 50%

**Success Criteria**:
- [ ] Run clause extraction on 25 contracts → Scholar validates accuracy ≥85%
- [ ] Cache hit rate >60% on second run of same contracts
- [ ] Average extraction time <15 seconds per contract

---

#### Week 5: Riba & Gharar Detection (Hybrid Engine)

**Tasks**:
1. ✅ **Rule Engine Implementation**
   - Code 5 riba patterns (regex + keyword matching)
   - Code 4 gharar patterns
   - Unit tests: 20 test cases per pattern (10 positive, 10 negative)
   - **Owner**: Backend Engineer 2 | **Duration**: 3 days

2. ✅ **LLM Semantic Analysis**
   - Design riba/gharar analysis prompts (separate prompts)
   - Implement hybrid logic: rule engine → LLM fallback for ambiguous cases
   - Cross-validate with AAOIFI standards (citation matching)
   - **Owner**: ML Engineer | **Duration**: 3 days

3. ✅ **Violation Storage & Reporting**
   - Store violations in database (linked to clauses)
   - Calculate severity scores (critical/high/medium/low)
   - Generate violation summary (count by type/severity)
   - **Owner**: Backend Engineer 2 | **Duration**: 1 day

**Deliverables**:
- ✅ Riba detection: 90%+ recall, 85%+ precision on validation set
- ✅ Gharar detection: 85%+ recall, 80%+ precision
- ✅ Hybrid engine successfully handles 100% of test cases (no crashes)

**Success Criteria**:
- [ ] False positive rate <15% (validated by scholar on 25 contracts)
- [ ] False negative rate <10% (catch 90% of actual violations)
- [ ] Scholar approves detection logic and AAOIFI citation accuracy

---

#### Week 6: Report Generation & HITL Tier Assignment

**Tasks**:
1. ✅ **HITL Tier Classifier**
   - Implement tier assignment logic (contract value, violation severity, novelty score)
   - Unit tests: 30 scenarios (10 per tier)
   - **Owner**: Backend Engineer 1 | **Duration**: 2 days

2. ✅ **Report Generation (PDF/Word)**
   - Design Jinja2 templates (executive summary, detailed findings, compliance checklist)
   - Implement PDF export (WeasyPrint or Pandoc)
   - Implement Word export (python-docx)
   - Include explainability sections (why AI flagged each issue)
   - **Owner**: Backend Engineer 2 | **Duration**: 3 days

3. ✅ **GET /api/v1/contracts/{id}/analysis Endpoint**
   - Return full analysis results (clauses, violations, tier, report URL)
   - Implement caching (24-hour TTL)
   - **Owner**: Backend Engineer 1 | **Duration**: 1 day

4. ✅ **End-to-End Testing**
   - Run full pipeline on 25-contract validation set
   - Measure accuracy, latency, and error rate
   - **Owner**: QA Engineer + Shariah Scholar | **Duration**: 2 days

**Deliverables**:
- ✅ Complete backend MVP operational (upload → OCR → clause → riba/gharar → report)
- ✅ 85%+ accuracy on 25-contract validation set (scholar-verified)
- ✅ Average analysis time <60 seconds per 10-page contract
- ✅ Generated reports meet regulatory audit requirements (scholar approval)

**Success Criteria** (Go/No-Go Gate):
- [ ] **Accuracy**: Riba/gharar detection ≥85% (scholar validation)
- [ ] **Latency**: <60 seconds for typical contract
- [ ] **Quality**: Scholar approves 20/25 generated reports as audit-ready
- **Decision**: If criteria met → proceed to Phase 2. If not → iterate on prompts/rules (1-2 week delay)

---

### Phase 2: Frontend MVP (Weeks 7-10)

**Objective**: Build user interface for contract upload, dashboard, and HITL workflow.

#### Week 7: Frontend Scaffolding & Contract Upload

**Tasks**:
1. ✅ **React Project Setup**
   ```
   frontend/
   ├── src/
   │   ├── components/
   │   │   ├── ContractUpload/
   │   │   │   ├── FileDropzone.tsx
   │   │   │   └── UploadProgress.tsx
   │   │   └── Shared/
   │   │       ├── Header.tsx
   │   │       └── Sidebar.tsx
   │   ├── pages/
   │   │   ├── Dashboard.tsx
   │   │   └── ContractReview.tsx
   │   ├── hooks/
   │   │   └── useContractAnalysis.ts
   │   ├── utils/
   │   │   └── apiClient.ts
   │   └── App.tsx
   ├── public/
   └── package.json
   ```
   - **Owner**: Frontend Engineer 1 | **Duration**: 1 day

2. ✅ **File Upload Component**
   - Drag-drop interface (React Dropzone)
   - File validation (PDF only, max 50MB)
   - Upload progress bar
   - Jurisdiction selector (AAOIFI/Malaysia/Hybrid)
   - **Owner**: Frontend Engineer 1 | **Duration**: 2 days

3. ✅ **API Client Setup**
   - Axios instance with auth interceptor
   - React Query for caching + retry logic
   - Error handling (toast notifications)
   - **Owner**: Frontend Engineer 2 | **Duration**: 2 days

**Deliverables**:
- ✅ Contract upload page functional
- ✅ User can drag-drop PDF → upload → see "processing" status
- ✅ API integration tested on dev environment

**Success Criteria**:
- [ ] Upload 3 contracts in a row → no crashes or errors
- [ ] Progress bar accurately reflects upload status
- [ ] Errors (e.g., file too large) display clear user-facing messages

---

#### Week 8-9: Analysis Dashboard & Violation Display

**Tasks**:
1. ✅ **Analysis Summary Card**
   - Display high-level metrics (clauses extracted, violations found, tier)
   - Status indicators (processing/completed/failed)
   - **Owner**: Frontend Engineer 1 | **Duration**: 2 days

2. ✅ **Violation List Component**
   - Display violations grouped by severity (Critical > High > Medium > Low)
   - Each violation shows: type, clause excerpt, AAOIFI citation, suggested fix
   - Expandable detail view (full clause text, page number, confidence score)
   - **Owner**: Frontend Engineer 1 | **Duration**: 3 days

3. ✅ **Extracted Clauses Table**
   - Searchable, sortable table (15 clause types)
   - Filter by confidence score (<70% flagged for review)
   - **Owner**: Frontend Engineer 2 | **Duration**: 2 days

4. ✅ **Report Export Buttons**
   - Download PDF report (presigned S3 URL)
   - Download Word report
   - Email report to scholar (future enhancement)
   - **Owner**: Frontend Engineer 2 | **Duration**: 1 day

5. ✅ **Responsive Design & Arabic RTL**
   - Test on tablet (iPad Pro)
   - Implement RTL layout for Arabic UI
   - **Owner**: Frontend Engineer 1 + Designer | **Duration**: 2 days

**Deliverables**:
- ✅ Full analysis dashboard operational
- ✅ User can upload contract → see analysis results → download report
- ✅ UI tested on Chrome, Safari, Edge (desktop + tablet)

**Success Criteria**:
- [ ] 5 test users (non-technical) can complete full workflow without guidance
- [ ] Arabic RTL layout displays correctly
- [ ] Page load time <2 seconds on 4G connection

---

#### Week 10: HITL Workflow & User Management

**Tasks**:
1. ✅ **Authentication (OAuth2 + JWT)**
   - Implement login page
   - OAuth2 flow (email/password for MVP, SSO in Phase 3)
   - JWT token management (access + refresh tokens)
   - **Owner**: Backend Engineer 2 + Frontend Engineer 2 | **Duration**: 3 days

2. ✅ **Role-Based Access Control**
   - Implement 4 roles (Compliance Officer, Shariah Scholar, Product Manager, Auditor)
   - Permission checks on API endpoints
   - Hide/show UI elements based on role
   - **Owner**: Backend Engineer 2 | **Duration**: 2 days

3. ✅ **HITL Approval Workflow**
   - Scholar dashboard: "Contracts Awaiting Review" list
   - Approve/Reject/Request Revision buttons
   - Approval notes textarea (required for rejection)
   - Email notification on status change
   - **Owner**: Frontend Engineer 1 + Backend Engineer 1 | **Duration**: 3 days

**Deliverables**:
- ✅ Authentication functional (login/logout/token refresh)
- ✅ RBAC enforced on all endpoints
- ✅ Scholar can approve/reject contracts from dashboard

**Success Criteria**:
- [ ] Compliance Officer can upload contract but NOT approve
- [ ] Shariah Scholar can approve/reject with audit trail logged
- [ ] Unauthorized API requests return 403 Forbidden

---

### Phase 3: Fatwa Search Integration (Weeks 11-14)

**Objective**: Add semantic fatwa search + contextual recommendations during contract review.

#### Week 11-12: Fatwa Search Backend

**Tasks**:
1. ✅ **Fatwa Search API**
   - Implement POST /api/v1/fatwas/search endpoint
   - Query embedding (OpenAI Ada-002)
   - Vector search (Pinecone)
   - Reranking (cross-encoder BERT) - optional for MVP
   - **Owner**: Backend Engineer 1 + ML Engineer | **Duration**: 3 days

2. ✅ **Fatwa Summarization**
   - Implement POST /api/v1/fatwas/{id}/summarize endpoint
   - GPT-4 summarization prompt (executive summary, key ruling, conditions)
   - Cache summaries (Redis, 24-hour TTL)
   - **Owner**: ML Engineer | **Duration**: 2 days

3. ✅ **Contextual Recommendations**
   - Implement POST /api/v1/fatwas/recommend endpoint
   - Trigger on ambiguous clause detection (confidence <70%)
   - Return top-3 relevant fatwas with rationale
   - **Owner**: ML Engineer | **Duration**: 2 days

4. ✅ **Performance Optimization**
   - Tune Pinecone index (experiment with dimensions, similarity metric)
   - Implement hybrid search (vector + keyword BM25)
   - Target <3 seconds for search query
   - **Owner**: ML Engineer | **Duration**: 2 days

**Deliverables**:
- ✅ Fatwa search returns Top-10 results in <3 seconds
- ✅ Search relevance: Top-3 contains answer ≥75% of time (validated on 50 test queries)
- ✅ Summarization generates accurate 3-sentence summaries (spot-checked by scholar)

**Success Criteria**:
- [ ] Scholar validates search relevance on 50 queries: ≥75% Top-3 accuracy
- [ ] Latency P95 <3 seconds
- [ ] No crashes or timeouts on 100 consecutive queries

---

#### Week 13-14: Fatwa Search Frontend

**Tasks**:
1. ✅ **Search Interface**
   - Search bar with autocomplete (suggest common queries)
   - Filter sidebar (authority, date range, contract type)
   - Result list (card layout with title, excerpt, relevance score)
   - **Owner**: Frontend Engineer 1 | **Duration**: 3 days

2. ✅ **Fatwa Detail View**
   - Side panel with full text (collapsible sections)
   - Related fatwas (similar rulings)
   - Citation button (insert into contract report)
   - **Owner**: Frontend Engineer 1 | **Duration**: 2 days

3. ✅ **Contextual Recommendations in Dashboard**
   - When reviewing contract, sidebar shows "3 Relevant Fatwas"
   - Click to expand summary
   - One-click insert citation into report
   - **Owner**: Frontend Engineer 2 | **Duration**: 2 days

4. ✅ **Bilingual Search (English + Arabic)**
   - Detect query language (Arabic vs. English)
   - Display results in query language
   - Toggle full text between Arabic/English if both available
   - **Owner**: Frontend Engineer 2 | **Duration**: 2 days

**Deliverables**:
- ✅ Full fatwa search interface operational
- ✅ User can search, view details, cite in reports seamlessly
- ✅ Contextual recommendations display during contract review

**Success Criteria**:
- [ ] User can find answer to "Can we charge processing fees in Murabaha?" in <60 seconds
- [ ] 5 test users rate search experience ≥4/5 stars
- [ ] Arabic search returns relevant Arabic fatwas (spot-checked)

---

### Phase 4: Polish & Testing (Weeks 15-16)

**Objective**: Final QA, performance optimization, security hardening, pilot deployment readiness.

#### Week 15: End-to-End Testing & Bug Fixing

**Tasks**:
1. ✅ **Comprehensive Testing**
   - Run 50-contract validation set through full system
   - Measure accuracy, latency, error rate
   - User acceptance testing (5 Shariah officers + 2 scholars)
   - **Owner**: QA Engineer + Product Manager | **Duration**: 3 days

2. ✅ **Bug Triage & Fixing**
   - Prioritize P0 (blocking) and P1 (high-impact) bugs
   - Fix critical issues (crashes, data loss, security vulnerabilities)
   - Defer P2 (nice-to-have) bugs to post-launch backlog
   - **Owner**: Full Team | **Duration**: 2 days

3. ✅ **Performance Optimization**
   - Optimize slow database queries (add indexes)
   - Tune LLM prompts to reduce token usage (cost optimization)
   - Implement aggressive caching for frequent queries
   - **Owner**: Backend Engineers + ML Engineer | **Duration**: 2 days

**Deliverables**:
- ✅ All P0 and P1 bugs fixed (zero known critical issues)
- ✅ System performance meets targets (60s analysis, 3s search)
- ✅ 50-contract validation achieves 85%+ accuracy

**Success Criteria**:
- [ ] Zero crashes during 50-contract test
- [ ] User satisfaction score ≥4/5 (exit survey)
- [ ] Scholar approves system for pilot deployment

---

#### Week 16: Security Audit & Deployment

**Tasks**:
1. ✅ **Security Hardening**
   - Penetration testing (hire external firm or use OWASP ZAP)
   - Fix identified vulnerabilities (SQL injection, XSS, CSRF)
   - Implement rate limiting (100 req/min/user)
   - Enable HTTPS (TLS 1.3) with valid SSL certificate
   - **Owner**: DevOps Engineer + Security Consultant | **Duration**: 3 days

2. ✅ **Documentation**
   - User guide (contract upload → approval workflow)
   - Admin guide (user management, fatwa ingestion)
   - API documentation (OpenAPI/Swagger)
   - Troubleshooting guide (common errors + resolutions)
   - **Owner**: Technical Writer + Product Manager | **Duration**: 2 days

3. ✅ **Pilot Deployment**
   - Deploy to production environment (AWS EKS)
   - Set up monitoring alerts (Datadog)
   - Configure backups (daily RDS snapshots)
   - Train 5-10 pilot users (Shariah officers + scholars)
   - **Owner**: DevOps Engineer + Product Manager | **Duration**: 2 days

4. ✅ **Launch Checklist**
   - [ ] All P0 bugs fixed
   - [ ] Security audit passed (no critical vulnerabilities)
   - [ ] Documentation complete
   - [ ] Monitoring & alerting operational
   - [ ] Pilot users trained
   - [ ] Shariah advisory board approval documented
   - **Owner**: Product Manager | **Duration**: 1 day

**Deliverables**:
- ✅ Production system live and stable
- ✅ 5-10 pilot users onboarded and actively using system
- ✅ All documentation published (internal wiki + user-facing)

**Success Criteria** (Final Go/No-Go Gate):
- [ ] Zero critical security vulnerabilities
- [ ] System uptime ≥99% during Week 16
- [ ] Pilot users rate experience ≥4/5 stars
- [ ] Scholar provides written approval for production use
- **Decision**: If criteria met → launch pilot program. If not → delay 1-2 weeks for fixes.

---

## Resource Allocation

### Team Structure

| Role | FTE | Duration | Responsibilities |
|------|-----|----------|------------------|
| **Tech Lead** | 1.0 | Weeks 1-16 | Architecture decisions, code reviews, unblock engineers |
| **Backend Engineer 1** | 1.0 | Weeks 3-16 | Contract analysis service, LLM integration |
| **Backend Engineer 2** | 1.0 | Weeks 3-16 | Database, rule engine, user management |
| **ML Engineer** | 1.0 | Weeks 4-14 | Prompt engineering, vector search, model optimization |
| **Frontend Engineer 1** | 1.0 | Weeks 7-16 | Dashboard, contract review UI |
| **Frontend Engineer 2** | 1.0 | Weeks 7-16 | Authentication, fatwa search UI |
| **DevOps Engineer** | 0.5 | Weeks 1-16 | Infrastructure, CI/CD, monitoring, security |
| **QA Engineer** | 0.5 | Weeks 3-16 | Test planning, UAT, bug verification |
| **Product Manager** | 0.5 | Weeks 1-16 | Requirements, stakeholder management, scholar coordination |
| **Designer (UI/UX)** | 0.3 | Weeks 7-10 | Mockups, user flows, Arabic RTL design |
| **Technical Writer** | 0.2 | Weeks 15-16 | Documentation |
| **Shariah Scholar (Advisor)** | 0.2 | Weeks 2-16 | Validation, fatwa review, approval authority |
| **Total** | **6.7 FTE** | | |

### Budget Estimate

**Labor Costs** (16 weeks):

| Role | Rate ($/hour) | Hours | Total |
|------|--------------|-------|-------|
| Tech Lead | $150 | 640 (16 weeks × 40h) | $96,000 |
| Backend Engineers (2) | $120 | 1,120 (14 weeks × 40h × 2) | $134,400 |
| ML Engineer | $130 | 440 (11 weeks × 40h) | $57,200 |
| Frontend Engineers (2) | $110 | 800 (10 weeks × 40h × 2) | $88,000 |
| DevOps Engineer | $100 | 320 (16 weeks × 20h) | $32,000 |
| QA Engineer | $80 | 280 (14 weeks × 20h) | $22,400 |
| Product Manager | $120 | 320 (16 weeks × 20h) | $38,400 |
| Designer | $100 | 120 (4 weeks × 30h) | $12,000 |
| Technical Writer | $80 | 64 (2 weeks × 32h) | $5,120 |
| Shariah Scholar | $200 | 128 (14 weeks × 9h) | $25,600 |
| **Total Labor** | | | **$511,120** |

**Non-Labor Costs** (16 weeks):

| Category | Monthly Cost | Total (4 months) |
|----------|-------------|------------------|
| AWS Infrastructure | $567 | $2,268 |
| Third-Party APIs (OpenAI, Azure, Pinecone, Datadog) | $303 | $1,212 |
| Security Audit | - | $5,000 (one-time) |
| Contingency (10%) | - | $51,848 |
| **Total Non-Labor** | | **$60,328** |

**Total Project Cost**: $571,448 (~$571K)

---

## Risk Management

### High-Priority Risks

| Risk | Mitigation | Contingency Plan |
|------|-----------|------------------|
| **LLM accuracy below 85%** | Extensive testing in Week 4-6; iterate on prompts | Add 2-week buffer; consider rule-engine-only fallback |
| **Shariah scholar availability** | Schedule weekly sessions in advance; async review via email | Recruit backup scholar; pay premium for fast turnaround |
| **Contract dataset insufficient** | Partner with Bank Islam Malaysia early (Week 2) | Use synthetic data generator (GPT-4 generates mock contracts) |
| **Third-party API downtime** (OpenAI, Azure) | Implement fallback providers (Anthropic, AWS Textract) | Design graceful degradation (e.g., skip LLM, use rules only) |
| **Scope creep** (feature requests mid-project) | Firm MVP scope; defer non-critical features to Phase 2 | Product Manager authority to reject out-of-scope requests |

---

## Quality Gates & Decision Points

### Week 6 Go/No-Go Gate (Backend MVP)
**Criteria**:
- [ ] Riba/gharar detection accuracy ≥85%
- [ ] Analysis latency <60 seconds
- [ ] Scholar approves 80% of generated reports

**Decision**:
- ✅ **Go**: Proceed to Phase 2 (Frontend)
- ❌ **No-Go**: Iterate on LLM prompts/rule engine (1-2 week delay)

### Week 14 Go/No-Go Gate (Fatwa Search)
**Criteria**:
- [ ] Search relevance (Top-3 accuracy) ≥75%
- [ ] Latency <3 seconds
- [ ] Scholar validates 40/50 test queries as relevant

**Decision**:
- ✅ **Go**: Proceed to Phase 4 (Polish & Deploy)
- ❌ **No-Go**: Add more fatwas to database, tune search algorithm (1 week delay)

### Week 16 Launch Gate (Pilot Deployment)
**Criteria**:
- [ ] Zero critical security vulnerabilities
- [ ] Pilot user satisfaction ≥4/5
- [ ] Scholar written approval obtained

**Decision**:
- ✅ **Go**: Launch pilot program with 1-2 institutions
- ❌ **No-Go**: Fix critical issues (1-2 week delay)

---

## Post-Launch Plan (Weeks 17-20)

### Week 17-18: Pilot Observation
- Monitor pilot user activity (Datadog analytics)
- Collect feedback (weekly surveys)
- Fix bugs discovered in production (priority: P0 > P1 > P2)
- Scholar spot-checks 10% of approved contracts (quality assurance)

### Week 19: Pilot Review & Iteration
- Conduct retrospective with pilot users
- Measure KPIs: audit time reduction, accuracy, NPS
- Implement high-priority feature requests (e.g., bulk upload, mobile view)
- Prepare case study (before/after metrics, testimonials)

### Week 20: Scale-Up Planning
- Recruit 5-10 additional customers (target: Enterprise tier)
- Develop sales collateral (demo video, ROI calculator, white paper)
- Plan Phase 2 features (real-time monitoring, portfolio screening, fine-tuned LLM)
- Secure Series A funding if needed (target: $3-5M for 18-month runway)

---

## Success Metrics Summary

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Backend Accuracy** | ≥85% | Scholar validation on 50-contract test set |
| **Analysis Latency** | <60 seconds | P95 latency (10-page contract) |
| **Search Relevance** | ≥75% | Top-3 contains answer (50 test queries) |
| **User Satisfaction** | ≥4/5 stars | Exit survey (pilot users) |
| **System Uptime** | ≥99% | Datadog monitoring (Week 16+) |
| **Pilot Adoption** | 5-10 active users | Contract uploads per week >10 |
| **Audit Time Reduction** | ≥70% | Before/after comparison (pilot institution) |

---

## Conclusion

This implementation plan provides a **clear, actionable roadmap** from requirements (Weeks 1-2) through MVP development (Weeks 3-14) to production deployment (Weeks 15-16). The phased approach with explicit go/no-go gates ensures high-risk components (LLM accuracy) are validated early, minimizing wasted effort.

**Key Success Factors**:
1. ✅ **Shariah scholar involvement from Week 2** (validation authority)
2. ✅ **Test-driven development** (acceptance criteria per milestone)
3. ✅ **Realistic timeline** (16 weeks for POC, not production-scale system)
4. ✅ **Focus on MVP** (defer nice-to-have features to Phase 2)
5. ✅ **Proven architecture** (based on Bank Islam Malaysia, Prudential BSN case studies)

**Next Step**: Secure stakeholder approval + allocate resources → Begin Week 1 execution.

---

## Appendix: Sprint Breakdown (Agile 2-Week Sprints)

| Sprint | Weeks | Theme | Key Deliverables |
|--------|-------|-------|------------------|
| **Sprint 0** | 1-2 | Foundation | Infrastructure, data acquisition, team onboarding |
| **Sprint 1** | 3-4 | Core Engine Part 1 | OCR, clause extraction, LLM gateway |
| **Sprint 2** | 5-6 | Core Engine Part 2 | Riba/gharar detection, reports, HITL tier |
| **Sprint 3** | 7-8 | Frontend Part 1 | Upload UI, dashboard summary |
| **Sprint 4** | 9-10 | Frontend Part 2 | Violation display, HITL workflow, auth |
| **Sprint 5** | 11-12 | Fatwa Search Backend | Vector search, summarization, recommendations |
| **Sprint 6** | 13-14 | Fatwa Search Frontend | Search UI, detail view, citations |
| **Sprint 7** | 15-16 | Launch Readiness | Testing, security, documentation, deployment |

**Daily Standups**: 15-minute sync (blocker resolution)  
**Sprint Reviews**: Friday afternoon (demo progress to stakeholders)  
**Sprint Retrospectives**: Friday end-of-day (what went well, what to improve)

---

**Status**: ✅ Implementation Plan Complete  
**Deliverables**: 4/4 Complete (FRD ✅, PRD ✅, Architecture ✅, Implementation Plan ✅)  
**Ready For**: Stakeholder Approval → Resource Allocation → Week 1 Kickoff
