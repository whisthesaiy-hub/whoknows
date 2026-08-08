# Part 3 — AI-Augmented FinTech Advisory & Blockchain Risk (25 marks)

**Paytm vertical:** Money / Wealth advisory, plus a blockchain/crypto risk appendix.

A lightweight AI-assisted advisory toolkit built on the **agentic think-act-observe pattern** and
**LLM structured JSON extraction** — no retrieval/vector-database pipeline. All required outputs
are graded with `MOCK_LLM` left at its default (deterministic, keyless, no network call).

## MOCK_LLM mode

Every "LLM reasoning" step in this part is gated behind one environment variable, `MOCK_LLM`.
Left unset (the default used for every transcript below), all four scripts run fully
deterministic, rule-based mock logic — no signup, no API key, no network call. This is what gets
graded. `MOCK_LLM=0` (calling a real LLM, e.g. Groq's free tier) is an optional, ungraded
extension not implemented in this submission.

## Contents

- [x] `stock_universe.py`, `investor_profiles.py`, `disclosure_snippets.py` — seed data, copied
  as specified. **Note on `INV05`**: the source brief's screenshot was cut off before INV05's
  exact `horizon_years`/`investment_amount_inr`. `risk_tolerance="Aggressive"` is confirmed by the
  brief's own acceptance criteria; the two other fields are illustrative placeholders since
  neither is used in any graded computation (only `risk_tolerance`, via the prescribed allocation
  table, and `STOCK_UNIVERSE` drive the CAPM/variance/escalation outputs). Swap in the real values
  if you have the original brief.
- [x] `advisory_agent.py` (Part A) — think/act/observe agent, all 5 investor profiles.
  **Verified**: independently re-derived the CAPM return and portfolio std dev by hand-checked
  formula before writing the script, and matched the brief's stated expected values exactly
  (Conservative 8.44%, Moderate 12.57%, Aggressive 20.58%); escalation fires correctly only for
  INV03/INV05.
- [x] `extract_disclosure.py` (Part B) — `extract_signals()`, run against all 6 snippets.
  **Verified against all 3 stated acceptance checks**: doc_02 flagged `litigation`; doc_01 and
  doc_04 flagged `hedging_detected=True`; doc_05 classified `"confident"`.
- [x] `debate.py` (Part C) — 3-agent bull/bear/synthesizer debate for `PAYTECH` (chosen because it
  has both the highest expected return and highest std dev in the universe, making the bull/bear
  tension concrete).
- [x] `dcf_calculator.py` (Part D) — 5-year unlevered FCFF projection, WACC via CAPM cost of
  equity + illustrative cost of debt, terminal value, 3×3 sensitivity table, EV/EBITDA
  cross-check. **Self-check passes**: worst-case WACC − terminal growth = 4.60pp (≥ 1pp required).
- [x] `blockchain_risk_note.md` (Part E) — 851 words, all three required sections.
- [x] Recorded run transcripts (below and in `*_transcript.txt` / `*_output.json` files).

## How to run

```bash
cd ai_advisory_blockchain
python advisory_agent.py       # -> advisory_agent_output.json
python extract_disclosure.py   # -> disclosure_extraction_output.json
python debate.py                # -> debate_output.json
python dcf_calculator.py        # -> dcf_output.json
```
No `pip install` needed for the graded (`MOCK_LLM=1`/default) path — standard library only.

## Design decisions

- **Allocation table**: implemented exactly as prescribed (Conservative → PAYBOND/PAYGOLD/PAYRETAIL,
  Moderate → PAYRETAIL/PAYINFRA/PAYGOLD, Aggressive → PAYTECH/PAYFIN/PAYINFRA, equal-weighted).
- **CAPM uses `beta` only**, never `analyst_expected_return`, per the brief's explicit instruction
  — the two are expected to differ, which is by design, not a bug.
- **Portfolio variance** uses the full covariance formula with a stated pairwise correlation
  ρ = 0.3 for every pair within a tier's 3-ticker allocation.
- **Escalation threshold**: portfolio std dev > 20% → `ESCALATED_TO_HUMAN_ADVISOR`, computed
  deterministically from the formula above (not hardcoded per investor).
- **Disclosure extraction rules** (mock mode): keyword/regex matches for `litigation`,
  `regulatory`, and customer-concentration phrasing (risk flags); `assuming`/`cautiously`/
  `visibility` (hedging); `confident`/`approved` → sentiment `"confident"`, else hedging present →
  `"cautious"`, else `"neutral"`.
- **DCF ticker for cost of equity**: `PAYFIN` (beta 1.35), chosen as the closest thematic match to
  a lending/financial-services business line among the six fictional tickers.
- **DCF inputs are stated, illustrative assumptions** for a hypothetical "Paytm Merchant Lending &
  Postpaid" business line — not real Paytm financials. All figures in INR (stated in Rs. crore for
  readability).

## Run transcripts (MOCK_LLM left at default)

### Part A — Advisory agent (all 5 investor profiles)
```
MOCK_LLM mode: True (graded baseline is MOCK_LLM=1 / unset)

--- INV01 (Conservative) ---
  Tickers: ['PAYBOND', 'PAYGOLD', 'PAYRETAIL']
  Portfolio expected return: 9.2000%
  Portfolio std dev: 8.4393%
  Escalated: False
  Narrative: For Conservative investor INV01, we recommend an allocation across ['PAYBOND', 'PAYGOLD', 'PAYRETAIL'] with an expected portfolio return of 9.2% and volatility of 8.4%.

--- INV02 (Moderate) ---
  Tickers: ['PAYRETAIL', 'PAYINFRA', 'PAYGOLD']
  Portfolio expected return: 11.3000%
  Portfolio std dev: 12.5707%
  Escalated: False
  Narrative: For Moderate investor INV02, we recommend an allocation across ['PAYRETAIL', 'PAYINFRA', 'PAYGOLD'] with an expected portfolio return of 11.3% and volatility of 12.6%.

--- INV03 (Aggressive) ---
  Tickers: ['PAYTECH', 'PAYFIN', 'PAYINFRA']
  Portfolio expected return: 15.0000%
  Portfolio std dev: 20.5848%
  Escalated: True
  Narrative: ESCALATED_TO_HUMAN_ADVISOR: For Aggressive investor INV03, the computed allocation across ['PAYTECH', 'PAYFIN', 'PAYINFRA'] has an expected portfolio return of 15.0% and volatility of 20.6%, which exceeds the 20% human-review threshold and requires manual sign-off before finalizing.

--- INV04 (Moderate) ---
  Tickers: ['PAYRETAIL', 'PAYINFRA', 'PAYGOLD']
  Portfolio expected return: 11.3000%
  Portfolio std dev: 12.5707%
  Escalated: False
  Narrative: For Moderate investor INV04, we recommend an allocation across ['PAYRETAIL', 'PAYINFRA', 'PAYGOLD'] with an expected portfolio return of 11.3% and volatility of 12.6%.

--- INV05 (Aggressive) ---
  Tickers: ['PAYTECH', 'PAYFIN', 'PAYINFRA']
  Portfolio expected return: 15.0000%
  Portfolio std dev: 20.5848%
  Escalated: True
  Narrative: ESCALATED_TO_HUMAN_ADVISOR: For Aggressive investor INV05, the computed allocation across ['PAYTECH', 'PAYFIN', 'PAYINFRA'] has an expected portfolio return of 15.0% and volatility of 20.6%, which exceeds the 20% human-review threshold and requires manual sign-off before finalizing.
```

### Part B — Disclosure extraction (all 6 snippets)
```
doc_01: {'risk_flags': [], 'hedging_detected': True, 'sentiment': 'cautious'}
doc_02: {'risk_flags': ['litigation'], 'hedging_detected': False, 'sentiment': 'neutral'}
doc_03: {'risk_flags': ['customer_concentration'], 'hedging_detected': False, 'sentiment': 'neutral'}
doc_04: {'risk_flags': [], 'hedging_detected': True, 'sentiment': 'cautious'}
doc_05: {'risk_flags': [], 'hedging_detected': False, 'sentiment': 'confident'}
doc_06: {'risk_flags': ['regulatory'], 'hedging_detected': False, 'sentiment': 'neutral'}
```

### Part C — Debate demo (PAYTECH)
```
BULL: With an expected return of 19.0% against a beta of 1.55, this offers attractive risk-adjusted upside.

BEAR: PAYTECH's standard deviation of 34.0% is the highest in the universe, and its beta of 1.55 means it will amplify any market downturn -- this is a high-volatility bet, not a stable holding.

SYNTHESIZER: PAYTECH combines the highest expected return in the universe (19.0%) with its highest risk (std dev 34.0%, beta 1.55). It suits Aggressive-risk-tolerance investors with a long horizon who can absorb drawdowns, but is a poor fit for Conservative or Moderate profiles.
```

### Part D — DCF calculator
```
=== Inputs ===
FCFF Year 0: Rs. 65.00 crore (= 120.0*(1-0.25) + 30.0 - 45.0 - 10.0)
Growth schedule (Y1-Y5): ['18%', '16%', '14%', '12%', '10%'], terminal: 6.0%
Cost of equity (CAPM, beta=1.35 from PAYFIN): 15.1000%
After-tax cost of debt: 6.7500% (pre-tax 9.0%)
Capital structure: 70% equity / 30% debt
WACC: 12.5950%
Terminal growth: 6.0%  (gap to base WACC: 6.60pp, required >= 3.0pp)

=== 5-year FCFF projection (Rs. crore) ===
  Year 1: 76.70
  Year 2: 88.97
  Year 3: 101.43
  Year 4: 113.60
  Year 5: 124.96

Terminal value (end of Year 5): Rs. 2008.45 crore
PV of terminal value: Rs. 1109.85 crore
PV of 5-year FCFF: Rs. 349.09 crore
Enterprise Value (DCF): Rs. 1458.94 crore (Rs. 14,589,390,593)

=== 3x3 sensitivity table (Enterprise Value, Rs. crore) ===
WACC \ terminal_g           5.0%        6.0%        7.0%
11.60%                    1508.1      1726.5      2039.9
12.60%                    1303.7      1458.9      1669.6
13.60%                    1147.0      1262.0      1411.8

Self-check: worst-case WACC - terminal_growth = 4.60pp (required >= 1pp) -- PASS

=== EV/EBITDA cross-check ===
Base-year EBITDA: Rs. 150.00 crore  (EBIT 120.0 + D&A 30.0)
Illustrative multiple: 14.0x
EV/EBITDA-implied Enterprise Value: Rs. 2100.00 crore
DCF-implied Enterprise Value: Rs. 1458.94 crore
Difference: -30.5% (DCF vs. multiple)
```

**DCF vs. EV/EBITDA comparison (required 2–3 sentence comment):** The DCF-implied enterprise
value (Rs. 1,459 crore) sits about 30% below the EV/EBITDA-multiple estimate (Rs. 2,100 crore).
This gap is expected: the DCF only credits value the fading 18%→10%→6% growth schedule and chosen
WACC actually discount to present value, while a flat 14x EBITDA multiple implicitly assumes the
business sustains something closer to peer-average growth and margins indefinitely rather than
decelerating. The two methods bracket a reasonable valuation range (~Rs. 1,460–2,100 crore) rather
than converging on a single number, which is the expected and useful outcome of cross-checking a
bottom-up DCF against a top-down comparable multiple.
