"""
Part D — DCF valuation calculator for a hypothetical Paytm business line.

All monetary figures are in INR (stated in Rs. crore for readability; 1 crore =
10,000,000 INR). This is a hypothetical business line ("Paytm Merchant Lending &
Postpaid"), not real Paytm financials.

Run from this folder:
    python dcf_calculator.py
"""
import json
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

CRORE = 1e7  # 1 crore = 10,000,000 INR

# ---------------------------------------------------------------- stated inputs (illustrative)
# Base-year (Year 0) financials for the hypothetical business line, in Rs. crore.
EBIT_Y0_CR = 120.0
TAX_RATE = 0.25
DA_Y0_CR = 30.0
CAPEX_Y0_CR = 45.0
DELTA_NWC_Y0_CR = 10.0

# Unlevered FCFF = EBIT * (1 - tax_rate) + D&A - CapEx - Delta NWC
FCFF_Y0_CR = EBIT_Y0_CR * (1 - TAX_RATE) + DA_Y0_CR - CAPEX_Y0_CR - DELTA_NWC_Y0_CR

# 5-year growth schedule that fades toward the terminal growth rate (stated, illustrative)
GROWTH_SCHEDULE = [0.18, 0.16, 0.14, 0.12, 0.10]  # Year 1..Year 5 FCFF growth
TERMINAL_GROWTH = 0.06

# --- WACC ---
# Cost of equity via CAPM, using PAYFIN's beta (chosen as the closest thematic match
# in STOCK_UNIVERSE to a financial-services/lending business line).
COST_OF_EQUITY_BETA_TICKER = "PAYFIN"
beta = STOCK_UNIVERSE[COST_OF_EQUITY_BETA_TICKER]["beta"]
cost_of_equity = RISK_FREE_RATE + beta * (MARKET_RETURN - RISK_FREE_RATE)

# Illustrative after-tax cost of debt and capital-structure weights (stated assumptions).
PRETAX_COST_OF_DEBT = 0.09
AFTER_TAX_COST_OF_DEBT = PRETAX_COST_OF_DEBT * (1 - TAX_RATE)
WEIGHT_EQUITY = 0.70
WEIGHT_DEBT = 0.30

WACC = WEIGHT_EQUITY * cost_of_equity + WEIGHT_DEBT * AFTER_TAX_COST_OF_DEBT

# --- terminal-growth constraint self-check (required before submitting) ---
MIN_GAP_PP = 3.0  # terminal growth must be >= 3 percentage points below base-case WACC
assert (WACC - TERMINAL_GROWTH) * 100 >= MIN_GAP_PP, "terminal growth too close to base WACC"


def project_fcff(fcff_y0, growth_schedule):
    fcff = [fcff_y0]
    for g in growth_schedule:
        fcff.append(fcff[-1] * (1 + g))
    return fcff[1:]  # Year 1..Year 5, drop Year 0


def dcf_value(fcff_y0, growth_schedule, wacc, terminal_growth):
    """Returns (enterprise_value_cr, projected_fcff_list, terminal_value_cr, pv_terminal_cr, pv_fcff_cr)"""
    projected = project_fcff(fcff_y0, growth_schedule)
    pv_fcff = [cf / ((1 + wacc) ** (i + 1)) for i, cf in enumerate(projected)]
    terminal_value = projected[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / ((1 + wacc) ** len(projected))
    ev = sum(pv_fcff) + pv_terminal
    return ev, projected, terminal_value, pv_terminal, pv_fcff


base_ev_cr, base_projected, base_tv_cr, base_pv_tv_cr, base_pv_fcff_cr = dcf_value(
    FCFF_Y0_CR, GROWTH_SCHEDULE, WACC, TERMINAL_GROWTH
)

# ---------------------------------------------------------------- 3x3 sensitivity table
wacc_deltas = [-0.01, 0.0, 0.01]
growth_deltas = [-0.01, 0.0, 0.01]
sensitivity = []
worst_case_gap_pp = None
for dw in wacc_deltas:
    row = []
    for dg in growth_deltas:
        w = WACC + dw
        g = TERMINAL_GROWTH + dg
        gap_pp = (w - g) * 100
        if worst_case_gap_pp is None or gap_pp < worst_case_gap_pp:
            worst_case_gap_pp = gap_pp
        ev_cell, *_ = dcf_value(FCFF_Y0_CR, GROWTH_SCHEDULE, w, g)
        row.append({"wacc": w, "terminal_growth": g, "ev_cr": ev_cell, "wacc_minus_growth_pp": gap_pp})
    sensitivity.append(row)

assert worst_case_gap_pp >= 1.0, (
    f"Required self-check failed: WACC - terminal_growth = {worst_case_gap_pp:.2f}pp "
    f"in the worst-case sensitivity cell, must be >= 1pp"
)

# ---------------------------------------------------------------- EV/EBITDA cross-check
EBITDA_Y0_CR = EBIT_Y0_CR + DA_Y0_CR  # illustrative base-year EBITDA
EV_EBITDA_MULTIPLE = 14.0  # illustrative multiple (stated assumption, fintech/payments comp)
ev_multiple_cr = EBITDA_Y0_CR * EV_EBITDA_MULTIPLE

if __name__ == "__main__":
    print("=== Inputs ===")
    print(f"FCFF Year 0: Rs. {FCFF_Y0_CR:.2f} crore "
          f"(= {EBIT_Y0_CR}*(1-{TAX_RATE}) + {DA_Y0_CR} - {CAPEX_Y0_CR} - {DELTA_NWC_Y0_CR})")
    print(f"Growth schedule (Y1-Y5): {[f'{g:.0%}' for g in GROWTH_SCHEDULE]}, terminal: {TERMINAL_GROWTH:.1%}")
    print(f"Cost of equity (CAPM, beta={beta} from {COST_OF_EQUITY_BETA_TICKER}): {cost_of_equity:.4%}")
    print(f"After-tax cost of debt: {AFTER_TAX_COST_OF_DEBT:.4%} (pre-tax {PRETAX_COST_OF_DEBT:.1%})")
    print(f"Capital structure: {WEIGHT_EQUITY:.0%} equity / {WEIGHT_DEBT:.0%} debt")
    print(f"WACC: {WACC:.4%}")
    print(f"Terminal growth: {TERMINAL_GROWTH:.1%}  (gap to base WACC: {(WACC-TERMINAL_GROWTH)*100:.2f}pp, "
          f"required >= {MIN_GAP_PP}pp)")

    print("\n=== 5-year FCFF projection (Rs. crore) ===")
    for i, cf in enumerate(base_projected, start=1):
        print(f"  Year {i}: {cf:.2f}")

    print(f"\nTerminal value (end of Year 5): Rs. {base_tv_cr:.2f} crore")
    print(f"PV of terminal value: Rs. {base_pv_tv_cr:.2f} crore")
    print(f"PV of 5-year FCFF: Rs. {sum(base_pv_fcff_cr):.2f} crore")
    print(f"Enterprise Value (DCF): Rs. {base_ev_cr:.2f} crore (Rs. {base_ev_cr*CRORE:,.0f})")

    print("\n=== 3x3 sensitivity table (Enterprise Value, Rs. crore) ===")
    header = "WACC \\ terminal_g".ljust(20) + "".join(
        f"{TERMINAL_GROWTH+dg:.1%}".rjust(12) for dg in growth_deltas)
    print(header)
    for i, dw in enumerate(wacc_deltas):
        row_label = f"{WACC+dw:.2%}".ljust(20)
        row_vals = "".join(f"{sensitivity[i][j]['ev_cr']:.1f}".rjust(12) for j in range(3))
        print(row_label + row_vals)

    print(f"\nSelf-check: worst-case WACC - terminal_growth = {worst_case_gap_pp:.2f}pp "
          f"(required >= 1pp) -- {'PASS' if worst_case_gap_pp >= 1.0 else 'FAIL'}")

    print("\n=== EV/EBITDA cross-check ===")
    print(f"Base-year EBITDA: Rs. {EBITDA_Y0_CR:.2f} crore  (EBIT {EBIT_Y0_CR} + D&A {DA_Y0_CR})")
    print(f"Illustrative multiple: {EV_EBITDA_MULTIPLE}x")
    print(f"EV/EBITDA-implied Enterprise Value: Rs. {ev_multiple_cr:.2f} crore")
    print(f"DCF-implied Enterprise Value: Rs. {base_ev_cr:.2f} crore")
    diff_pct = (base_ev_cr - ev_multiple_cr) / ev_multiple_cr
    print(f"Difference: {diff_pct:+.1%} (DCF vs. multiple)")

    output = {
        "inputs": {
            "fcff_y0_cr": FCFF_Y0_CR, "growth_schedule": GROWTH_SCHEDULE,
            "terminal_growth": TERMINAL_GROWTH, "wacc": WACC, "cost_of_equity": cost_of_equity,
            "after_tax_cost_of_debt": AFTER_TAX_COST_OF_DEBT,
        },
        "projected_fcff_cr": base_projected,
        "terminal_value_cr": base_tv_cr,
        "enterprise_value_dcf_cr": base_ev_cr,
        "ev_ebitda_cross_check": {
            "ebitda_cr": EBITDA_Y0_CR, "multiple": EV_EBITDA_MULTIPLE,
            "ev_multiple_cr": ev_multiple_cr, "diff_pct_vs_dcf": diff_pct,
        },
        "sensitivity_table_ev_cr": [[cell["ev_cr"] for cell in row] for row in sensitivity],
        "worst_case_wacc_minus_growth_pp": worst_case_gap_pp,
    }
    with open("dcf_output.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\nWrote dcf_output.json")
