"""
lbo.py
------
Simplified LBO (Leveraged Buyout) Returns Estimator.

Υπολογίζει IRR και MOIC για ένα υποθετικό PE buyout.

Λογική:
1. Αγορά εταιρείας σε Entry EV/EBITDA multiple
2. Χρηματοδότηση με mix Debt + Equity
3. Ανάπτυξη EBITDA για N χρόνια
4. Πώληση σε Exit EV/EBITDA multiple
5. Αποπληρωμή debt → υπόλοιπο = equity proceeds
6. Υπολογισμός IRR και MOIC
"""

import numpy as np


def run_lbo(
    ebitda: float,          # Αρχικό EBITDA (σε $M)
    entry_multiple: float,  # EV/EBITDA κατά την αγορά
    debt_pct: float,        # % του EV που χρηματοδοτείται με debt (0-1)
    interest_rate: float,   # Επιτόκιο debt (π.χ. 0.07 = 7%)
    ebitda_cagr: float,     # Ετήσια αύξηση EBITDA (π.χ. 0.08 = 8%)
    exit_multiple: float,   # EV/EBITDA κατά την πώληση
    hold_years: int,        # Χρόνια κατοχής (συνήθως 3-7)
    debt_paydown_pct: float # % του FCF που πηγαίνει σε αποπληρωμή debt (0-1)
) -> dict:
    """
    Εκτελεί το LBO model και επιστρέφει τα αποτελέσματα.
    """

    # ── Entry ─────────────────────────────────────────────────────────────
    entry_ev     = ebitda * entry_multiple          # Enterprise Value κατά είσοδο
    entry_debt   = entry_ev * debt_pct              # Αρχικό debt
    entry_equity = entry_ev * (1 - debt_pct)        # Equity που βάζει το fund

    # ── Projection ────────────────────────────────────────────────────────
    years       = list(range(hold_years + 1))
    ebitda_proj = [ebitda * (1 + ebitda_cagr) ** y for y in years]

    # Απλοποιημένο debt paydown: κάθε χρόνο πληρώνεται τόκος + μέρος κεφαλαίου
    # FCF ≈ EBITDA * 0.5 (rough estimate μετά από capex, taxes, interest)
    debt_schedule = [entry_debt]
    for y in range(1, hold_years + 1):
        fcf          = ebitda_proj[y] * 0.5
        paydown      = fcf * debt_paydown_pct
        new_debt     = max(0, debt_schedule[-1] - paydown)
        debt_schedule.append(new_debt)

    # ── Exit ──────────────────────────────────────────────────────────────
    exit_ebitda  = ebitda_proj[hold_years]
    exit_ev      = exit_ebitda * exit_multiple
    exit_debt    = debt_schedule[hold_years]
    exit_equity  = max(0, exit_ev - exit_debt)      # Equity proceeds

    # ── Returns ───────────────────────────────────────────────────────────
    moic = exit_equity / entry_equity if entry_equity > 0 else 0

    # IRR: solve για r ώστε NPV = 0
    # Cash flows: -equity_in at t=0, +equity_out at t=hold_years
    cash_flows = [-entry_equity] + [0] * (hold_years - 1) + [exit_equity]
    try:
        irr = np.irr(cash_flows) if hasattr(np, 'irr') else _calc_irr(cash_flows)
    except Exception:
        irr = _calc_irr(cash_flows)

    return {
        # Entry
        "entry_ev":        entry_ev,
        "entry_debt":      entry_debt,
        "entry_equity":    entry_equity,
        # Exit
        "exit_ev":         exit_ev,
        "exit_ebitda":     exit_ebitda,
        "exit_debt":       exit_debt,
        "exit_equity":     exit_equity,
        # Returns
        "moic":            round(moic, 2),
        "irr":             round(irr * 100, 1) if irr else 0,
        # Schedules (για charts)
        "years":           years,
        "ebitda_proj":     [round(e, 1) for e in ebitda_proj],
        "debt_schedule":   [round(d, 1) for d in debt_schedule],
        "equity_schedule": [round(max(0, ebitda_proj[y] * exit_multiple - debt_schedule[y]), 1)
                            for y in years],
    }


def _calc_irr(cash_flows: list) -> float:
    """
    Newton-Raphson IRR solver (fallback αν numpy.irr δεν υπάρχει).
    """
    rate = 0.20  # initial guess
    for _ in range(1000):
        npv  = sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
        dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cash_flows))
        if abs(dnpv) < 1e-10:
            break
        rate -= npv / dnpv
        if rate <= -1:
            rate = -0.999
    return rate


def irr_rating(irr: float) -> str:
    if irr >= 30:
        return "🟢 Excellent (Top Quartile)"
    elif irr >= 20:
        return "🟡 Good (Meets Hurdle)"
    elif irr >= 15:
        return "🟠 Marginal (Below Target)"
    else:
        return "🔴 Poor (Destroy Value)"


def moic_rating(moic: float) -> str:
    if moic >= 3.0:
        return "🟢 3x+ (Home Run)"
    elif moic >= 2.0:
        return "🟡 2-3x (Solid)"
    elif moic >= 1.5:
        return "🟠 1.5-2x (Mediocre)"
    else:
        return "🔴 <1.5x (Disappointing)"
