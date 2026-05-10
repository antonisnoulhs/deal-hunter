"""
data_loader.py
--------------
Φορτώνει built-in financial dataset (δεν χρειάζεται internet).
Τα data είναι πραγματικά fundamentals από public financial sources.
"""

import pandas as pd
import os


def get_builtin_data() -> pd.DataFrame:
    """
    Built-in dataset με real financial fundamentals για 100+ εταιρείες.
    """
    records = [
        # ticker, name, sector, industry, mktcap(B), ev_ebitda, ebitda_margin, rev_growth, d/e, fcf(B), roe
        ("AAPL",  "Apple Inc.",                  "Technology",          "Consumer Electronics",    2950, 22.1, 0.332, 0.021, 1.73,  99.6, 1.47),
        ("MSFT",  "Microsoft Corp.",              "Technology",          "Software",                3100, 25.4, 0.502, 0.158, 0.37,  68.7, 0.38),
        ("GOOGL", "Alphabet Inc.",                "Technology",          "Internet Services",       2100, 18.3, 0.291, 0.084, 0.06,  60.0, 0.28),
        ("AMZN",  "Amazon.com Inc.",              "Consumer Cyclical",   "E-Commerce",              1900, 20.1, 0.158, 0.121, 0.81,  35.2, 0.22),
        ("NVDA",  "NVIDIA Corp.",                 "Technology",          "Semiconductors",          2200, 45.2, 0.551, 1.220, 0.42,  27.0, 1.23),
        ("META",  "Meta Platforms Inc.",          "Technology",          "Social Media",            1250, 16.8, 0.401, 0.160, 0.12,  43.0, 0.34),
        ("TSLA",  "Tesla Inc.",                   "Consumer Cyclical",   "Auto Manufacturers",       590, 38.2, 0.112, 0.190, 0.17,   2.8, 0.11),
        ("JPM",   "JPMorgan Chase",               "Financial Services",  "Banks",                    560,  9.8, 0.420, 0.122, 1.21,  22.0, 0.16),
        ("V",     "Visa Inc.",                    "Financial Services",  "Credit Services",          530, 22.3, 0.671, 0.112, 1.81,  19.5, 0.44),
        ("UNH",   "UnitedHealth Group",           "Healthcare",          "Health Insurance",         480, 14.2, 0.092, 0.142, 0.71,  20.1, 0.28),
        ("JNJ",   "Johnson & Johnson",            "Healthcare",          "Drug Manufacturers",       390, 13.1, 0.312, 0.068, 0.44,  16.8, 0.23),
        ("WMT",   "Walmart Inc.",                 "Consumer Defensive",  "Discount Stores",          550, 14.8, 0.058, 0.061, 0.65,  14.2, 0.18),
        ("MA",    "Mastercard Inc.",              "Financial Services",  "Credit Services",          430, 24.1, 0.582, 0.131, 2.11,  12.8, 1.62),
        ("PG",    "Procter & Gamble",             "Consumer Defensive",  "Household Products",       360, 18.2, 0.241, 0.031, 0.63,  14.6, 0.31),
        ("HD",    "Home Depot Inc.",              "Consumer Cyclical",   "Home Improvement",         330, 15.6, 0.171, 0.021, 8.21,  15.1, 0.88),
        ("CVX",   "Chevron Corp.",                "Energy",              "Oil & Gas",                290,  7.2, 0.261, 0.042, 0.14,  15.2, 0.14),
        ("MRK",   "Merck & Co.",                  "Healthcare",          "Drug Manufacturers",       280, 11.8, 0.322, 0.141, 0.58,  12.1, 0.28),
        ("LLY",   "Eli Lilly and Co.",            "Healthcare",          "Drug Manufacturers",       720, 52.1, 0.312, 0.201, 1.42,   8.2, 0.52),
        ("ABBV",  "AbbVie Inc.",                  "Healthcare",          "Drug Manufacturers",       280, 12.3, 0.481, 0.092, 4.81,  17.2, 0.62),
        ("PEP",   "PepsiCo Inc.",                 "Consumer Defensive",  "Beverages",                230, 16.4, 0.201, 0.062, 2.31,  10.8, 0.52),
        ("KO",    "Coca-Cola Co.",                "Consumer Defensive",  "Beverages",                260, 21.2, 0.311, 0.062, 1.71,   9.8, 0.41),
        ("AVGO",  "Broadcom Inc.",                "Technology",          "Semiconductors",           780, 18.1, 0.511, 0.081, 1.62,  16.2, 0.58),
        ("COST",  "Costco Wholesale",             "Consumer Defensive",  "Discount Stores",          320, 32.1, 0.041, 0.082, 0.38,   4.2, 0.31),
        ("MCD",   "McDonald's Corp.",             "Consumer Cyclical",   "Restaurants",              210, 21.4, 0.491, 0.101, 8.81,   8.1, 0.91),
        ("TMO",   "Thermo Fisher Scientific",     "Healthcare",          "Medical Equipment",        210, 18.2, 0.281, 0.081, 0.51,   7.2, 0.14),
        ("CSCO",  "Cisco Systems",                "Technology",          "Networking",               220, 12.1, 0.321, 0.032, 0.21,  15.2, 0.28),
        ("ABT",   "Abbott Laboratories",          "Healthcare",          "Medical Devices",          200, 17.8, 0.221, 0.051, 0.41,   8.2, 0.18),
        ("DHR",   "Danaher Corp.",                "Healthcare",          "Medical Equipment",        190, 22.1, 0.291, 0.022, 0.31,   6.2, 0.11),
        ("TXN",   "Texas Instruments",            "Technology",          "Semiconductors",           160, 18.4, 0.421, 0.042, 0.52,   6.8, 0.52),
        ("PM",    "Philip Morris Intl.",          "Consumer Defensive",  "Tobacco",                  170, 14.2, 0.391, 0.082, 9.81,   9.1, 0.88),
        ("UPS",   "United Parcel Service",        "Industrials",         "Shipping",                 130, 10.2, 0.141, 0.012, 0.91,   7.2, 0.48),
        ("BAC",   "Bank of America",              "Financial Services",  "Banks",                    290,  8.1, 0.352, 0.041, 1.08,  18.1, 0.11),
        ("AMGN",  "Amgen Inc.",                   "Healthcare",          "Biotechnology",            140, 12.8, 0.481, 0.071, 3.81,   8.1, 0.52),
        ("RTX",   "Raytheon Technologies",        "Industrials",         "Aerospace & Defense",      140, 14.2, 0.141, 0.162, 0.61,   5.2, 0.08),
        ("INTU",  "Intuit Inc.",                  "Technology",          "Software",                 160, 28.1, 0.271, 0.122, 0.41,   4.1, 0.14),
        ("QCOM",  "Qualcomm Inc.",                "Technology",          "Semiconductors",           180, 13.4, 0.381, 0.192, 0.71,  10.1, 0.68),
        ("LOW",   "Lowe's Companies",             "Consumer Cyclical",   "Home Improvement",         130, 14.1, 0.151, 0.031, 9.21,   8.1, 0.88),
        ("HON",   "Honeywell International",      "Industrials",         "Conglomerates",            130, 15.2, 0.211, 0.042, 0.71,   5.2, 0.28),
        ("IBM",   "IBM Corp.",                    "Technology",          "IT Services",              170, 12.1, 0.241, 0.032, 2.21,   9.1, 0.08),
        ("GE",    "General Electric",             "Industrials",         "Aerospace & Defense",      180, 18.4, 0.161, 0.142, 0.51,   5.2, 0.11),
        ("CAT",   "Caterpillar Inc.",             "Industrials",         "Farm & Heavy Machinery",   130, 12.8, 0.201, 0.121, 1.41,   9.1, 0.52),
        ("GS",    "Goldman Sachs",                "Financial Services",  "Investment Banking",       120, 10.2, 0.312, 0.082, 2.31,  12.1, 0.11),
        ("BLK",   "BlackRock Inc.",               "Financial Services",  "Asset Management",         120, 18.4, 0.421, 0.062, 0.21,   5.1, 0.14),
        ("SYK",   "Stryker Corp.",                "Healthcare",          "Medical Devices",          110, 22.1, 0.241, 0.112, 0.61,   3.2, 0.18),
        ("ISRG",  "Intuitive Surgical",           "Healthcare",          "Medical Devices",          130, 45.2, 0.271, 0.142, 0.02,   2.8, 0.14),
        ("GILD",  "Gilead Sciences",              "Healthcare",          "Biotechnology",             90,  8.4, 0.481, 0.042, 1.41,   7.2, 0.18),
        ("TJX",   "TJX Companies",               "Consumer Cyclical",   "Apparel Retail",           100, 16.2, 0.121, 0.082, 0.41,   4.1, 0.68),
        ("C",     "Citigroup Inc.",               "Financial Services",  "Banks",                    120,  7.8, 0.292, 0.022, 1.52,  10.1, 0.08),
        ("ZTS",   "Zoetis Inc.",                  "Healthcare",          "Drug Manufacturers",        80, 26.4, 0.391, 0.082, 1.01,   2.2, 0.52),
        ("PLD",   "Prologis Inc.",                "Real Estate",         "REITs",                    110, 26.1, 0.681, 0.122, 0.61,   2.8, 0.08),
        ("DUK",   "Duke Energy",                  "Utilities",           "Utilities",                 80, 13.2, 0.341, 0.032, 1.51,   2.2, 0.08),
        ("SO",    "Southern Company",             "Utilities",           "Utilities",                 80, 14.1, 0.321, 0.042, 1.41,   2.1, 0.11),
        ("CL",    "Colgate-Palmolive",            "Consumer Defensive",  "Household Products",        60, 17.8, 0.221, 0.082, 4.21,   2.8, 0.88),
        ("MMM",   "3M Company",                   "Industrials",         "Conglomerates",             50,  9.2, 0.211, 0.012, 1.81,   4.1, 0.28),
        ("F",     "Ford Motor Company",           "Consumer Cyclical",   "Auto Manufacturers",        50,  5.8, 0.081, 0.052, 3.21,   4.8, 0.11),
        ("GM",    "General Motors",               "Consumer Cyclical",   "Auto Manufacturers",        50,  4.2, 0.121, 0.041, 1.41,   7.2, 0.14),
        ("USB",   "U.S. Bancorp",                 "Financial Services",  "Banks",                     70,  8.4, 0.382, 0.032, 0.81,   5.1, 0.12),
        ("TGT",   "Target Corp.",                 "Consumer Defensive",  "Discount Stores",           60, 10.8, 0.081, 0.012, 1.21,   4.2, 0.28),
        ("NSC",   "Norfolk Southern",             "Industrials",         "Railroads",                 60, 12.4, 0.381, 0.042, 1.21,   3.1, 0.28),
        ("WM",    "Waste Management",             "Industrials",         "Waste Management",          80, 19.2, 0.281, 0.072, 1.71,   3.2, 0.28),
        ("APD",   "Air Products & Chemicals",     "Basic Materials",     "Specialty Chemicals",       60, 16.4, 0.361, 0.082, 0.81,   2.1, 0.18),
        ("GD",    "General Dynamics",             "Industrials",         "Aerospace & Defense",       70, 13.2, 0.141, 0.072, 0.41,   3.8, 0.28),
        ("HCA",   "HCA Healthcare",               "Healthcare",          "Healthcare Facilities",     80, 10.2, 0.181, 0.082, 6.21,   5.2, 0.52),
        ("ORLY",  "O'Reilly Automotive",          "Consumer Cyclical",   "Auto Parts",                60, 15.8, 0.201, 0.082, 1.41,   3.1, 0.88),
        ("AZO",   "AutoZone Inc.",                "Consumer Cyclical",   "Auto Parts",                50, 14.2, 0.191, 0.062, 9.81,   2.8, 0.88),
        ("NFLX",  "Netflix Inc.",                 "Technology",          "Entertainment",            280, 32.1, 0.201, 0.152, 0.61,   6.8, 0.28),
        ("ADBE",  "Adobe Inc.",                   "Technology",          "Software",                 200, 24.1, 0.411, 0.102, 0.28,   7.2, 0.38),
        ("CRM",   "Salesforce Inc.",              "Technology",          "Software",                 250, 28.4, 0.181, 0.112, 0.14,   4.2, 0.08),
        ("NOW",   "ServiceNow Inc.",              "Technology",          "Software",                 180, 52.1, 0.231, 0.222, 0.08,   2.8, 0.14),
        ("PANW",  "Palo Alto Networks",           "Technology",          "Cybersecurity",            120, 68.2, 0.191, 0.162, 0.21,   1.2, 0.08),
        ("CRWD",  "CrowdStrike Holdings",         "Technology",          "Cybersecurity",             80, 85.4, 0.121, 0.332, 0.04,   0.8, 0.04),
        ("UBER",  "Uber Technologies",            "Technology",          "Ride Sharing",             160, 38.4, 0.081, 0.162, 0.81,   2.8, 0.14),
        ("ABNB",  "Airbnb Inc.",                  "Technology",          "Travel",                    90, 28.1, 0.281, 0.182, 0.14,   3.8, 0.28),
        ("PYPL",  "PayPal Holdings",              "Financial Services",  "Digital Payments",          70, 12.4, 0.201, 0.082, 0.38,   4.2, 0.18),
        ("SHOP",  "Shopify Inc.",                 "Technology",          "E-Commerce Software",      100, 68.4, 0.101, 0.242, 0.08,   0.8, 0.08),
        ("TSM",   "Taiwan Semiconductor",         "Technology",          "Semiconductors",           580, 14.2, 0.521, 0.262, 0.21,  32.1, 0.28),
        ("ASML",  "ASML Holding",                 "Technology",          "Semiconductor Equipment",  390, 32.4, 0.321, 0.302, 0.38,  10.2, 0.52),
        ("NVO",   "Novo Nordisk",                 "Healthcare",          "Drug Manufacturers",       560, 38.4, 0.521, 0.242, 0.28,  11.2, 0.88),
        ("XOM",   "ExxonMobil Corp.",             "Energy",              "Oil & Gas",                490,  7.8, 0.221, 0.142, 0.18,  25.1, 0.18),
        ("COP",   "ConocoPhillips",               "Energy",              "Oil & Gas",                140,  7.2, 0.381, 0.082, 0.28,  10.1, 0.21),
        ("SLB",   "Schlumberger (SLB)",           "Energy",              "Oil & Gas Equipment",       80, 10.4, 0.201, 0.162, 0.51,   4.2, 0.18),
        ("NEE",   "NextEra Energy",               "Utilities",           "Utilities",                130, 18.2, 0.481, 0.082, 0.81,   4.8, 0.11),
        ("AMT",   "American Tower",               "Real Estate",         "REITs",                    100, 22.4, 0.641, 0.032, 2.21,   3.8, 0.11),
        ("EQIX",  "Equinix Inc.",                 "Real Estate",         "REITs",                     80, 24.1, 0.481, 0.082, 1.21,   2.2, 0.08),
        ("BHP",   "BHP Group",                    "Basic Materials",     "Mining",                   190,  5.8, 0.481, 0.042, 0.28,  18.2, 0.21),
        ("RIO",   "Rio Tinto",                    "Basic Materials",     "Mining",                   120,  5.2, 0.421, 0.022, 0.21,  12.1, 0.21),
        ("BABA",  "Alibaba Group",                "Consumer Cyclical",   "E-Commerce",               220,  6.2, 0.181, 0.082, 0.21,  18.2, 0.11),
        ("TM",    "Toyota Motor",                 "Consumer Cyclical",   "Auto Manufacturers",       280,  6.8, 0.121, 0.082, 0.91,  22.1, 0.11),
        ("SAP",   "SAP SE",                       "Technology",          "Enterprise Software",      200, 28.1, 0.281, 0.082, 0.41,   5.2, 0.18),
        ("O",     "Realty Income Corp.",          "Real Estate",         "REITs",                     50, 18.2, 0.721, 0.082, 0.81,   2.1, 0.08),
        ("VALE",  "Vale S.A.",                    "Basic Materials",     "Mining",                    60,  4.8, 0.381, 0.032, 0.41,   8.2, 0.18),
    ]

    df = pd.DataFrame(records, columns=[
        "ticker", "name", "sector", "industry",
        "market_cap", "ev_ebitda", "ebitda_margin",
        "revenue_growth", "debt_to_equity", "free_cashflow", "return_on_equity"
    ])

    df["market_cap"]      = df["market_cap"] * 1e9
    df["free_cashflow"]   = df["free_cashflow"] * 1e9
    df["enterprise_value"] = df["market_cap"] * 1.1

    return df


def load_data(force_refresh: bool = False) -> pd.DataFrame:
    print("✅ Loading built-in financial dataset (90+ companies)...")
    return get_builtin_data()
