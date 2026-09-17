# Shariah Compliance Copilot — Demo UX & Visual Design

**Purpose:** A stakeholder-ready front-end prototype for Capco’s Islamic finance AI demonstration.

## The Demonstrated Story

The product is a decision workspace for a Shariah Compliance Officer. It makes the result of an AI-assisted contract analysis legible, inspectable, and safe to use in a regulated setting.

The primary demo is the non-compliant QuickCash personal-financing agreement described in the test-data design. It produces a Tier 3 result: the system has identified critical riba indicators, but does not issue a ruling or reject the contract. The user sees evidence, standards references, a remediation path, and an explicit handoff to a qualified scholar.

This preserves the product’s core premise: AI accelerates routine evidence work while Shariah scholars retain decision authority.

## Information Architecture

| Surface | User need | Demo behavior |
| --- | --- | --- |
| Contract header | Establish the document, framework, and next action | Shows source file, AAOIFI framework, export action, and scholar-review request |
| Determination band | Understand the current risk level within seconds | Shows Tier 3, six riba findings, two gharar risks, 15 extracted clauses, and confidence |
| Findings | Move from risk summary to source evidence | Select a finding to reveal clause text, AAOIFI reference, confidence, and remediation |
| Extracted clauses | Validate the AI’s structured reading of the contract | Presents the relevant provisions in a compact review table |
| Related guidance | Research the applicable precedent | Shows contextual AAOIFI standards matched to the analysis |
| Audit state | Make governance visible | Confirms that the model, evidence, and scholar decision are retained |

## Primary Interaction Flow

```mermaid
flowchart LR
  A[Contract uploaded] --> B[AI extracts clauses and flags risks]
  B --> C[Decision workspace]
  C --> D[Inspect finding evidence]
  D --> E[Review AAOIFI reference and remediation]
  E --> F[Request scholar review]
  F --> G[Decision recorded in audit trail]
```

## Visual Direction

The interface takes its cues from Capco’s public site without imitating a marketing page: dark graphite navigation, a restrained red action color, high-contrast editorial typography, thin structural rules, and generous empty space.

| Token | Value | Intent |
| --- | --- | --- |
| Ink | `#101011` | Global navigation and decision summary band |
| Paper | `#F7F7F4` | Primary workspace background |
| White | `#FFFFFF` | Evidence surfaces, making source detail feel distinct |
| Signal red | `#CF2028` | Critical risk, active selection, decisive action only |
| Amber | `#D58B1F` | High-risk issue marker |
| Governance green | `#4D8768` | Confidence and successful handoff state |
| Body/UI | DM Sans | Clear operational text and controls |
| Editorial/headline | Libre Baskerville | Review headings and decision labels |
| Metadata | DM Mono | Framework labels, IDs, confidence, and audit detail |

## Component Rules

**Navigation:** The main bar is dark and quiet. It carries only the product identity, top-level areas, utility controls, and user identity. Mobile navigation collapses behind a menu control.

**Determination band:** A single dark strip separates decision context from work. It starts with the human-authority message, moves through objective counts, and closes with the decision tier. It never presents a compliance “pass” as an autonomous AI decision.

**Finding rows:** Each row uses an initial marker (`R` or `G`), a text severity label, a source ID, title, and clause location. Selection is signalled by a red left rule and quiet grey fill, avoiding alarm fatigue.

**Evidence panel:** The selected finding retains generous reading space. Source text is isolated in a paper-like quote block, followed by a specific standard citation and a concrete remediation. The evidence panel is white to distinguish original decision material from browsing context.

**Actions:** The red filled action is reserved for the governance handoff. Secondary actions are outlined or plain text. This keeps the hierarchy clear and aligns visual emphasis with the human-in-the-loop workflow.

## Responsive Rules

At desktop widths, the workspace uses a fixed analysis rail and a two-column findings/evidence view. At tablet widths, analysis navigation becomes a horizontal rail. On mobile, the decision summary stacks; primary actions remain readable; finding evidence follows the selected row in one column; tables transform into labelled vertical records.

## Accessibility and Content Rules

- Every decision signal combines color, text, and icon treatment.
- Controls are native buttons or inputs with descriptive labels.
- The visual hierarchy follows heading order: page title, view title, finding title.
- AI language is intentionally qualified: “potential,” “preliminary,” “confidence,” and “recommended next step.”
- The footer repeats the product’s governance rule: qualified scholars retain final authority.

## Demo Coverage and Deliberate Boundaries

The front-end prototype covers the POC’s main review flow with realistic data. It does not make live OCR, LLM calls, document export, authentication, or persistent audit storage. Those need the FastAPI services defined in the architecture document before a production deployment.
