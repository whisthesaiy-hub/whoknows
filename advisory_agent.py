"""
Part A — Portfolio advisory agent (agentic think-act-observe pattern).

Implements a 3-stage agent loop per investor profile:
  THINK   - read the investor's risk_tolerance, look up the prescribed allocation.
  ACT     - call get_stock_data(ticker) (a "tool call") for each ticker in the allocation.
  OBSERVE - compute CAPM expected return (beta only) and portfolio variance/std dev;
            decide whether to escalate to a human advisor (std dev > 20%) or finalize.

The final narrative sentence is the ONLY part gated by MOCK_LLM. Left unset (or
MOCK_LLM=1, the default and the graded baseline), the sentence is built from a
deterministic f-string template -- no network call, no LLM.

Run from this folder:
    python advisory_agent.py
"""
import os
import math
import json
from investor_profiles import INVESTOR_PROFILES
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

MOCK_LLM = os.environ.get("MOCK_LLM", "1") != "0"  # unset or "1" -> mock (graded baseline)

# --- THINK: the required, prescribed lookup table (not a free-choice mapping) ---
ALLOCATION_TABLE = {
    "Conservative": ["PAYBOND", "PAYGOLD", "PAYRETAIL"],
    "Moderate": ["PAYRETAIL", "PAYINFRA", "PAYGOLD"],
    "Aggressive": ["PAYTECH", "PAYFIN", "PAYINFRA"],
}
CORRELATION_RHO = 0.3
ESCALATION_STD_THRESHOLD = 0.20  # 20%


def think(investor: dict) -> list:
    """Read the investor profile and determine its allocation via the prescribed table."""
    return ALLOCATION_TABLE[investor["risk_tolerance"]]


def get_stock_data(ticker: str) -> dict:
    """
    ACT (tool call): looks up beta / analyst_expected_return / std_dev from
    STOCK_UNIVERSE for a ticker. Simulates an external-API tool call; no real API
    is needed since the reference data is local.
    """
    return STOCK_UNIVERSE[ticker]


def observe_and_decide(tickers: list) -> dict:
    """
    OBSERVE -> decide: equal-weight (1/3 each) across the prescribed tickers.
    - CAPM expected return per stock: E(R) = R_f + beta * (E(R_m) - R_f), using ONLY
      beta (never analyst_expected_return), then weight-averaged across the 3 tickers.
    - Portfolio variance: Var(R_p) = sum(w_i^2 * sigma_i^2) + 2 * sum_{i<j} w_i*w_j*Cov(R_i,R_j)
      with Cov(R_i,R_j) = rho * sigma_i * sigma_j, rho = 0.3 for every pair.
    - Human-in-the-loop escalation: if portfolio std dev > 20%, do not finalize --
      flag ESCALATED_TO_HUMAN_ADVISOR with the computed numbers attached.
    """
    n = len(tickers)
    w = 1 / n
    stock_data = {t: get_stock_data(t) for t in tickers}  # ACT stage, tool calls

    capm_returns = {
        t: RISK_FREE_RATE + stock_data[t]["beta"] * (MARKET_RETURN - RISK_FREE_RATE)
        for t in tickers
    }
    portfolio_return = sum(w * r for r in capm_returns.values())

    variance = sum((w ** 2) * (stock_data[t]["std_dev"] ** 2) for t in tickers)
    for i in range(n):
        for j in range(i + 1, n):
            si, sj = stock_data[tickers[i]]["std_dev"], stock_data[tickers[j]]["std_dev"]
            cov_ij = CORRELATION_RHO * si * sj
            variance += 2 * w * w * cov_ij
    portfolio_std = math.sqrt(variance)

    escalate = portfolio_std > ESCALATION_STD_THRESHOLD

    return {
        "tickers": tickers,
        "weights": {t: w for t in tickers},
        "per_stock_capm_return": capm_returns,
        "portfolio_expected_return": portfolio_return,
        "portfolio_variance": variance,
        "portfolio_std_dev": portfolio_std,
        "escalated_to_human_advisor": escalate,
    }


def build_narrative(investor: dict, decision: dict) -> str:
    """The only MOCK_LLM-gated part. Mock (graded baseline): deterministic f-string."""
    if MOCK_LLM:
        if decision["escalated_to_human_advisor"]:
            return (
                f"ESCALATED_TO_HUMAN_ADVISOR: For {investor['risk_tolerance']} investor "
                f"{investor['investor_id']}, the computed allocation across "
                f"{decision['tickers']} has an expected portfolio return of "
                f"{decision['portfolio_expected_return']:.1%} and volatility of "
                f"{decision['portfolio_std_dev']:.1%}, which exceeds the 20% human-review "
                f"threshold and requires manual sign-off before finalizing."
            )
        return (
            f"For {investor['risk_tolerance']} investor {investor['investor_id']}, we "
            f"recommend an allocation across {decision['tickers']} with an expected "
            f"portfolio return of {decision['portfolio_expected_return']:.1%} and "
            f"volatility of {decision['portfolio_std_dev']:.1%}."
        )
    else:
        # Optional MOCK_LLM=0 extension: would call an LLM to phrase the same numbers
        # more naturally here. Not exercised in the graded baseline.
        raise NotImplementedError(
            "MOCK_LLM=0 (live LLM) path is an optional, ungraded extension not "
            "implemented in this submission. Set MOCK_LLM=1 (or leave unset) to run "
            "the graded deterministic mock baseline."
        )


def run_agent(investor: dict) -> dict:
    tickers = think(investor)                         # THINK
    decision = observe_and_decide(tickers)             # ACT (inside) + OBSERVE/decide
    narrative = build_narrative(investor, decision)     # MOCK_LLM-gated narrative only
    return {
        "investor_id": investor["investor_id"],
        "risk_tolerance": investor["risk_tolerance"],
        **decision,
        "narrative": narrative,
    }


if __name__ == "__main__":
    print(f"MOCK_LLM mode: {MOCK_LLM} (graded baseline is MOCK_LLM=1 / unset)\n")
    results = [run_agent(inv) for inv in INVESTOR_PROFILES]

    for r in results:
        print(f"--- {r['investor_id']} ({r['risk_tolerance']}) ---")
        print(f"  Tickers: {r['tickers']}")
        print(f"  Portfolio expected return: {r['portfolio_expected_return']:.4%}")
        print(f"  Portfolio std dev: {r['portfolio_std_dev']:.4%}")
        print(f"  Escalated: {r['escalated_to_human_advisor']}")
        print(f"  Narrative: {r['narrative']}\n")

    with open("advisory_agent_output.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Wrote advisory_agent_output.json")
