"""
Part C — Multi-agent debate demo.

3-agent debate (bull, bear, synthesizer) for one ticker from STOCK_UNIVERSE.
Mock mode (graded baseline): each agent's argument is built from a template
referencing that ticker's actual beta/analyst_expected_return/std_dev -- no LLM call.

Run from this folder:
    python debate.py
"""
import os
import json
from stock_universe import STOCK_UNIVERSE

MOCK_LLM = os.environ.get("MOCK_LLM", "1") != "0"

TICKER = "PAYTECH"  # chosen ticker for this debate demo


def bull_agent(ticker: str, data: dict) -> str:
    if MOCK_LLM:
        return (
            f"With an expected return of {data['analyst_expected_return']:.1%} against a "
            f"beta of {data['beta']:.2f}, this offers attractive risk-adjusted upside."
        )
    raise NotImplementedError("MOCK_LLM=0 is an optional, ungraded extension.")


def bear_agent(ticker: str, data: dict) -> str:
    if MOCK_LLM:
        return (
            f"{ticker}'s standard deviation of {data['std_dev']:.1%} is the highest in "
            f"the universe, and its beta of {data['beta']:.2f} means it will amplify "
            f"any market downturn -- this is a high-volatility bet, not a stable holding."
        )
    raise NotImplementedError("MOCK_LLM=0 is an optional, ungraded extension.")


def synthesizer_agent(ticker: str, bull_arg: str, bear_arg: str, data: dict) -> str:
    if MOCK_LLM:
        return (
            f"{ticker} combines the highest expected return in the universe "
            f"({data['analyst_expected_return']:.1%}) with its highest risk "
            f"(std dev {data['std_dev']:.1%}, beta {data['beta']:.2f}). It suits "
            f"Aggressive-risk-tolerance investors with a long horizon who can absorb "
            f"drawdowns, but is a poor fit for Conservative or Moderate profiles."
        )
    raise NotImplementedError("MOCK_LLM=0 is an optional, ungraded extension.")


if __name__ == "__main__":
    print(f"MOCK_LLM mode: {MOCK_LLM} (graded baseline is MOCK_LLM=1 / unset)")
    print(f"Ticker: {TICKER}\n")

    data = STOCK_UNIVERSE[TICKER]
    bull_arg = bull_agent(TICKER, data)
    bear_arg = bear_agent(TICKER, data)
    synthesis = synthesizer_agent(TICKER, bull_arg, bear_arg, data)

    print(f"BULL: {bull_arg}\n")
    print(f"BEAR: {bear_arg}\n")
    print(f"SYNTHESIZER: {synthesis}\n")

    with open("debate_output.json", "w") as f:
        json.dump({
            "ticker": TICKER, "stock_data": data,
            "bull": bull_arg, "bear": bear_arg, "synthesizer": synthesis,
        }, f, indent=2)
    print("Wrote debate_output.json")
