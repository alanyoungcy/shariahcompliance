# Shariah Compliance Copilot - Demo Implementation Plan

**Project**: Capco Islamic Finance AI Demo  
**Location**: `/Users/alanyoung/Orico/code/capco/islamic-ai/shariah`  
**Timeline**: 2-3 weeks for functional demo  
**Goal**: Working prototype demonstrating LLM-powered Shariah compliance automation

---

## Project Structure

```
shariah/
├── docs/                          # Design documentation
│   ├── 01-FUNCTIONAL-REQUIREMENTS.md
│   ├── 02-PRODUCT-REQUIREMENTS.md
│   ├── 03-SYSTEM-ARCHITECTURE.md
│   ├── 04-IMPLEMENTATION-PLAN.md
│   ├── TEST-DATA-EXAMPLES.md
│   └── README.md
├── src/                           # Source code
│   ├── backend/                   # FastAPI backend
│   │   ├── api/                   # API routes
│   │   ├── services/              # Business logic
│   │   ├── models/                # Data models
│   │   └── config.py              # Configuration
│   ├── frontend/                  # React frontend
│   │   ├── components/            # UI components
│   │   ├── pages/                 # Page components
│   │   └── utils/                 # Utilities
│   └── generators/                # Contract generators
│       ├── contract_generator.py  # Main generator
│       ├── templates/             # Contract templates
│       └── scenarios.py           # Test scenarios
├── tests/                         # Test suite
│   ├── test_contract_generator.py
│   ├── test_riba_detection.py
│   └── test_clause_extraction.py
├── data/                          # Data assets
│   ├── aaoifi_standards/          # AAOIFI rules
│   ├── generated_contracts/       # Generated test data
│   └── fatwa_database/            # Fatwa samples
├── scripts/                       # Utility scripts
│   ├── setup.sh                   # Environment setup
│   ├── generate_contracts.py     # Batch contract generation
│   └── run_demo.sh               # Demo launcher
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── package.json                   # Node dependencies
└── README.md                      # Project overview
```

---

## Phase 1: Core Contract Generator (Days 1-3)

**Objective**: Build synthetic contract generator for testing without real customer data

### Features

**1. Compliant Contract Generator**
- Generate valid Murabaha contracts (property, auto, business financing)
- Randomize: customer names, amounts, terms, dates
- Follow AAOIFI SS 8 structure exactly
- Output PDF and JSON formats

**2. Non-Compliant Contract Generator**
- Generate contracts with specific violation types:
  - Explicit riba (interest rates)
  - Time-based penalties
  - Variable rates
  - No asset backing (gharar)
  - Compounding penalties
  - Early repayment penalties
- Control violation severity (1-10 violations per contract)

**3. Batch Generation**
- Generate 100+ test contracts with known labels
- 50% compliant, 50% non-compliant
- Varying contract types: Murabaha, Ijara, Musharaka
- Export metadata: contract_id, violations[], compliance_status

### Implementation

```python
# src/generators/contract_generator.py

from typing import Literal, List, Dict
from datetime import datetime, timedelta
import random
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

fake = Faker(['ar_AE', 'en_US'])  # Arabic and English

class ContractGenerator:
    """Generate synthetic Islamic finance contracts for testing"""
    
    def __init__(self):
        self.contract_types = ['murabaha', 'ijara', 'musharaka']
        self.jurisdictions = ['aaoifi', 'malaysia', 'hybrid']
    
    def generate_compliant_murabaha(
        self,
        customer_name: str = None,
        asset_type: Literal['property', 'vehicle', 'equipment'] = 'property',
        amount: int = None,
        term_months: int = 120
    ) -> Dict:
        """Generate AAOIFI-compliant Murabaha contract"""
        
        # Randomize if not provided
        customer_name = customer_name or fake.name()
        amount = amount or random.randint(500000, 5000000)
        bank_cost = amount
        profit_margin_pct = random.uniform(15, 25)
        profit_amount = int(bank_cost * profit_margin_pct / 100)
        sale_price = bank_cost + profit_amount
        monthly_payment = sale_price // term_months
        
        # Asset details
        if asset_type == 'property':
            asset_desc = f"Residential villa, {random.randint(2,5)}-bedroom, {random.randint(1500,4000)} sq ft"
            location = fake.address()
        elif asset_type == 'vehicle':
            asset_desc = f"{fake.company()} {random.choice(['sedan', 'SUV', 'truck'])}, {random.randint(2020,2027)} model"
            location = "N/A (movable asset)"
        else:
            asset_desc = f"Commercial equipment: {fake.bs()}"
            location = fake.city()
        
        contract = {
            "contract_id": f"MRB-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}",
            "contract_type": "murabaha",
            "jurisdiction": "aaoifi",
            "date": datetime.now().isoformat(),
            "compliance_status": "compliant",
            "violations": [],
            
            "parties": {
                "bank": "Emirates Islamic Bank PJSC",
                "customer": customer_name,
                "customer_id": f"784-{random.randint(1980,2005)}-{random.randint(1000000,9999999)}-{random.randint(1,9)}"
            },
            
            "asset": {
                "type": asset_type,
                "description": asset_desc,
                "location": location,
                "title_deed": f"DLD-{random.randint(2020,2027)}-{random.randint(100000,999999)}" if asset_type == 'property' else "N/A"
            },
            
            "financial_terms": {
                "bank_cost": bank_cost,
                "profit_margin_pct": round(profit_margin_pct, 2),
                "profit_amount": profit_amount,
                "sale_price": sale_price,
                "down_payment": sale_price // 10,
                "financed_amount": sale_price - (sale_price // 10),
                "term_months": term_months,
                "monthly_payment": monthly_payment,
                "currency": "AED"
            },
            
            "key_clauses": {
                "profit_calculation": f"Fixed {profit_margin_pct:.1f}% markup on cost",
                "payment_schedule": f"{term_months} equal monthly installments of AED {monthly_payment:,}",
                "ownership_transfer": "Upon down payment, subject to registration",
                "early_settlement": "No penalty; bank may offer voluntary rebate (ibra')",
                "late_payment": "Actual damages only; no time-based penalties",
                "insurance_requirement": "Takaful (Islamic insurance) mandatory",
                "default_consequences": "Actual collection costs only, no compounding"
            },
            
            "shariah_compliance": {
                "board_approved": True,
                "board_members": [
                    "Dr. Sheikh Mohammed Al-Qassimi",
                    "Dr. Hussain Hamid Hassan",
                    "Dr. Abdul Sattar Abu Ghuddah"
                ],
                "aaoifi_standards": ["SS 8"],
                "approval_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
        }
        
        return contract
    
    def generate_non_compliant_contract(
        self,
        violation_types: List[str] = None,
        severity: Literal['low', 'medium', 'high', 'critical'] = 'high'
    ) -> Dict:
        """Generate contract with specific Shariah violations"""
        
        # Start with base structure
        customer_name = fake.name()
        amount = random.randint(50000, 500000)
        term_months = random.randint(24, 60)
        
        # Determine violations to include
        all_violations = [
            'explicit_interest',
            'variable_rate',
            'time_based_penalty',
            'compounding_penalty',
            'early_repayment_penalty',
            'no_asset_backing',
            'undefined_purpose',
            'conventional_insurance',
            'no_shariah_board'
        ]
        
        if violation_types is None:
            # Random selection based on severity
            num_violations = {
                'low': 1,
                'medium': 3,
                'high': 5,
                'critical': 8
            }[severity]
            violation_types = random.sample(all_violations, num_violations)
        
        contract = {
            "contract_id": f"BAD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}",
            "contract_type": "personal_financing",  # Red flag: not proper Islamic contract type
            "jurisdiction": "claimed_aaoifi",  # Red flag: claimed but not compliant
            "date": datetime.now().isoformat(),
            "compliance_status": "non_compliant",
            "violations": [],
            
            "parties": {
                "bank": "QuickCash Financial Services LLC",  # Fictional non-Islamic bank
                "customer": customer_name,
                "customer_id": f"784-{random.randint(1980,2005)}-{random.randint(1000000,9999999)}-{random.randint(1,9)}"
            },
            
            "financial_terms": {
                "loan_amount": amount,  # Red flag: "loan" not "sale"
                "term_months": term_months,
                "currency": "AED"
            },
            
            "key_clauses": {},
            
            "shariah_compliance": {
                "board_approved": False,
                "board_members": [],
                "aaoifi_standards": [],
                "approval_date": None
            }
        }
        
        # Add violations
        if 'explicit_interest' in violation_types:
            interest_rate = round(random.uniform(6.5, 12.5), 1)
            contract['financial_terms']['annual_interest_rate'] = interest_rate
            contract['key_clauses']['profit_calculation'] = f"Annual profit rate of {interest_rate}%"
            contract['violations'].append({
                "type": "riba",
                "severity": "critical",
                "pattern": "explicit_interest",
                "evidence": f"{interest_rate}% annual rate",
                "aaoifi_violation": "AAOIFI SS 8, Section 4.2"
            })
        
        if 'variable_rate' in violation_types:
            base_rate = round(random.uniform(5, 8), 1)
            spread = round(random.uniform(2, 4), 1)
            contract['key_clauses']['rate_adjustment'] = f"Rate = EIBOR + {spread}%, adjusted every 6 months"
            contract['violations'].append({
                "type": "riba",
                "severity": "critical",
                "pattern": "variable_rate",
                "evidence": f"EIBOR + {spread}%",
                "aaoifi_violation": "AAOIFI SS 8, Section 4.2"
            })
        
        if 'time_based_penalty' in violation_types:
            penalty_pct = round(random.uniform(1.5, 3), 1)
            contract['key_clauses']['late_payment_penalty'] = f"{penalty_pct}% per month on overdue amounts"
            contract['violations'].append({
                "type": "riba",
                "severity": "critical",
                "pattern": "time_based_penalty",
                "evidence": f"{penalty_pct}% per month",
                "aaoifi_violation": "AAOIFI SS 8, Section 5.1"
            })
        
        if 'compounding_penalty' in violation_types:
            contract['key_clauses']['compounding'] = "Late fees compound monthly if default continues beyond 30 days"
            contract['violations'].append({
                "type": "riba",
                "severity": "critical",
                "pattern": "compounding_interest",
                "evidence": "monthly compounding",
                "aaoifi_violation": "AAOIFI SS 8, Section 5.1"
            })
        
        if 'early_repayment_penalty' in violation_types:
            penalty_pct = random.randint(1, 3)
            contract['key_clauses']['early_settlement'] = f"{penalty_pct}% fee for early repayment"
            contract['violations'].append({
                "type": "riba",
                "severity": "high",
                "pattern": "early_repayment_penalty",
                "evidence": f"{penalty_pct}% fee",
                "aaoifi_violation": "AAOIFI SS 8, Section 6.2"
            })
        
        if 'no_asset_backing' in violation_types:
            contract['asset'] = {
                "type": "none",
                "description": "Unsecured cash loan",
                "location": "N/A"
            }
            contract['key_clauses']['collateral'] = "Unsecured loan - no specific asset backing"
            contract['violations'].append({
                "type": "gharar",
                "severity": "critical",
                "pattern": "no_asset_backing",
                "evidence": "cash loan without asset",
                "aaoifi_violation": "AAOIFI SS 8 (Murabaha requires asset)"
            })
        
        if 'undefined_purpose' in violation_types:
            contract['key_clauses']['purpose'] = "Funds may be used for any legal purpose"
            contract['violations'].append({
                "type": "gharar",
                "severity": "high",
                "pattern": "undefined_purpose",
                "evidence": "unspecified use of funds",
                "aaoifi_violation": "AAOIFI SS 8 (Murabaha requires specific asset)"
            })
        
        if 'conventional_insurance' in violation_types:
            contract['key_clauses']['insurance'] = "Optional credit life insurance from conventional provider"
            contract['violations'].append({
                "type": "non_compliant_ancillary",
                "severity": "medium",
                "pattern": "conventional_insurance",
                "evidence": "conventional insurance offered",
                "aaoifi_violation": "AAOIFI SS 50 (Takaful required)"
            })
        
        if 'no_shariah_board' in violation_types:
            contract['violations'].append({
                "type": "governance_failure",
                "severity": "high",
                "pattern": "no_shariah_approval",
                "evidence": "no documented Shariah board approval",
                "aaoifi_violation": "AAOIFI Governance Standard 1"
            })
        
        return contract
    
    def generate_pdf(self, contract: Dict, output_path: str):
        """Generate PDF document from contract dict"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph(
            f"<b>{contract['contract_type'].upper().replace('_', ' ')} AGREEMENT</b>",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Contract details
        details = f"""
        <b>Contract ID:</b> {contract['contract_id']}<br/>
        <b>Date:</b> {contract['date'][:10]}<br/>
        <b>Bank:</b> {contract['parties']['bank']}<br/>
        <b>Customer:</b> {contract['parties']['customer']}<br/>
        <b>Customer ID:</b> {contract['parties']['customer_id']}<br/>
        """
        story.append(Paragraph(details, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Financial terms
        if 'financial_terms' in contract:
            terms = contract['financial_terms']
            financial_text = "<b>FINANCIAL TERMS:</b><br/>"
            for key, value in terms.items():
                financial_text += f"{key.replace('_', ' ').title()}: {value}<br/>"
            story.append(Paragraph(financial_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Key clauses
        if 'key_clauses' in contract:
            clauses_text = "<b>KEY CLAUSES:</b><br/>"
            for key, value in contract['key_clauses'].items():
                clauses_text += f"<b>{key.replace('_', ' ').title()}:</b> {value}<br/>"
            story.append(Paragraph(clauses_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Violations (if any)
        if contract['violations']:
            violations_text = "<b>⚠️ SHARIAH VIOLATIONS DETECTED:</b><br/>"
            for v in contract['violations']:
                violations_text += f"• {v['type'].upper()} - {v['severity']}: {v['evidence']}<br/>"
            story.append(Paragraph(violations_text, styles['Normal']))
        
        doc.build(story)
    
    def generate_batch(
        self,
        num_compliant: int = 50,
        num_non_compliant: int = 50,
        output_dir: str = "data/generated_contracts"
    ):
        """Generate batch of test contracts"""
        import os
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/compliant", exist_ok=True)
        os.makedirs(f"{output_dir}/non_compliant", exist_ok=True)
        
        manifest = []
        
        # Generate compliant contracts
        for i in range(num_compliant):
            contract = self.generate_compliant_murabaha(
                asset_type=random.choice(['property', 'vehicle', 'equipment'])
            )
            
            contract_id = contract['contract_id']
            
            # Save JSON
            json_path = f"{output_dir}/compliant/{contract_id}.json"
            with open(json_path, 'w') as f:
                json.dump(contract, f, indent=2)
            
            # Save PDF
            pdf_path = f"{output_dir}/compliant/{contract_id}.pdf"
            self.generate_pdf(contract, pdf_path)
            
            manifest.append({
                "contract_id": contract_id,
                "type": contract['contract_type'],
                "compliance_status": "compliant",
                "violations_count": 0,
                "json_path": json_path,
                "pdf_path": pdf_path
            })
        
        # Generate non-compliant contracts
        severities = ['low'] * 10 + ['medium'] * 20 + ['high'] * 15 + ['critical'] * 5
        random.shuffle(severities)
        
        for i in range(num_non_compliant):
            contract = self.generate_non_compliant_contract(
                severity=severities[i % len(severities)]
            )
            
            contract_id = contract['contract_id']
            
            # Save JSON
            json_path = f"{output_dir}/non_compliant/{contract_id}.json"
            with open(json_path, 'w') as f:
                json.dump(contract, f, indent=2)
            
            # Save PDF
            pdf_path = f"{output_dir}/non_compliant/{contract_id}.pdf"
            self.generate_pdf(contract, pdf_path)
            
            manifest.append({
                "contract_id": contract_id,
                "type": contract['contract_type'],
                "compliance_status": "non_compliant",
                "violations_count": len(contract['violations']),
                "violations": [v['pattern'] for v in contract['violations']],
                "json_path": json_path,
                "pdf_path": pdf_path
            })
        
        # Save manifest
        manifest_path = f"{output_dir}/manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest

# CLI interface
if __name__ == "__main__":
    generator = ContractGenerator()
    
    print("Generating 100 test contracts (50 compliant, 50 non-compliant)...")
    manifest = generator.generate_batch(num_compliant=50, num_non_compliant=50)
    
    print(f"✅ Generated {len(manifest)} contracts")
    print(f"📁 Location: data/generated_contracts/")
    print(f"📋 Manifest: data/generated_contracts/manifest.json")
    
    # Statistics
    compliant_count = sum(1 for c in manifest if c['compliance_status'] == 'compliant')
    non_compliant_count = len(manifest) - compliant_count
    
    print(f"\n📊 Statistics:")
    print(f"  Compliant: {compliant_count}")
    print(f"  Non-compliant: {non_compliant_count}")
    print(f"  Total violations detected: {sum(c.get('violations_count', 0) for c in manifest)}")
```

---

## Phase 2: Backend Core (Days 4-7)

**Objective**: Implement LLM-powered analysis engine

### Components

**1. Clause Extraction Service**
- OpenAI GPT-4 integration
- Few-shot prompting (15 clause types)
- JSON parsing with error handling
- Confidence scoring

**2. Riba Detection Engine**
- Rule-based patterns (regex + keywords)
- LLM semantic analysis for ambiguous cases
- Hybrid scoring (rule + LLM confidence)
- AAOIFI standard citation matching

**3. Gharar Detection Engine**
- Asset backing verification
- Uncertainty pattern detection
- Ownership timeline analysis

**4. Report Generator**
- Markdown → PDF conversion
- Violation severity ranking
- Suggested alternatives
- Explainability sections

### API Endpoints

```python
# src/backend/api/contracts.py

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uuid

app = FastAPI(title="Shariah Compliance API")

@app.post("/api/v1/contracts/analyze")
async def analyze_contract(file: UploadFile):
    """
    Upload and analyze contract
    Returns: {contract_id, status, analysis_url}
    """
    contract_id = str(uuid.uuid4())
    
    # Extract text (OCR or direct PDF parsing)
    text = await extract_text(file)
    
    # Run analysis pipeline
    clauses = await extract_clauses(text)
    riba_violations = await detect_riba(clauses)
    gharar_violations = await detect_gharar(clauses)
    
    # Generate report
    report_path = await generate_report(
        contract_id, clauses, riba_violations, gharar_violations
    )
    
    return {
        "contract_id": contract_id,
        "status": "completed",
        "clauses_count": len(clauses),
        "violations": {
            "riba": len(riba_violations),
            "gharar": len(gharar_violations)
        },
        "tier": classify_tier(riba_violations, gharar_violations),
        "report_url": f"/api/v1/contracts/{contract_id}/report"
    }

@app.get("/api/v1/contracts/{contract_id}/report")
async def get_report(contract_id: str):
    """Download PDF report"""
    report_path = f"data/reports/{contract_id}.pdf"
    return FileResponse(report_path, filename=f"shariah_report_{contract_id}.pdf")
```

---

## Phase 3: Frontend Demo UI (Days 8-10)

**Objective**: Simple, clean demo interface

### Pages

**1. Upload Page**
- Drag-drop PDF upload
- Jurisdiction selector (AAOIFI/Malaysia/Hybrid)
- Real-time progress indicator

**2. Dashboard Page**
- Summary cards (clauses extracted, violations found)
- Severity breakdown (Critical/High/Medium/Low)
- Downloadable PDF report

**3. Violation Detail View**
- Clause excerpt with highlighting
- AAOIFI citation
- Suggested remediation
- Confidence score

### Tech Stack (Simplified for Demo)

```
- React 18 (create-react-app or Vite)
- Ant Design (UI components)
- Axios (API calls)
- React PDF Viewer (display uploaded contract)
```

---

## Phase 4: Integration & Demo Scenarios (Days 11-14)

**Objective**: End-to-end demo flows with narrative

### Demo Scenarios

**Scenario 1: Compliant Contract (Happy Path)**
1. Upload Emirates Islamic Murabaha contract (from generator)
2. Show real-time analysis (15 seconds)
3. Display dashboard: 0 violations, Tier 1 auto-approve
4. Show explainability: "Why is this compliant?" → AAOIFI citations
5. Download audit-ready PDF report

**Scenario 2: Non-Compliant Contract (Violation Detection)**
1. Upload QuickCash "Islamic" contract (6 riba violations)
2. Show analysis detecting all violations
3. Display dashboard: 6 critical violations, Tier 3 reject
4. Drill into each violation: evidence + AAOIFI reference + suggested fix
5. Show rejection report for scholar review

**Scenario 3: Batch Processing**
1. Run generator: create 20 contracts (10 compliant, 10 non-compliant)
2. Batch analyze via API script
3. Show accuracy metrics: precision/recall on known labels
4. Demonstrate ROI: 20 contracts analyzed in 5 minutes vs 3 days manual

---

## Quick Start Implementation Order

### Week 1: Foundation
**Days 1-2**: Contract generator + 100 test contracts
**Days 3-4**: Backend scaffolding + OpenAI integration
**Days 5-7**: Clause extraction + riba detection

### Week 2: Core Features
**Days 8-9**: Gharar detection + report generation
**Days 10-11**: Frontend dashboard (upload + results)
**Days 12-14**: Integration + demo scenarios

### Week 3: Polish
**Days 15-16**: Testing + bug fixes
**Days 17-18**: Documentation + demo script
**Days 19-21**: Capco presentation prep

---

## Technology Stack (Demo Version)

**Backend**:
- Python 3.11
- FastAPI (async API)
- OpenAI GPT-4 API
- PyPDF2 (PDF parsing)
- ReportLab (PDF generation)

**Frontend**:
- React 18 + TypeScript
- Vite (build tool)
- Ant Design (UI)
- Axios (HTTP client)

**Infrastructure** (Local Dev):
- Docker Compose (containerization)
- SQLite (simple DB for demo)
- Redis (LLM response caching)

---

## Key Files to Create

```
shariah/
├── src/
│   ├── generators/
│   │   └── contract_generator.py          ← START HERE (Day 1)
│   ├── backend/
│   │   ├── main.py                        ← FastAPI app (Day 3)
│   │   ├── services/
│   │   │   ├── clause_extractor.py        ← GPT-4 integration (Day 4)
│   │   │   ├── riba_detector.py           ← Rule engine + LLM (Day 5)
│   │   │   └── report_generator.py        ← PDF export (Day 6)
│   │   └── api/
│   │       └── contracts.py               ← API endpoints (Day 7)
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx                    ← Main app (Day 10)
│       │   ├── pages/
│       │   │   ├── Upload.tsx             ← Upload page (Day 10)
│       │   │   └── Dashboard.tsx          ← Results page (Day 11)
│       │   └── components/
│       │       ├── ViolationCard.tsx      ← Violation display (Day 11)
│       │       └── ReportDownload.tsx     ← Report button (Day 11)
├── scripts/
│   ├── generate_contracts.py              ← Batch generation CLI (Day 2)
│   └── run_demo.sh                        ← Demo launcher (Day 14)
├── requirements.txt                       ← Python deps
├── package.json                           ← Node deps
├── docker-compose.yml                     ← Local environment
└── README.md                              ← Setup instructions
```

---

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set up OpenAI API key**: Create `.env` with `OPENAI_API_KEY=sk-...`
3. **Generate test contracts**: `python src/generators/contract_generator.py`
4. **Run backend**: `uvicorn src.backend.main:app --reload`
5. **Run frontend**: `cd src/frontend && npm run dev`
6. **Test analysis**: Upload a generated contract and verify detection

**Goal**: Have working demo by end of Week 2, polish in Week 3 for Capco presentation.
