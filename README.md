# Shariah Compliance Copilot

**Capco Islamic Finance AI Demo**  
**LLM-Powered Shariah Compliance Automation**

---

## Overview

This project demonstrates AI-powered Shariah compliance automation for Islamic financial institutions. The system uses GPT-4 and rule-based engines to analyze Islamic finance contracts, detect riba (interest) and gharar (excessive uncertainty) violations, and generate audit-ready reports.

**Key Features**:
- ✅ Automated contract analysis (OCR → clause extraction → violation detection → reporting)
- ✅ Hybrid intelligence (GPT-4 semantic analysis + AAOIFI rule engine)
- ✅ Synthetic contract generator (100+ test contracts with known labels)
- ✅ Explainable AI (every decision cites AAOIFI Shariah standards)
- ✅ Demo-ready UI (upload → analyze → report in <60 seconds)

**Target Accuracy**: 85%+ violation detection, <15% false positive rate  
**Target Latency**: <60 seconds for 10-page contract  
**Use Case**: Proof-of-concept for Islamic banks and takaful operators

---

## Project Structure

```
shariah/
├── docs/                          # Complete design documentation
│   ├── 01-FUNCTIONAL-REQUIREMENTS.md
│   ├── 02-PRODUCT-REQUIREMENTS.md
│   ├── 03-SYSTEM-ARCHITECTURE.md
│   ├── 04-IMPLEMENTATION-PLAN.md
│   ├── TEST-DATA-EXAMPLES.md
│   └── README.md
├── src/                           # Source code
│   ├── backend/                   # FastAPI backend
│   ├── frontend/                  # React frontend
│   └── generators/                # Contract generator
├── tests/                         # Test suite
├── data/                          # Generated contracts + AAOIFI standards
├── scripts/                       # Setup and demo scripts
└── DEMO-IMPLEMENTATION-PLAN.md    # Implementation roadmap
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key (GPT-4 access)

### 1. Clone and Setup

```bash
cd /Users/alanyoung/Orico/code/capco/islamic-ai/shariah

# Install Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Node dependencies
cd src/frontend
npm install
cd ../..

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Generate Test Contracts

```bash
# Generate one good/bad pair from each standalone PDF in template/
python -m src.generators.contract_generator

# Generate more repeatable pairs for selected structures
python -m src.generators.contract_generator --types murabaha,salam,ijarah --pairs 5 --seed 42

# Output: data/generated_contracts/
#   ├── good/             (no issue intentionally seeded)
#   ├── bad/              (explicit demo review issues)
#   ├── manifest.json     (machine-readable labels)
#   └── ANSWER-KEY.md     (human-readable labels)
```

The files are synthetic demonstrations, not legal advice or Shariah rulings. A good label means
the generator did not intentionally seed an issue; it does not constitute approval of the source wording.

### 3. Run Backend

```bash
# Start FastAPI server
uvicorn src.backend.main:app --reload --port 8000

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Run Frontend

```bash
# Start React dev server
cd src/frontend
npm run dev

# UI will be available at http://localhost:5173
```

### 5. Run Demo

```bash
# Full demo launcher (backend + frontend + sample contracts)
./scripts/run_demo.sh
```

---

## Start and Stop the Docker Demo

After copying `.env.example` to `.env` and adding the copilot provider values, start every service with one command:

```bash
./scripts/start.sh
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173). Stop the frontend, API, and database together with:

```bash
./scripts/stop.sh
```

The stop script preserves the local database volume. To reset all local data deliberately, run `docker compose down -v`.

---

## Demo Scenarios

### Scenario 1: Compliant Contract ✅
**File**: `data/generated_contracts/compliant/MRB-20270917-XXXX.pdf`

1. Upload compliant Murabaha contract
2. System analyzes in ~15 seconds
3. Results: 0 violations, Tier 1 auto-approve
4. Download audit-ready PDF report

**Expected Output**:
- 15 clauses extracted (profit calculation, payment schedule, ownership transfer, etc.)
- 0 riba violations
- 0 gharar violations
- Confidence: 98%
- Recommendation: Auto-approve with scholar spot-check

### Scenario 2: Non-Compliant Contract ❌
**File**: `data/generated_contracts/non_compliant/BAD-20270917-XXXX.pdf`

1. Upload contract with 6 riba violations
2. System detects all violations
3. Results: 6 critical violations, Tier 3 reject
4. Each violation shows: evidence + AAOIFI citation + suggested fix

**Expected Output**:
- Riba violations detected:
  - Explicit interest rate (8.5% annual)
  - Variable rate (EIBOR + 3%)
  - Time-based late penalty (2% per month)
  - Compounding penalties
  - Early repayment penalty (3%)
  - No asset backing (cash loan)
- Recommendation: Reject (not Shariah-compliant)

### Scenario 3: Batch Processing
```bash
python scripts/batch_analyze.py --input data/generated_contracts/ --output results/

# Analyzes all 100 contracts
# Generates accuracy report: precision, recall, F1 score
```

---

## API Endpoints

**POST /api/v1/contracts/analyze**
- Upload PDF contract
- Returns: contract_id, analysis summary, violations

**GET /api/v1/contracts/{contract_id}/report**
- Download PDF report

**GET /api/v1/contracts/{contract_id}/analysis**
- Get full analysis JSON (clauses, violations, tier, confidence)

**POST /api/v1/contracts/batch**
- Batch analyze multiple contracts
- Returns: array of analyses

---

## Key Technologies

**Backend**:
- FastAPI (async Python API)
- OpenAI GPT-4 Turbo (clause extraction, semantic analysis)
- PyPDF2 (PDF parsing)
- ReportLab (PDF report generation)

**Frontend**:
- React 18 + TypeScript
- Ant Design (UI components)
- Axios (API client)

**Contract Generator**:
- Faker (synthetic data)
- ReportLab (PDF generation)
- Configurable violation patterns

---

## Architecture Highlights

**Hybrid Intelligence**:
- **Rule Engine**: Regex + keyword patterns for explicit violations (95% precision)
- **LLM Semantic Analysis**: GPT-4 for ambiguous cases (90% recall)
- **Confidence Scoring**: Combined rule + LLM confidence (0-100%)

**HITL (Human-in-the-Loop)**:
- **Tier 1**: Auto-approve (routine, 0 violations)
- **Tier 2**: Scholar approval required (minor ambiguities)
- **Tier 3**: Immediate rejection (critical violations)

**Explainability**:
- Every violation cites AAOIFI Shariah Standard
- Suggested alternatives provided
- Confidence scores for transparency

---

## Project Timeline

**Week 1**: Contract generator + backend core (Days 1-7)  
**Week 2**: Frontend UI + integration (Days 8-14)  
**Week 3**: Testing + polish + Capco presentation (Days 15-21)

**Current Status**: Design complete, ready for implementation

---

## Documentation

- **[Functional Requirements](docs/01-FUNCTIONAL-REQUIREMENTS.md)**: 35+ requirements, use cases, success criteria
- **[Product Requirements](docs/02-PRODUCT-REQUIREMENTS.md)**: Market analysis, personas, business model
- **[System Architecture](docs/03-SYSTEM-ARCHITECTURE.md)**: 6-layer architecture, tech stack, security
- **[Implementation Plan](docs/04-IMPLEMENTATION-PLAN.md)**: 16-week roadmap for production system
- **[Test Data Examples](docs/TEST-DATA-EXAMPLES.md)**: Sample compliant/non-compliant contracts
- **[Demo Implementation Plan](DEMO-IMPLEMENTATION-PLAN.md)**: 2-3 week demo development plan

---

## Success Metrics

**Accuracy** (Week 2 validation):
- Riba detection: ≥90% recall, ≥85% precision
- Gharar detection: ≥85% recall, ≥80% precision
- False positive rate: <15%

**Performance** (Week 2 testing):
- Analysis latency: <60 seconds for 10-page contract
- Batch throughput: >10 contracts/minute

**User Validation** (Week 3 testing):
- Shariah scholar approval: ≥80% of reports meet audit standards
- User satisfaction: ≥4/5 stars (5-10 test users)

---

## Next Steps

1. ✅ Design documentation complete (4 docs, 150KB)
2. ✅ Demo implementation plan finalized
3. 🔲 **Day 1-2**: Implement contract generator
4. 🔲 **Day 3-7**: Build backend analysis engine
5. 🔲 **Day 8-14**: Build frontend demo UI
6. 🔲 **Day 15-21**: Integration, testing, Capco presentation

**Target Demo Date**: End of Week 2  
**Target Presentation**: Week 3

---

## Contact

**Project Lead**: Alan Young (Capco CTO Consulting)  
**Purpose**: Proof-of-concept for Islamic finance compliance automation  
**Stakeholder**: Capco clients (Islamic banks, takaful operators)

---

## License

Proprietary - Capco Internal Demo  
© 2027 Capco. All rights reserved.

---

**Status**: Design Complete | Implementation Ready | Target: 2-3 Week Demo
