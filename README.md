# Paytm FinTech Analytics & AI Platform — Executive Certification Capstone

One connected platform, three internally-linked parts, submitted as a single repository, per the capstone brief. All monetary figures are in **INR**. No real Paytm data is used anywhere — every dataset is synthetic and generated locally with a fixed random seed.

| Part | Folder | Marks | Status |
|---|---|---|---|
| 1 — Payments & Fraud Analytics | [`/payments_fraud_analytics`](./payments_fraud_analytics) | 35 | ✅ complete |
| 2 — Credit-Risk Lending ML | [`/credit_risk_lending_ml`](./credit_risk_lending_ml) | 40 | ✅ complete |
| 3 — AI Advisory & Blockchain | [`/ai_advisory_blockchain`](./ai_advisory_blockchain) | 25 | ✅ complete |
| **Total** | | **100** | **All 3 parts complete** |

## Repo layout

```
.
├── README.md                      ← this file
├── payments_fraud_analytics/      ← Part 1 (Excel + SQL + Python reconciliation + dashboard)
├── credit_risk_lending_ml/        ← Part 2 (credit-risk ML pipeline)
└── ai_advisory_blockchain/        ← Part 3 (AI-augmented advisory + blockchain/crypto risk appendix)
```

## Setup

Each part ships its own `requirements.txt` (stated per-part below — this project uses **one consolidated top-level approach is NOT used**; each part is self-contained so it can be graded independently).

```bash
# Part 1
cd payments_fraud_analytics
pip install -r requirements.txt
python generate_data.py        # must be run with this folder as the working directory

# Part 2
cd ../credit_risk_lending_ml
pip install -r requirements.txt
python generate_data.py        # must be run with this folder as the working directory

# Part 3
cd ../ai_advisory_blockchain
pip install -r requirements.txt
```

> **Note on seed-data scripts:** `generate_data.py` in Part 1 and Part 2 write their output CSVs via relative paths, so each must be run with its own part folder as the working directory (e.g. `cd payments_fraud_analytics && python generate_data.py`). Do not run either script from the repository root.

## Design decisions

_(To be filled in as each part is built — one short subsection per part, summarizing key choices such as classification cutoffs, fee-tier assumptions, chart choices, and modeling decisions.)_

### Part 1 — Payments & Fraud Analytics
- **GMV** = sum of `amount_inr` across all transactions regardless of status ("value processed" reading, since the brief doesn't pin down the definition).
- **High-Value Merchant Day**: merchant's same-calendar-day total > ₹5,000 **and** region ≠ "East".
- **Pivot table**: built as live SUMIFS/COUNTIFS formulas rather than a native Excel PivotTable object, so values recalculate and can be verified from the file directly (see part README for the full rationale).
- **Velocity-attack detection**: grouped by `user_id` + a floored 10-minute time bucket, per the brief's grading clarification.
- Full design-decision log with verification details: [`payments_fraud_analytics/README.md`](./payments_fraud_analytics/README.md).

### Part 2 — Credit-Risk Lending ML
- **Preprocessing order matters and is verified leak-free**: `is_thin_file` engineered before the split; train/test split first; median imputation and `StandardScaler` both fit on the training split only (independently re-derived and confirmed identical).
- **Winner: Logistic Regression** (ROC AUC 0.719 vs. Decision Tree's near-random 0.531) — see full comparison table and recommendation in the part README.
- **Risk-pricing tiers** (quartiles of predicted default probability) show a clean monotonic actual-default-rate progression: 8% → 12% → 20% → 40%.
- **Isolation Forest** anomaly recall: 11/15 (73.3%) of seeded fraud-like transactions.
- Full design-decision log, bias-awareness note, and final recommendation: [`credit_risk_lending_ml/README.md`](./credit_risk_lending_ml/README.md).

### Part 3 — AI Advisory & Blockchain
- **Agent design verified against the brief's own expected numbers**: independently re-derived the CAPM/portfolio-variance formula before coding it, and matched the stated 8.44% / 12.57% / 20.58% std-dev values exactly; escalation fires correctly only for the two Aggressive investors.
- **DCF self-check passes**: worst-case sensitivity-grid WACC − terminal growth = 4.60pp (≥1pp required).
- **MOCK_LLM=1 (deterministic, keyless) is the graded path** for all 4 scripts — no network calls, no API keys needed to run this part.
- One data gap flagged: **INV05's exact horizon/investment-amount weren't visible in the uploaded brief** (risk_tolerance is confirmed as Aggressive from the acceptance criteria); placeholder values used since neither field affects any graded computation. See part README for details.
- Full design-decision log and run transcripts: [`ai_advisory_blockchain/README.md`](./ai_advisory_blockchain/README.md).

## Git workflow

Optional, unscored: a feature-branch workflow (branch → ≥2 commits → merge to `main`) may be used as general engineering practice. No `grader_rubric.md` marks depend on it.
