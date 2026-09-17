# Shariah Compliance Copilot - Product Requirements Document (PRD)

**Project**: Shariah Compliance Automation Demo for Capco  
**Version**: 1.0  
**Date**: September 17, 2026  
**Product Owner**: Alan Young (Capco CTO Consulting)  
**Target Market**: Islamic Financial Institutions (GCC, Malaysia, Global)

---

## 1. Product Vision

**Vision Statement**:  
Transform Shariah compliance from a manual, scholar-intensive bottleneck into an AI-assisted, scalable process that reduces audit time by 70% while maintaining 94% accuracy and full religious integrity.

**Mission**:  
Empower Islamic financial institutions to launch products faster, reduce compliance costs by 40%, and scale operations without proportionally increasing Shariah scholar headcount—while ensuring every AI decision is explainable and auditable.

**Target Outcome**:  
By Q2 2027, enable 5+ pilot institutions to process 1,000+ contracts/month with <10% requiring full manual scholar review, demonstrating clear path to production deployment.

---

## 2. Market Context

### 2.1 Market Opportunity

**Total Addressable Market (TAM)**:
- **$6 trillion** global Islamic finance assets (2026)
- **$9.7 trillion** projected by 2029 (LSEG-ICD)
- **300+** Islamic banks globally
- **200+** takaful operators

**Serviceable Addressable Market (SAM)**:
- **Tier 1 Markets**: UAE, Saudi Arabia, Malaysia (mature, high digitalization readiness)
- **150 institutions** with >$1B assets
- **Compliance spend**: ~20% of operating expenses = **$12-15B annually** (addressable via automation)

**Serviceable Obtainable Market (SOM)** (Year 1-2):
- **10-15 pilot institutions** (focus on Malaysia & UAE)
- **$5-8M ARR potential** at $500K-$1M per enterprise license

### 2.2 Competitive Landscape

**Direct Competitors**:
- **Azentio iMAL**: AAOIFI-certified core banking (16 years), but limited AI/LLM capabilities
- **Path Solutions**: Islamic finance software, rule-based compliance (no LLM)
- **In-house systems**: Most institutions use Excel + manual scholar review

**Competitive Advantages**:
1. **First-mover in LLM-powered Islamic finance**: No direct competitor with production-grade LLM compliance automation
2. **Hybrid approach**: Combines GPT-4 flexibility with AAOIFI rule-based precision (avoiding 40% accuracy ceiling of pure LLM)
3. **Capco credibility**: CTO consulting brand in financial services
4. **Explainability-first**: Built for regulatory audit from day one

**Threat Analysis**:
- **Big Tech entry**: Google/Microsoft could bundle Islamic finance features into cloud offerings
- **Incumbent integration**: Azentio/Path could partner with OpenAI/Anthropic
- **Regulatory hesitation**: Conservative institutions may resist AI in Shariah governance

### 2.3 User Personas

#### Persona 1: Fatima - Shariah Compliance Officer
**Profile**:
- Age: 32, Malaysian, Bachelor's in Islamic Banking + AAOIFI CIPA certification
- Works at mid-sized Islamic bank (5,000 contracts/year)
- Spends 60% of time on repetitive contract review, 20% on research, 20% on reporting

**Pain Points**:
- Manual clause extraction from 50-page contracts (3-4 hours/contract)
- Inconsistent interpretation (varies by officer fatigue/experience)
- Hard to find relevant fatwa precedents (scattered across PDF libraries)
- Pressure to reduce turnaround time from business teams

**Jobs-to-be-Done**:
- *"When I receive a new Murabaha contract, I want to quickly identify riba/gharar risks so I can focus my review on legitimate edge cases, not obvious violations."*
- *"When I encounter a novel structure, I want instant access to relevant Shariah precedents so I don't have to read 200 fatwas to find 3 relevant ones."*

**Success Metrics**:
- Reduce contract review time from 3 hours to 30 minutes
- Increase consistency (inter-rater reliability) from 82% to 95%
- Handle 2x contract volume without hiring additional staff

---

#### Persona 2: Sheikh Abdullah - Shariah Scholar
**Profile**:
- Age: 55, UAE national, PhD in Islamic Jurisprudence from Al-Azhar
- Serves on Shariah Supervisory Board for 3 institutions
- Reviews 50-80 complex contracts/month, issues 10-15 fatwas/year

**Pain Points**:
- Bottleneck: Business teams wait weeks for board meeting schedule
- Reviewing routine contracts is low-value use of expertise
- Hard to maintain consistency across institutions with different teams
- Accountability: If AI makes mistake, scholar reputation at risk

**Jobs-to-be-Done**:
- *"When the compliance team escalates a contract, I want confidence that routine checks were done correctly so I can focus on theological nuance, not catch clerical errors."*
- *"When approving an AI-flagged issue, I want to see the Shariah reasoning so I can validate it aligns with our board's interpretive framework."*
- *"When audit time comes, I want complete traceability showing every decision had human oversight at appropriate tier."*

**Success Metrics**:
- Reduce time spent on routine contracts from 60% to 20%
- Increase focus on innovation (new product structures) from 20% to 50%
- Zero compliance violations due to AI errors (human HITL prevents)
- Board approval for AI-assisted workflow

---

#### Persona 3: Rashid - Product Manager (Islamic Banking)
**Profile**:
- Age: 38, Saudi, MBA + 10 years product management
- Launching 3-5 new Islamic finance products per year
- Frustrated by 4-6 month compliance review cycle delaying launches

**Pain Points**:
- Compliance is black box ("we'll tell you in 3 months")
- Iterative design is impossible (each revision = another 2-month cycle)
- Hard to understand "why" product rejected (vague scholar feedback)
- Competitors launching faster

**Jobs-to-be-Done**:
- *"When designing a new sukuk structure, I want instant preliminary compliance feedback so I can iterate the design before formal scholar review."*
- *"When compliance flags an issue, I want suggested alternatives so I can fix it myself rather than waiting for next board meeting."*
- *"When pitching to leadership, I want confidence the structure will pass so I don't invest in a doomed product."*

**Success Metrics**:
- Reduce concept-to-launch from 6 months to 2 months
- Increase first-pass approval rate from 40% to 80%
- Cut product design iterations from 5 to 2

---

## 3. Product Features & Prioritization

### 3.1 MVP Feature Set (Proof-of-Concept)

**Phase 1 - Core Compliance Engine** (Weeks 1-8):

| Feature | User Story | Priority | Complexity | Value |
|---------|-----------|----------|------------|-------|
| **F1: Contract Upload & OCR** | As Fatima, I want to upload PDF contracts and get text extraction | P0 | Medium | High |
| **F2: Clause Extraction (15 types)** | As Fatima, I want key clauses auto-identified with confidence scores | P0 | High | Critical |
| **F3: Riba Detection (5 patterns)** | As Fatima, I want riba violations flagged with severity levels | P0 | High | Critical |
| **F4: Gharar Detection (4 patterns)** | As Fatima, I want gharar violations flagged with AAOIFI citations | P0 | High | Critical |
| **F5: Compliance Report (PDF/Word)** | As Sheikh Abdullah, I want audit-ready report with findings | P0 | Medium | High |
| **F6: HITL Tiering (Auto/Recommend/Assist)** | As Sheikh Abdullah, I want automatic tier assignment based on risk | P0 | Medium | Critical |

**Phase 2 - Fatwa Search** (Weeks 9-12):

| Feature | User Story | Priority | Complexity | Value |
|---------|-----------|----------|------------|-------|
| **F7: Fatwa Database Ingestion** | As Admin, I want to load AAOIFI/Malaysia SAC fatwas | P0 | Medium | High |
| **F8: Semantic Search Interface** | As Fatima, I want natural language fatwa search in English/Arabic | P0 | High | High |
| **F9: Fatwa Summarization** | As Rashid, I want 3-sentence fatwa summaries with key ruling | P1 | Medium | Medium |
| **F10: Contextual Recommendations** | As Fatima, I want relevant fatwas auto-suggested during contract review | P1 | Medium | High |

**Phase 3 - Enterprise Features** (Weeks 13-16):

| Feature | User Story | Priority | Complexity | Value |
|---------|-----------|----------|------------|-------|
| **F11: Multi-Jurisdiction Support** | As Admin, I want to switch between AAOIFI/Malaysia/Hybrid modes | P1 | Medium | Medium |
| **F12: Audit Trail & Explainability** | As Sheikh Abdullah, I want to see AI reasoning for every decision | P0 | Medium | Critical |
| **F13: User Access Control (RBAC)** | As Admin, I want role-based permissions (Officer/Scholar/PM/Auditor) | P1 | Low | Medium |
| **F14: Dashboard & Analytics** | As Manager, I want weekly stats (contracts reviewed, violations found, turnaround time) | P2 | Low | Low |

### 3.2 Feature Prioritization Matrix

**Priority Legend**:
- **P0 (Must-Have)**: POC fails without this
- **P1 (Should-Have)**: Enhances POC, deferrable to post-launch
- **P2 (Nice-to-Have)**: Future enhancement

**Prioritization Criteria**:
1. **User Value**: Does this solve a top-3 pain point?
2. **Technical Risk**: Can we build this reliably in timeline?
3. **Differentiation**: Does this beat competitors?
4. **Regulatory Requirement**: Is this mandatory for Shariah governance?

**MVP Scope Decision**:
- **In Scope**: F1-F8, F12, F13 (13 features)
- **Deferred**: F9-F11, F14 (4 features to post-MVP)
- **Out of Scope**: Real-time transaction monitoring, portfolio screening, zakat calculation

---

## 4. User Experience (UX) Design Principles

### 4.1 Core UX Principles

1. **Trust Through Transparency**: Every AI decision shows reasoning, confidence score, and "human review recommended" flag
2. **Scholar-Centric Design**: UI emphasizes human authority (AI as assistant, not decision-maker)
3. **Progressive Disclosure**: Show summary first, details on-demand (avoid overwhelming with 50-page reports)
4. **Bilingual Symmetry**: English and Arabic equally first-class (not translation layer)
5. **Error Tolerance**: System never auto-rejects contract; always offers "override & explain" option

### 4.2 Key User Flows

**Flow 1: Contract Compliance Review (Happy Path)**

```
[Fatima uploads PDF contract]
   ↓
[System extracts text (30s loading indicator)]
   ↓
[Dashboard shows: "15 clauses extracted, 2 potential riba violations, 1 gharar risk"]
   ↓
[Fatima clicks "2 potential riba violations"]
   ↓
[Detail view shows: Clause excerpt, severity (High), AAOIFI citation, suggested fix]
   ↓
[Fatima clicks "Request Scholar Review" (Tier 2)]
   ↓
[Sheikh Abdullah gets email notification]
   ↓
[Sheikh reviews, clicks "Approve with Conditions"]
   ↓
[System generates final report, logs decision to audit trail]
```

**Flow 2: Fatwa Semantic Search**

```
[Fatima types: "Can we charge early repayment fees in Ijara?"]
   ↓
[System searches (2s), returns 10 ranked fatwas]
   ↓
[Fatima clicks top result: "AAOIFI SS 9, Early Termination"]
   ↓
[Side panel shows: Summary, Full text, Related contracts, Cite button]
   ↓
[Fatima clicks "Cite in Report"]
   ↓
[Citation inserted: "Per AAOIFI SS 9 Section 3.4, early termination fees permissible if..."]
```

**Flow 3: Product Manager Pre-Flight Check**

```
[Rashid uploads draft sukuk structure document]
   ↓
[System runs analysis in "Advisory Mode" (non-binding)]
   ↓
[Dashboard shows: "3 compliance risks flagged, 5 alternative structures suggested"]
   ↓
[Rashid clicks "Alternative Structures"]
   ↓
[System shows: "Consider Wakalah structure instead of Mudarabah to avoid profit guarantee issue"]
   ↓
[Rashid revises design, re-uploads]
   ↓
[System shows: "0 critical risks, ready for formal scholar review"]
```

### 4.3 UI Mockup (Text-Based Wireframe)

**Main Dashboard** (after contract upload complete):

```
┌─────────────────────────────────────────────────────────────┐
│ Shariah Compliance Copilot            [Settings] [Logout]   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Contract: Murabaha_ABC_Bank_Customer123.pdf                 │
│  Uploaded: 2026-09-17 10:15 AM   Status: ⚠️ Review Required │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 Analysis Summary                                  │   │
│  │                                                       │   │
│  │  ✅ 15 Clauses Extracted (85% confidence)            │   │
│  │  ⚠️  2 Riba Violations (1 Critical, 1 High)          │   │
│  │  ⚠️  1 Gharar Risk (Medium)                          │   │
│  │  ℹ️  3 Ambiguous Clauses (Manual Review Recommended) │   │
│  │                                                       │   │
│  │  Tier: 2 (Recommend - Human Approval Required)       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [View Detailed Report]  [Search Related Fatwas]             │
│  [Request Scholar Review]  [Export PDF]                      │
│                                                               │
│  🚨 Critical Issues (1)                                      │
│  ─────────────────────────────────────────────────────────  │
│  ❌ Riba - Time-Based Penalty                                │
│     Clause 7.2: "1.5% monthly late payment charge"          │
│     Violation: AAOIFI SS 8, Section 4.2 (Interest Prohibition)│
│     Suggested Fix: Replace with actual damages clause        │
│     [View Details] [Override & Explain]                      │
│                                                               │
│  ⚠️  High Priority Issues (1)                                │
│  ─────────────────────────────────────────────────────────  │
│  ⚠️  Riba - Guaranteed Return Language                       │
│     Clause 12.1: "Bank guarantees 8% profit distribution"   │
│     Violation: AAOIFI SS 13, Section 2.1 (Profit-Loss Sharing)│
│     Suggested Fix: Replace with "expected profit of 8%..."  │
│     [View Details] [Accept Suggestion]                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Constraints & Requirements

### 5.1 Technology Stack Decisions

**LLM Provider**: 
- **Primary**: OpenAI GPT-4 Turbo (128K context, JSON mode, function calling)
- **Backup**: Anthropic Claude 3 Opus (200K context, constitutional AI for safety)
- **Rationale**: GPT-4 offers best balance of accuracy, speed, and ecosystem maturity. Claude as fallback for data residency concerns (EU/Malaysia).

**Vector Database** (for fatwa search):
- **Primary**: Pinecone (managed, serverless, <500ms query latency)
- **Alternative**: Weaviate (self-hosted option for on-premise deployments)

**Rule Engine** (AAOIFI standards):
- **Primary**: Python-based rule engine (JSON config files per jurisdiction)
- **Future**: Consider Drools (Java) for complex multi-step rules

**OCR**:
- **Primary**: Azure Form Recognizer (95%+ accuracy on Arabic/English)
- **Backup**: AWS Textract

**Backend**:
- **Framework**: FastAPI (Python 3.11+) for async API performance
- **Database**: PostgreSQL 15 (audit trail, user management)
- **Caching**: Redis (LLM response caching to reduce API costs)

**Frontend**:
- **Framework**: React 18 + TypeScript
- **UI Library**: Ant Design (enterprise-grade, Arabic RTL support)
- **State Management**: Zustand (lightweight vs. Redux)

**Deployment**:
- **Infrastructure**: AWS (Singapore region for Asia latency) or Azure (UAE North for MENA)
- **Container**: Docker + Kubernetes (EKS/AKS)
- **CI/CD**: GitHub Actions
- **Monitoring**: Datadog (APM, logs, custom metrics)

### 5.2 Performance Budgets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Contract analysis (10-page) | <60 seconds | Competitive with manual pre-screening |
| Fatwa search query | <3 seconds | Faster than Ctrl+F in PDF |
| UI first contentful paint | <2 seconds | Standard web performance |
| LLM API P95 latency | <10 seconds | GPT-4 Turbo typical response time |
| Concurrent users | 50 | Pilot institution usage peak |
| Database query time | <100ms | Standard OLTP performance |

### 5.3 Data Privacy & Security

**Data Classification**:
- **Highly Sensitive**: Contract full text, Shariah board decisions
- **Sensitive**: User credentials, audit logs
- **Public**: AAOIFI standards, public fatwa databases

**Compliance Requirements**:
- **GDPR** (EU clients): Right to erasure, data portability
- **PDPA** (Malaysia): Data residency (must store in Malaysia data centers)
- **UAE PDPL**: Consent for AI processing, local storage option

**Security Measures**:
- **Encryption at Rest**: AES-256 (AWS KMS or Azure Key Vault)
- **Encryption in Transit**: TLS 1.3
- **API Security**: OAuth2 + JWT, rate limiting (100 requests/minute/user)
- **Audit Logging**: Immutable append-only log (PostgreSQL + blockchain-ready design)
- **No Model Training on Customer Data**: Zero-retention policy with OpenAI API

---

## 6. Business Model & Pricing

### 6.1 Revenue Model

**Primary**: **SaaS Subscription** (Annual Contract)

**Pricing Tiers**:

| Tier | Target | Contract Volume | Price/Year | Features |
|------|--------|----------------|------------|----------|
| **Starter** | Small takaful operators | <500 contracts/year | $25K | Single jurisdiction, 5 users, email support |
| **Professional** | Mid-sized Islamic banks | 500-5,000 contracts/year | $100K | Multi-jurisdiction, 25 users, fatwa search, priority support |
| **Enterprise** | Large banks (Al Rajhi, Maybank Islamic) | >5,000 contracts/year | $500K-$1M | Unlimited users, custom rule configuration, dedicated CSM, on-premise option |

**Secondary**: **Professional Services**

- **Implementation**: $50K-$150K (data migration, integration, training)
- **Custom Fatwa Ingestion**: $10K-$25K per institution's historical fatwa database
- **Ongoing Support**: Included in Enterprise tier, 20% of contract value for Professional tier

### 6.2 Unit Economics

**Customer Acquisition Cost (CAC)**:
- **Sales Cycle**: 6-9 months (enterprise sales in financial services)
- **Cost per Lead**: $500 (conference sponsorships, LinkedIn ads)
- **Conversion Rate**: 10% (qualified lead → pilot → paid contract)
- **CAC**: $50K per customer (assume 10 leads to close 1)

**Lifetime Value (LTV)**:
- **Average Contract**: $150K/year (weighted average of tiers)
- **Gross Margin**: 75% (SaaS typical after infrastructure costs)
- **Customer Lifetime**: 5 years (enterprise software retention)
- **LTV**: $562K (150K × 0.75 × 5)

**LTV:CAC Ratio**: 11.2x (healthy SaaS benchmark is >3x)

### 6.3 Go-to-Market Strategy

**Phase 1: Pilot Program** (Q1-Q2 2027)
- **Target**: 3-5 design partners (1 Malaysia, 2 GCC, 1 other)
- **Pricing**: Heavily discounted ($10K-$25K) in exchange for case study rights
- **Success Criteria**: 70%+ time reduction, 85%+ accuracy, regulatory acceptance

**Phase 2: Launch** (Q3-Q4 2027)
- **Target**: 15-20 paying customers
- **Channels**: Islamic finance conferences (WIBC Dubai, GIFF Malaysia), direct sales
- **Partnerships**: Reseller agreements with Azentio/Path Solutions (bundle with core banking)

**Phase 3: Scale** (2028+)
- **Target**: 50+ customers, $10M ARR
- **Product Expansion**: Real-time transaction monitoring, portfolio screening, zakat calculation
- **Geographic Expansion**: Indonesia, Pakistan, Turkey, UK (Islamic finance hubs)

---

## 7. Risk Assessment & Mitigation

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **LLM Hallucination** (fabricated AAOIFI citations) | Medium | Critical | Validation layer: every citation cross-checked against source database before presenting to user |
| **Accuracy Below 85% Threshold** | Medium | High | Hybrid approach: LLM + rule engine; extensive testing on 500-contract validation set |
| **Latency >60s** (user abandonment) | Low | Medium | Optimize prompts, use streaming responses, show progress indicators |
| **API Cost Overruns** (GPT-4 expensive) | Medium | Medium | Implement aggressive caching (Redis), use GPT-3.5 for low-risk tasks, negotiate volume discounts |

### 7.2 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Regulatory Rejection** (central banks ban AI in Shariah governance) | Low | Critical | Early engagement with BNM, UAE Central Bank; position as "assistant" not "decision-maker"; ensure HITL at all tiers |
| **Shariah Scholar Resistance** | Medium | High | Scholar advisory board from day one; transparent explainability; no replacement narrative (augmentation only) |
| **Slow Enterprise Sales** (long pilots) | High | Medium | Build 3-5 design partner relationships early; leverage Capco consulting network for warm intros |
| **Competitor Entry** (Microsoft/Google bundle Islamic finance into Azure/GCP) | Medium | High | First-mover advantage; deep domain expertise (AAOIFI certification pathway); position as specialized vs. generic |

### 7.3 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Talent Shortage** (need Islamic finance + AI expertise) | High | Medium | Partner with INCEIF (Malaysia Islamic finance university) for talent pipeline; remote-first team |
| **Data Labeling Quality** (need scholar-annotated training data) | Medium | High | Hire 2-3 retired Shariah scholars as advisors; rigorous inter-annotator agreement checks (κ>0.90) |
| **Customer Data Breach** | Low | Critical | SOC2 Type II compliance; penetration testing; cyber insurance; incident response plan |

---

## 8. Success Metrics & KPIs

### 8.1 Product Metrics (Leading Indicators)

**Activation**:
- % of users who complete first contract analysis within 7 days of signup: **>80%**
- Time-to-first-value (upload → report generated): **<10 minutes**

**Engagement**:
- Weekly active users (WAU) / Monthly active users (MAU): **>60%** (enterprise SaaS benchmark)
- Avg contracts analyzed per user per week: **>10**
- Fatwa search queries per user per week: **>5**

**Retention**:
- Month-1 retention (users who return after first use): **>70%**
- Annual renewal rate: **>90%** (enterprise software standard)

### 8.2 Business Metrics (Lagging Indicators)

**Revenue**:
- Annual Recurring Revenue (ARR): $1.5M by end of Year 1 (10 customers × $150K avg)
- Net Revenue Retention (NRR): >110% (upsells from Starter → Professional → Enterprise)

**Customer Acquisition**:
- Sales pipeline: 30 qualified leads, 10 active pilots, 3 closed deals per quarter
- Time to close (first demo → signed contract): <9 months

**Operational Efficiency**:
- Gross margin: >75%
- Customer support tickets per user per month: <0.5
- NPS (Net Promoter Score): >50 (good SaaS benchmark)

### 8.3 Impact Metrics (Customer Outcomes)

**Primary**: Measured in pilot case studies
- ✅ **Audit time reduction**: Baseline 3 days → Target 6-12 hours (**70-85% reduction**)
- ✅ **Accuracy improvement**: Baseline 78% → Target 85-94% (**+7-16 percentage points**)
- ✅ **Cost savings**: $200K-$500K per year per institution (avoided hiring 2-3 compliance officers)

**Secondary**:
- Product launch cycle time: 6 months → 2 months (measured with Product Manager persona)
- Scholar satisfaction: "AI allows me to focus on innovation" (qualitative interviews)
- Regulatory audit pass rate: 100% (no violations attributed to AI errors)

---

## 9. Roadmap & Milestones

### 9.1 Development Phases

**Phase 0: Foundation** (Weeks 1-2)
- ✅ Requirements finalized (this document)
- ✅ Architecture designed (separate document)
- 🔲 Development environment setup
- 🔲 Contract dataset sourced (50 anonymized samples)

**Phase 1: MVP Backend** (Weeks 3-6)
- 🔲 OCR integration (Azure Form Recognizer)
- 🔲 Clause extraction (GPT-4 + few-shot prompts)
- 🔲 Riba/gharar detection (rule engine + LLM)
- 🔲 AAOIFI knowledge base (vector database)
- 🔲 Report generation (PDF/Word export)

**Phase 2: MVP Frontend** (Weeks 7-10)
- 🔲 Contract upload UI
- 🔲 Dashboard (summary + detailed findings)
- 🔲 HITL workflow (approve/reject/escalate)
- 🔲 User authentication & RBAC

**Phase 3: Fatwa Search** (Weeks 11-14)
- 🔲 Fatwa ingestion pipeline
- 🔲 Semantic search (vector similarity)
- 🔲 Summarization (GPT-4)
- 🔲 Contextual recommendations

**Phase 4: Polish & Testing** (Weeks 15-16)
- 🔲 End-to-end testing (50-contract test set)
- 🔲 Performance optimization (caching, prompt tuning)
- 🔲 Security audit (penetration testing)
- 🔲 Documentation (user guide, API docs)

**Phase 5: Pilot Deployment** (Week 17+)
- 🔲 Deploy to pilot institution (Malaysia or UAE)
- 🔲 Onboard 5-10 users
- 🔲 Monitor usage, collect feedback
- 🔲 Iterate based on real-world performance

### 9.2 Decision Points

**Go/No-Go Gates**:

1. **End of Phase 1 (Week 6)**:
   - **Criteria**: Riba/gharar detection accuracy >80% on 25-contract validation set
   - **Decision**: Proceed to frontend or revisit prompts/rules

2. **End of Phase 3 (Week 14)**:
   - **Criteria**: Fatwa search relevance (Top-3 contains answer) >75%
   - **Decision**: Proceed to pilot or add more fatwas to database

3. **End of Pilot (Week 20)**:
   - **Criteria**: >70% time reduction, >85% accuracy, NPS >40
   - **Decision**: Launch commercially or iterate on pain points

---

## 10. Open Questions & Decisions Needed

**Technical Decisions**:
1. ❓ **LLM vendor lock-in**: Should we abstract LLM layer (LangChain) or commit to OpenAI API?
   - **Trade-off**: Abstraction adds complexity but reduces vendor risk
   - **Recommendation**: Direct OpenAI integration for MVP, abstract in Phase 2

2. ❓ **On-premise vs. Cloud**: Should we support on-premise deployment from day one?
   - **Trade-off**: On-prem adds ops burden but critical for conservative GCC banks
   - **Recommendation**: Cloud-only MVP, containerize for easy on-prem in Phase 2

3. ❓ **AAOIFI licensing**: Can we embed full standards in product or only reference?
   - **Action Required**: Legal review + AAOIFI partnership discussion

**Business Decisions**:
4. ❓ **Design partners**: Which 3-5 institutions to target for pilots?
   - **Candidates**: Bank Islam Malaysia (known from research), Emirates Islamic (UAE), Qatar Islamic Bank, Bank Muamalat Malaysia, Al Rajhi Takaful (Saudi)
   - **Criteria**: Geographic diversity, willingness to co-innovate, access via Capco network

5. ❓ **Pricing validation**: Is $100K-$500K acceptable or too high?
   - **Action Required**: Customer development interviews (10-15 target institutions)

6. ❓ **Capco brand**: Launch under "Capco Shariah AI" or spin out separate brand?
   - **Trade-off**: Capco brand credibility vs. startup agility

---

## 11. Appendices

### Appendix A: Glossary

See main research report Appendix for full Islamic finance terms.

Key terms for product context:
- **AAOIFI**: Accounting and Auditing Organization for Islamic Financial Institutions (standard-setting body)
- **Murabaha**: Cost-plus financing (most common Islamic financing structure)
- **Ijara**: Leasing arrangement
- **Riba**: Interest/usury (prohibited)
- **Gharar**: Excessive uncertainty/speculation (prohibited)
- **Shariah Supervisory Board**: Panel of 3-5 scholars who approve products
- **HITL**: Human-in-the-Loop (AI decision-making governance)

### Appendix B: References

- [Bank Islam Malaysia Case Study](https://www.bankislam.com/shariah-ai-2024) - 70% audit time reduction
- [Prudential BSN Takaful Case Study](https://www.prudentialbsn.com.my/ai-underwriting-2025) - 5 days → 30 min
- [BNM AI Governance Framework](https://media.fintradesecurities.com/feature-articles/malaysian-insurtech-advances-algorithmic-underwriting-post-bnm-ai-consultation)
- [AAOIFI Shariah Standards](https://aaoifi.com) - 60+ standards
- Enhanced Islamic Finance & AI Research Report 2026 (Chapter 6)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-17 | Alan Young | Initial PRD - aligned with FRD v1.0 |

---

**Status**: ✅ Ready for Architecture Design  
**Next Deliverable**: System Architecture Document (detailed component design, data flows, deployment topology)
