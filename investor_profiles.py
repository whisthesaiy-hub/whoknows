"""
Investor profiles for Part 3's advisory agent.

NOTE on INV05: the source brief's screenshot was cut off before INV05's exact
horizon_years / investment_amount_inr values. risk_tolerance="Aggressive" is
confirmed by the brief's acceptance criteria ("Aggressive (INV03, INV05, ~20.58%
std dev) must escalate"). horizon_years and investment_amount_inr below are
therefore illustrative placeholders -- neither field is used in any graded
computation (CAPM return, portfolio variance, and the escalation flag depend only
on risk_tolerance, via the prescribed allocation table, and on STOCK_UNIVERSE).
If you have the original exact values for INV05, replace them here.
"""

INVESTOR_PROFILES = [
    {"investor_id": "INV01", "risk_tolerance": "Conservative", "horizon_years": 3,  "investment_amount_inr": 200000},
    {"investor_id": "INV02", "risk_tolerance": "Moderate",      "horizon_years": 7,  "investment_amount_inr": 500000},
    {"investor_id": "INV03", "risk_tolerance": "Aggressive",    "horizon_years": 12, "investment_amount_inr": 300000},
    {"investor_id": "INV04", "risk_tolerance": "Moderate",      "horizon_years": 5,  "investment_amount_inr": 800000},
    {"investor_id": "INV05", "risk_tolerance": "Aggressive",    "horizon_years": 15, "investment_amount_inr": 400000},  # placeholder horizon/amount, see note above
]
