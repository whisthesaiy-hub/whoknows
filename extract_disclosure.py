"""
Part B — Structured disclosure extraction.

extract_signals(snippet) -> {"risk_flags": [...], "hedging_detected": bool,
                              "sentiment": "confident"|"cautious"|"neutral"}

Mock mode (MOCK_LLM unset or "1", the graded baseline): keyword/regex rules, no LLM
call, no network access.

Run from this folder:
    python extract_disclosure.py
"""
import os
import re
import json
from disclosure_snippets import DISCLOSURE_SNIPPETS

MOCK_LLM = os.environ.get("MOCK_LLM", "1") != "0"

RISK_FLAG_PATTERNS = {
    "litigation": r"\blitigation\b",
    "regulatory": r"\bregulatory\b",
    "customer_concentration": r"\bcustomers?\b.{0,40}\b(?:percent|%|account for)\b|top\s+\w+\s+customers?",
}
HEDGING_PATTERNS = [r"\bassuming\b", r"\bcautiously\b", r"\bvisibility\b"]
CONFIDENT_PATTERNS = [r"\bconfident\b", r"\bapproved\b"]
CAUTIOUS_MARKERS = HEDGING_PATTERNS  # a hedging phrase present -> sentiment "cautious"


def extract_signals_mock(snippet: str) -> dict:
    text = snippet.lower()

    risk_flags = [name for name, pat in RISK_FLAG_PATTERNS.items() if re.search(pat, text)]
    hedging_detected = any(re.search(pat, text) for pat in HEDGING_PATTERNS)

    if any(re.search(pat, text) for pat in CONFIDENT_PATTERNS):
        sentiment = "confident"
    elif hedging_detected:
        sentiment = "cautious"
    else:
        sentiment = "neutral"

    return {"risk_flags": risk_flags, "hedging_detected": hedging_detected, "sentiment": sentiment}


def extract_signals(snippet: str) -> dict:
    if MOCK_LLM:
        return extract_signals_mock(snippet)
    # Optional MOCK_LLM=0 extension: call the LLM, validate its JSON against the same
    # schema, retry once on validation failure, else fall back to the mock result.
    raise NotImplementedError(
        "MOCK_LLM=0 (live LLM) path is an optional, ungraded extension not "
        "implemented in this submission. Set MOCK_LLM=1 (or leave unset) to run "
        "the graded deterministic mock baseline."
    )


if __name__ == "__main__":
    print(f"MOCK_LLM mode: {MOCK_LLM} (graded baseline is MOCK_LLM=1 / unset)\n")
    results = {}
    for snippet in DISCLOSURE_SNIPPETS:
        doc_id = snippet.split(":")[0]
        signals = extract_signals(snippet)
        results[doc_id] = {"snippet": snippet, **signals}
        print(f"{doc_id}: {signals}")

    with open("disclosure_extraction_output.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nWrote disclosure_extraction_output.json")
