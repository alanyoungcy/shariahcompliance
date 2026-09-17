# Shariah Compliance Copilot - Functional Requirements Document (FRD)

**Project**: Shariah Compliance Automation Demo for Capco  
**Version**: 1.0  
**Date**: September 17, 2026  
**Author**: Alan Young (Capco CTO Consulting)  
**Target Audience**: Islamic Financial Institutions (Banks, Takaful Operators)

---

## 1. Executive Summary

This document defines the functional requirements for a **Shariah Compliance Copilot** - an AI-powered proof-of-concept system that automates Shariah audit workflows for Islamic financial institutions. The system combines large language models (LLMs) with rule-based AAOIFI standards to achieve:

- **70% reduction in audit time** (3 days → 6 hours baseline)
- **94% accuracy target** in detecting riba/gharar violations
- **Dual-mode operation**: Contract compliance automation + Fatwa semantic search

**Core Value Proposition**: Transform manual, scholar-intensive Shariah compliance from a bottleneck into a scalable, explainable AI-assisted process while maintaining religious integrity.

---

## 2. System Overview

### 2.1 Target Users

**Primary Users**:
- **Shariah Compliance Officers**: Day-to-day contract review and preliminary screening
- **Shariah Scholars**: Final approval and complex rulings
- **Product Managers**: Pre-launch compliance validation for new Islamic finance products

**Secondary Users**:
- **Audit Teams**: Quarterly compliance reporting
- **Regulators**: Compliance evidence review

### 2.2 Operating Context

**Deployment Model**: Cloud-based SaaS with on-premise option for data sovereignty  
**Integration Requirements**: 
- Document management systems (PDF/Word contract ingestion)
- Core banking systems (API integration for transaction monitoring - future phase)
- Fatwa database repositories (initially seeded, user-augmentable)

**Regulatory Context**:
- AAOIFI Shariah Standards (60+ standards)
- Malaysia Bank Negara Malaysia (BNM) guidelines
- UAE Central Bank Shariah governance requirements

---

## 3. Functional Requirements

### 3.1 Use Case 1: Contract Compliance Automation

#### FR-1.1: Contract Document Ingestion
**Description**: System accepts Shariah-compliant financing contracts for automated review.

**User Story**:  
*As a Shariah Compliance Officer, I want to upload Murabaha/Ijara contracts in PDF or Word format so that the system can extract and analyze compliance-relevant clauses without manual data entry.*

**Acceptance Criteria**:
- ✅ Support PDF and DOCX formats (up to 50 pages)
- ✅ Extract text with 95%+ OCR accuracy for Arabic and English documents
- ✅ Preserve document structure (headers, tables, signature blocks)
- ✅ Handle mixed-language documents (Arabic + English)
- ✅ Process upload within 30 seconds for typical 10-page contract

**Edge Cases**:
- Scanned documents with poor quality (flag for manual review)
- Handwritten annotations (ignore or flag)
- Redacted sections (detect and note in report)

---

#### FR-1.2: Clause Extraction & Classification
**Description**: LLM identifies and categorizes key contractual clauses requiring Shariah review.

**User Story**:  
*As a Shariah Compliance Officer, I want the system to automatically identify profit calculation methods, payment schedules, penalty clauses, and collateral terms so I can focus review on high-risk areas.*

**Acceptance Criteria**:
- ✅ Extract minimum 15 clause types:
  - Profit calculation method (cost-plus margin)
  - Payment schedule (installments, due dates)
  - Late payment penalties
  - Collateral/security arrangements
  - Asset ownership transfer timing
  - Insurance requirements
  - Termination conditions
  - Dispute resolution mechanism
  - Parties (bank/mudarib, customer/rab-ul-mal)
  - Underlying asset description
  - Purchase price and sale price (for Murabaha)
  - Rental terms (for Ijara)
  - Risk allocation
  - Ownership warranties
  - Governing law and jurisdiction

- ✅ Assign confidence score (0-100%) to each extracted clause
- ✅ Link extracted clauses to original document locations (page + paragraph)
- ✅ Flag ambiguous clauses for human review (confidence <70%)

**Technical Approach**:
- GPT-4 with few-shot prompting (10-15 examples per clause type)
- Named Entity Recognition (NER) for parties, amounts, dates
- Regex patterns for structured data (payment schedules, percentages)

---

#### FR-1.3: Riba (Interest) Detection
**Description**: System identifies explicit and implicit interest-based elements prohibited under Shariah.

**User Story**:  
*As a Shariah Scholar, I want the system to flag any riba violations with specific evidence and severity level so I can prioritize review and provide corrective guidance.*

**Acceptance Criteria**:
- ✅ Detect 5 riba patterns:
  1. **Explicit interest rate** (e.g., "5% annual interest", "LIBOR + 2%")
  2. **Time-value-of-money penalties** (e.g., "1% per day late fee")
  3. **Guaranteed fixed returns** (violates profit-loss sharing principle)
  4. **Rollover fees** (penalty for deferring payment)
  5. **Hidden interest** (inflated prices with deferred payment vs. cash price differential >5%)

- ✅ Severity classification:
  - **CRITICAL**: Explicit interest language (auto-reject)
  - **HIGH**: Time-based penalties without clear asset backing
  - **MEDIUM**: Ambiguous cost structures requiring clarification
  - **LOW**: Minor terminology issues (e.g., "interest" used colloquially)

- ✅ Provide AAOIFI standard citation for each violation (e.g., "Violates AAOIFI SS 8, Section 4.2")
- ✅ Suggest Shariah-compliant alternatives (e.g., "Replace 5% interest with profit-sharing ratio")

**Technical Approach**:
- Rule-based engine for explicit patterns (regex + keyword matching)
- LLM semantic analysis for implicit violations
- AAOIFI standards knowledge base (embedded in vector database)

---

#### FR-1.4: Gharar (Excessive Uncertainty) Detection
**Description**: System identifies elements of excessive uncertainty or speculation prohibited under Shariah.

**User Story**:  
*As a Shariah Compliance Officer, I want the system to detect gharar elements like undefined asset specifications, ambiguous delivery terms, or contingent obligations so contracts meet certainty requirements.*

**Acceptance Criteria**:
- ✅ Detect 4 gharar patterns:
  1. **Undefined asset specifications** (e.g., "property to be determined later")
  2. **Ambiguous delivery/transfer terms** (e.g., "approximately 30 days")
  3. **Contingent pricing** (e.g., "price depends on market conditions")
  4. **Speculative elements** (e.g., futures contracts without asset backing)

- ✅ Flag missing required elements:
  - Asset description completeness
  - Ownership clarity at each transaction stage
  - Delivery timeline specificity
  - Price certainty at contract inception

- ✅ Cross-reference contract type (Murabaha requires full asset specification; Ijara requires clear ownership transfer timeline)

**Technical Approach**:
- LLM semantic analysis for vague language
- Checklist validation (contract type → required elements mapping)
- Fuzzy matching for incomplete descriptions

---

#### FR-1.5: Compliance Report Generation
**Description**: System generates human-readable audit reports with findings, evidence, and recommendations.

**User Story**:  
*As a Shariah Scholar, I want a comprehensive compliance report showing all flagged issues, their Shariah basis, original contract excerpts, and suggested remedies so I can make informed approval decisions.*

**Acceptance Criteria**:
- ✅ Report structure:
  - Executive summary (pass/fail, critical issues count)
  - Detailed findings by severity (Critical > High > Medium > Low)
  - For each finding:
    - Issue description
    - Contract excerpt with page reference
    - AAOIFI standard citation
    - Severity rationale
    - Suggested remediation
  - Extracted clauses reference table
  - Compliance checklist (AAOIFI standards coverage)
  - Explainability section (how AI reached conclusions)

- ✅ Export formats: PDF, Word, JSON (for system integration)
- ✅ Include confidence scores and "human review recommended" flags
- ✅ Version tracking (report ID, timestamp, contract hash)
- ✅ Support for multi-language reports (English and Arabic)

**Technical Approach**:
- Jinja2 templating for report generation
- Markdown → PDF conversion (Pandoc or WeasyPrint)
- Citation linking to AAOIFI online standards

---

### 3.2 Use Case 2: Fatwa Semantic Search

#### FR-2.1: Fatwa Database Ingestion
**Description**: System indexes historical Shariah rulings from recognized scholars and institutions.

**User Story**:  
*As a system administrator, I want to ingest fatwa collections from AAOIFI, Malaysia's Shariah Advisory Council, and UAE's Higher Sharia Authority so the system can reference authoritative precedents.*

**Acceptance Criteria**:
- ✅ Ingest fatwa sources:
  - AAOIFI Shariah Standards (60+ standards)
  - Malaysia SAC fatwas (Bank Negara Malaysia repository)
  - UAE Central Bank Shariah rulings
  - Custom institutional fatwas (user-uploaded)

- ✅ Extract metadata:
  - Fatwa ID/reference number
  - Issuing authority (scholar name, institution)
  - Date issued
  - Contract type (Murabaha, Ijara, Sukuk, etc.)
  - Keywords/topics (riba, gharar, zakat, etc.)
  - Full text in original language
  - English translation (if available)

- ✅ Support incremental updates (add new fatwas without reindexing entire database)
- ✅ Validate authenticity (checksum verification for official sources)

**Technical Approach**:
- Web scraping for public repositories (respecting robots.txt)
- PDF extraction for official publications
- Vector embeddings (OpenAI Ada-002 or similar) for semantic search
- Metadata stored in PostgreSQL, embeddings in Pinecone/Weaviate

---

#### FR-2.2: Semantic Search Query Interface
**Description**: Natural language search across fatwa database to find relevant precedents.

**User Story**:  
*As a Shariah Compliance Officer, I want to search "Can we charge processing fees for Murabaha contracts?" and get ranked fatwa excerpts addressing this question so I don't have to manually review hundreds of rulings.*

**Acceptance Criteria**:
- ✅ Accept natural language queries in English and Arabic
- ✅ Return top 10 ranked results with:
  - Fatwa title/summary
  - Relevance score (0-100%)
  - Issuing authority
  - Key excerpt (2-3 sentences)
  - Full text link
  - Related contract types

- ✅ Support filters:
  - Authority (AAOIFI, Malaysia SAC, UAE, custom)
  - Date range
  - Contract type
  - Madhab (school of thought) - future enhancement

- ✅ Handle synonyms and transliterations (e.g., "Murabaha" = "Murabahah" = "مرابحة")
- ✅ Response time <3 seconds for typical query

**Technical Approach**:
- Semantic search via vector similarity (cosine distance)
- Hybrid search (combine semantic + keyword BM25 ranking)
- Query expansion using LLM (rephrase user query into 3-5 variants)
- Re-ranking using cross-encoder (BERT-based relevance scoring)

---

#### FR-2.3: Fatwa Summarization & Extraction
**Description**: LLM generates concise summaries of long fatwa texts and extracts actionable guidance.

**User Story**:  
*As a Product Manager, I want a 3-sentence summary of a 20-page fatwa plus clear "permissible/impermissible" determination so I can quickly assess new product ideas.*

**Acceptance Criteria**:
- ✅ Generate summaries:
  - **Executive summary** (50-100 words)
  - **Key ruling** (permissible/impermissible/conditional)
  - **Conditions** (if ruling is conditional)
  - **Rationale** (Quranic/Hadith basis, 1-2 sentences)

- ✅ Extract structured guidance:
  - Required contract clauses
  - Prohibited elements
  - Recommended practices
  - Edge cases addressed

- ✅ Maintain original language nuance (avoid oversimplification that changes meaning)
- ✅ Flag "scholar discretion varies" cases (e.g., differing madhab interpretations)

**Technical Approach**:
- GPT-4 summarization with custom prompt template
- Few-shot examples (10 fatwa summaries reviewed by scholar)
- Validation: compare summary to original using semantic similarity (>85% threshold)

---

#### FR-2.4: Contextual Fatwa Recommendation
**Description**: When reviewing a contract, system proactively suggests relevant fatwa precedents.

**User Story**:  
*As a Shariah Compliance Officer reviewing a new Ijara contract, I want the system to automatically surface relevant fatwas about lease-to-own structures so I can reference authoritative guidance without manual search.*

**Acceptance Criteria**:
- ✅ Trigger recommendations when:
  - Ambiguous clause detected (confidence <70%)
  - Novel contract structure (no exact template match)
  - User explicitly requests "find similar fatwas"

- ✅ Recommendation criteria:
  - Contract type match (Ijara → Ijara fatwas)
  - Issue similarity (lease-to-own → ownership transfer timing fatwas)
  - Authority preference (prioritize user's jurisdiction)

- ✅ Display in sidebar during contract review:
  - "3 relevant fatwas found"
  - Click to expand summary
  - One-click insert citation into report

**Technical Approach**:
- Real-time embedding of contract clauses
- Vector search against fatwa database
- Ranking by (semantic similarity × authority weight × recency)

---

### 3.3 Cross-Cutting Requirements

#### FR-3.1: Explainability & Audit Trail
**Description**: Every AI decision must be explainable to satisfy Shariah governance and regulatory audit.

**Functional Requirements**:
- ✅ Record for each analysis:
  - Model version (GPT-4 turbo, AAOIFI rule engine v2.1, etc.)
  - Input data snapshot (contract text, metadata)
  - Intermediate reasoning steps (which clauses triggered which rules)
  - Output with confidence scores
  - Human review override (if scholar disagrees, reason logged)

- ✅ Generate explainability reports:
  - "Why was this flagged as riba?" → "Clause X contains time-based penalty 'Y% per month late', violating AAOIFI SS 8..."
  - "Why this fatwa recommended?" → "Query 'processing fees' matched fatwa #123 (87% similarity) which addresses 'administrative charges in Murabaha'..."

- ✅ Immutable audit trail (append-only log, blockchain optional for production)

**Technical Approach**:
- Structured logging (JSON format)
- SHAP values for ML components (if using fine-tuned models in future)
- Chain-of-thought prompting for LLM (record reasoning steps)

---

#### FR-3.2: User Access Control
**Description**: Role-based access control aligning with Shariah governance structure.

**Roles & Permissions**:

| Role | Permissions |
|------|------------|
| **Compliance Officer** | Upload contracts, run analysis, view reports, search fatwas |
| **Shariah Scholar** | All Officer permissions + approve/reject findings, edit fatwa database, access audit trail |
| **Product Manager** | Run analysis (read-only), search fatwas, cannot approve |
| **Auditor** | Read-only access to all reports and audit trails |
| **System Admin** | Manage users, configure AAOIFI rules, ingest fatwas, view system logs |

**Acceptance Criteria**:
- ✅ Authentication via OAuth2 (SSO with institution's Active Directory)
- ✅ Multi-factor authentication for Shariah Scholar role
- ✅ Session timeout after 30 minutes inactivity
- ✅ Audit log of all user actions (who reviewed what, when)

---

#### FR-3.3: Multi-Jurisdiction Support
**Description**: Accommodate differences between AAOIFI (GCC), Malaysia (BNM), and other frameworks.

**Functional Requirements**:
- ✅ Jurisdiction selection at contract upload:
  - **AAOIFI-compliant** (Bahrain, UAE, Saudi Arabia, etc.)
  - **Malaysia BNM**
  - **Hybrid** (satisfy both - for cross-border transactions)

- ✅ Jurisdiction-specific rules:
  - Malaysia allows organized tawarruq, AAOIFI classical only
  - Debt/asset ratio thresholds vary (AAOIFI 33%, Malaysia 33%)
  - Non-halal income tolerance (AAOIFI 5%, Malaysia 5%, but calculation differs)

- ✅ Flag jurisdictional conflicts for hybrid mode (e.g., "This sukuk structure compliant in Malaysia but not AAOIFI-compliant jurisdictions")

**Technical Approach**:
- Rule engine configuration files (JSON) per jurisdiction
- LLM prompt includes jurisdiction context
- Fatwa search filtered by jurisdiction preference

---

#### FR-3.4: Human-in-the-Loop (HITL) Workflow
**Description**: Balance automation with mandatory human oversight for high-stakes decisions.

**Decision Tiers** (per Chapter 6 best practices):

| Tier | Risk Level | AI Role | Human Role | Example |
|------|-----------|---------|------------|---------|
| **Tier 1** | Low | Auto-approve | Spot-check audit (10% sample) | Standard Murabaha <$10K, no violations found |
| **Tier 2** | Medium | Recommend | Human approves | Murabaha $100K-$1M, minor ambiguity flagged |
| **Tier 3** | High | Assist research | Human decides | Novel sukuk structure, critical riba violation, >$10M |

**Acceptance Criteria**:
- ✅ System auto-classifies contract into tier based on:
  - Contract value
  - Number/severity of violations
  - Novelty score (no similar template in database)

- ✅ Tier 1: Auto-generate approval report, email to scholar weekly
- ✅ Tier 2: Email immediate notification, require explicit approve/reject
- ✅ Tier 3: Lock system (no auto-decision), require full scholar review + written rationale

---

## 4. Non-Functional Requirements (NFRs)

### NFR-1: Performance
- Contract analysis response time: <60 seconds for 10-page document
- Fatwa search response time: <3 seconds
- System uptime: 99.5% (excluding planned maintenance)
- Concurrent users: Support 50 simultaneous contract reviews

### NFR-2: Accuracy Targets
- Riba detection recall: ≥90% (catch 90% of violations)
- Riba detection precision: ≥85% (false positive rate <15%)
- Clause extraction accuracy: ≥85% match with human annotation
- Fatwa search relevance: Top-3 results contain answer ≥80% of time

### NFR-3: Security & Compliance
- Data encryption at rest (AES-256) and in transit (TLS 1.3)
- GDPR/PDPA compliance (data residency options for Malaysia/EU)
- No training on customer contracts (privacy-preserving)
- API rate limiting (prevent abuse)

### NFR-4: Usability
- First-time user can complete contract review without training (intuitive UI)
- Mobile-responsive web interface (tablet support for scholars)
- Accessibility: WCAG 2.1 AA compliance
- Localization: English and Arabic UI

---

## 5. Out of Scope (Future Phases)

The following are explicitly **not** included in the proof-of-concept:

- ❌ Real-time transaction monitoring (integration with core banking)
- ❌ Zakat calculation automation
- ❌ Portfolio screening (equity investments, sukuk holdings)
- ❌ Fine-tuned Islamic Finance LLM (using general GPT-4 with prompt engineering)
- ❌ Mobile native apps (iOS/Android)
- ❌ Blockchain-based audit trail (using standard PostgreSQL for POC)
- ❌ Multi-madhab support (Hanafi, Maliki, Shafi'i, Hanbali differences)
- ❌ Automated fatwa drafting (scholar retains full authorship)

---

## 6. Success Criteria

The POC is considered successful if it demonstrates:

✅ **Quantitative**:
- 70% faster contract review vs. manual baseline (measured via user study)
- 85%+ accuracy in riba/gharar detection (validated against 50-contract test set)
- 80%+ user satisfaction score (Shariah officers and scholars)
- <5% false positive rate (critical violations flagged incorrectly)

✅ **Qualitative**:
- Shariah scholars express confidence in AI-assisted decisions
- System produces audit-ready reports accepted by regulators
- Demonstrates clear path to production deployment

---

## 7. Assumptions & Dependencies

**Assumptions**:
- Users have basic understanding of Islamic finance contracts
- Contracts are in Arabic, English, or mixed (no other languages)
- AAOIFI standards remain stable during POC (no major updates)
- Internet connectivity available (cloud-based LLM APIs)

**Dependencies**:
- OpenAI GPT-4 API access and stability
- AAOIFI Shariah Standards database (licensed or public domain)
- Sample contract dataset (anonymized from partner institutions)
- Shariah scholar availability for validation and feedback

---

## 8. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-17 | Alan Young | Initial version - brainstorming phase complete |

---

**Next Steps**: Proceed to Product Requirements Document (PRD) and System Architecture design.
