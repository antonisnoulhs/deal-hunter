"""
scorer.py
---------
Scoring engine που μιμείται τη λογική ενός PE analyst.

Κάθε εταιρεία παίρνει score 0-100 ("PE Attractiveness Score")
βάσει weighted financial metrics.

Λογική:
- Χαμηλό EV/EBITDA → φτηνή εταιρεία, ελκυστική για buyout
- Υψηλό EBITDA margin → κερδοφόρο, δυνατό business
- Υψηλό revenue growth → αναπτυσσόμενο
- Χαμηλό debt/equity → "clean" balance sheet, χώρος για leverage
- Υψηλό free cash flow → δυνατότητα debt repayment post-acquisition
"""

import pandas as pd
import numpy as np

# ─── Βάρη scoring model ──────────────────────────────────────────────────────
WEIGHTS = {
    "ev_ebitda_score": 0.25,      # Valuation — το πιο κρίσιμο metric για PE
    "ebitda_margin_score": 0.25,  # Profitability
    "revenue_growth_score": 0.20, # Growth potential
    "fcf_score": 0.15,            # Cash generation
    "debt_score": 0.15,           # Balance sheet health
}


def _percentile_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """
    Μετατρέπει μια στήλη σε percentile scores (0–100).
    higher_is_better=False σημαίνει ότι χαμηλότερη τιμή = καλύτερο score
    (π.χ. EV/EBITDA, debt).
    """
    pct = series.rank(pct=True, na_option="bottom")
    if not higher_is_better:
        pct = 1 - pct
    return (pct * 100).round(1)


def score_companies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Παίρνει το raw dataframe και επιστρέφει scored + ranked εταιρείες.
    """
    scored = df.copy()

    # Φιλτράρουμε εταιρείες με πολύ λίγα δεδομένα
    required_cols = ["ev_ebitda", "ebitda_margin", "revenue_growth", "debt_to_equity", "free_cashflow"]
    scored = scored.dropna(subset=required_cols, thresh=3)

    # ─── Individual metric scores ────────────────────────────────────────────

    # EV/EBITDA: χαμηλό = ελκυστικό (κάτω από 10x = deal territory)
    scored["ev_ebitda_score"] = _percentile_score(scored["ev_ebitda"], higher_is_better=False)

    # EBITDA Margin: υψηλό = καλό (>20% = quality business)
    scored["ebitda_margin_score"] = _percentile_score(scored["ebitda_margin"], higher_is_better=True)

    # Revenue Growth: υψηλό = καλό
    scored["revenue_growth_score"] = _percentile_score(scored["revenue_growth"], higher_is_better=True)

    # Free Cash Flow: υψηλό = καλό (normalized by market cap)
    scored["fcf_yield"] = scored["free_cashflow"] / scored["market_cap"].replace(0, np.nan)
    scored["fcf_score"] = _percentile_score(scored["fcf_yield"], higher_is_better=True)

    # Debt/Equity: χαμηλό = καλό
    scored["debt_score"] = _percentile_score(scored["debt_to_equity"], higher_is_better=False)

    # ─── Weighted total score ────────────────────────────────────────────────
    scored["pe_score"] = sum(
        scored[metric] * weight for metric, weight in WEIGHTS.items()
    ).round(1)

    # ─── Qualitative tier ────────────────────────────────────────────────────
    def classify(score):
        if score >= 75:
            return "🟢 Strong Buy"
        elif score >= 55:
            return "🟡 Watch List"
        elif score >= 35:
            return "🟠 Marginal"
        else:
            return "🔴 Pass"

    scored["rating"] = scored["pe_score"].apply(classify)

    # Τελική ταξινόμηση
    scored = scored.sort_values("pe_score", ascending=False).reset_index(drop=True)
    scored["rank"] = scored.index + 1

    return scored


def get_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Επιστρέφει clean dataframe για εμφάνιση στο dashboard.
    """
    display = df[[
        "rank", "ticker", "name", "sector",
        "pe_score", "rating",
        "ev_ebitda", "ebitda_margin", "revenue_growth",
        "debt_to_equity", "market_cap",
    ]].copy()

    # Formatting
    display["ebitda_margin"] = (display["ebitda_margin"] * 100).round(1).astype(str) + "%"
    display["revenue_growth"] = (display["revenue_growth"] * 100).round(1).astype(str) + "%"
    display["ev_ebitda"] = display["ev_ebitda"].round(1).astype(str) + "x"
    display["market_cap"] = (display["market_cap"] / 1e9).round(1).astype(str) + "B"
    display["debt_to_equity"] = display["debt_to_equity"].round(1)

    display.columns = [
        "#", "Ticker", "Company", "Sector",
        "PE Score", "Rating",
        "EV/EBITDA", "EBITDA Margin", "Rev. Growth",
        "D/E Ratio", "Mkt Cap ($B)",
    ]

    return display
