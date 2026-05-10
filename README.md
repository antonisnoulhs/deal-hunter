# 🎯 Deal Hunter — PE Deal Sourcing Screener

> A Python-based Private Equity deal sourcing tool that screens 90+ global companies and ranks acquisition targets using a weighted financial scoring model.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Overview

Deal Hunter replicates the logic a PE analyst uses when screening for acquisition targets. It combines real financial data with a proprietary scoring model to surface the most attractive buyout candidates across the S&P 500 universe.

Built as a personal project to apply computer science skills to private equity and investment banking workflows.

---

## 🚀 Features

- **PE Attractiveness Score (0–100)** — weighted model across 5 key metrics
- **Interactive filters** — sector, EV/EBITDA cap, EBITDA margin, revenue growth, market cap
- **LBO Returns Estimator** — calculates IRR & MOIC with sensitivity analysis
- **Visual analytics** — scatter plots, sector comparison charts, equity build-up
- **Export to CSV** — for further analysis in Excel

---

## 🧠 Scoring Model

Each company is scored using percentile ranking across 5 PE-relevant metrics:

| Metric | Weight | Logic |
|--------|--------|-------|
| EV/EBITDA | 25% | Lower = cheaper acquisition target |
| EBITDA Margin | 25% | Higher = more profitable business |
| Revenue Growth | 20% | Higher = more upside post-acquisition |
| FCF Yield | 15% | Higher = stronger debt repayment capacity |
| Debt/Equity | 15% | Lower = cleaner balance sheet |

### Rating Tiers
| Score | Rating |
|-------|--------|
| 75–100 | 🟢 Strong Buy |
| 55–74 | 🟡 Watch List |
| 35–54 | 🟠 Marginal |
| 0–34 | 🔴 Pass |

---

## 📐 LBO Returns Estimator

Model a full leveraged buyout scenario with:
- Entry/exit EV/EBITDA multiples
- Debt financing % and FCF paydown
- EBITDA CAGR assumption
- Holding period (3–7 years)

Outputs: **IRR**, **MOIC**, equity build-up chart, and a full **IRR sensitivity table**.

---

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/antonisnoulhs/deal-hunter.git
cd deal-hunter

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core logic |
| Streamlit | Interactive dashboard |
| Pandas | Data processing |
| Plotly | Charts & visualizations |
| NumPy | IRR calculation (Newton-Raphson) |

---

## 📁 Project Structure

```
deal-hunter/
├── app.py              # Main Streamlit app (self-contained)
├── requirements.txt
└── src/
    ├── data_loader.py  # Financial dataset
    ├── scorer.py       # PE scoring engine
    └── lbo.py          # LBO returns model
```

---

## 👤 Author

**Antonis Noulhs** — Computer Science Student, Year 3  
Interested in Private Equity, Investment Banking & Quantitative Finance

---

## 📄 License

MIT License — free to use and modify.
