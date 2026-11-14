"""
Pull Nifty 50 data for the 3 analysis levels. Output: nifty50_fundamentals.csv
Install: pip install yfinance pandas      Run: python pull_nifty50_fundamentals.py
All money values are in rupees. Edit SYMBOLS if the Nifty 50 list has changed.
"""
import time
from datetime import datetime

import pandas as pd
import yfinance as yf

SYMBOLS = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO",
    "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL", "CIPLA", "COALINDIA", "DRREDDY",
    "EICHERMOT", "ETERNAL", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
    "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JIOFIN",
    "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC",
    "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SHRIRAMFIN", "SUNPHARMA", "TATACONSUM",
    "TMPV", "TATASTEEL", "TCS", "TECHM", "TITAN", "TRENT", "ULTRACEMCO", "WIPRO",
]

# Columns in analysis order: Level 1 -> Level 2 -> Level 3
LEVEL1 = ["price", "eps", "net_profit", "total_debt", "equity", "market_cap"]
LEVEL2 = ["revenue", "operating_income", "total_assets", "current_assets",
          "current_liabilities", "dividend_per_share", "book_value_per_share", "free_cash_flow"]
LEVEL3 = ["sector", "is_financial"]          # sector rank, bank handling
COLUMNS = ["symbol", "company_name"] + LEVEL1 + LEVEL2 + LEVEL3 + ["filled_fields", "pulled_at"]


def latest(statement, names):
    """Latest-year value of the first row name found. Returns None if not found."""
    if statement is None or statement.empty:
        return None
    statement = statement.sort_index(axis=1, ascending=False)
    for name in names:
        if name in statement.index:
            s = statement.loc[name].dropna()
            if not s.empty:
                return float(s.iloc[0])
    return None


def pull_one(symbol):
    t = yf.Ticker(f"{symbol}.NS")
    info, inc, bal, cf = t.info or {}, t.financials, t.balance_sheet, t.cashflow
    sector = info.get("sector") or "Unknown"

    r = {
        "symbol": symbol, "company_name": info.get("shortName"),
        # Level 1
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "eps": info.get("trailingEps"),
        "net_profit": latest(inc, ["Net Income", "Net Income Common Stockholders"]),
        "total_debt": latest(bal, ["Total Debt"]),
        "equity": latest(bal, ["Stockholders Equity", "Common Stock Equity",
                               "Total Equity Gross Minority Interest"]),
        "market_cap": info.get("marketCap"),
        # Level 2
        "revenue": latest(inc, ["Total Revenue", "Operating Revenue"]),
        "operating_income": latest(inc, ["Operating Income", "EBIT"]),
        "total_assets": latest(bal, ["Total Assets"]),
        "current_assets": latest(bal, ["Current Assets"]),
        "current_liabilities": latest(bal, ["Current Liabilities"]),
        "dividend_per_share": info.get("dividendRate"),
        "book_value_per_share": info.get("bookValue"),
        "free_cash_flow": latest(cf, ["Free Cash Flow"]),
        # Level 3
        "sector": sector, "is_financial": int(sector == "Financial Services"),
        "shares": info.get("sharesOutstanding"),   # helper only, not saved
        "filled": [],
    }

    def fill(key, fn):
        """If a value is blank, try fn() to calculate it from other data."""
        if pd.isna(r[key]):
            try:
                v = fn()
            except Exception:
                return
            if v is not None and not pd.isna(v):
                r[key] = v
                r["filled"].append(key)

    # Fill order matters: price -> shares -> market cap -> profit and equity
    fill("price", lambda: t.history(period="5d")["Close"].iloc[-1])
    fill("shares", lambda: r["market_cap"] / r["price"])
    fill("market_cap", lambda: r["price"] * r["shares"])
    fill("eps", lambda: r["net_profit"] / r["shares"])
    fill("net_profit", lambda: r["eps"] * r["shares"])
    fill("equity", lambda: r["book_value_per_share"] * r["shares"])
    fill("book_value_per_share", lambda: r["equity"] / r["shares"])
    fill("total_debt", lambda: latest(bal, ["Long Term Debt"]) + latest(bal, ["Current Debt"]))
    fill("free_cash_flow", lambda: latest(cf, ["Operating Cash Flow"]) + latest(cf, ["Capital Expenditure"]))
    fill("dividend_per_share", lambda: 0.0)        # no dividend reported = pays none

    r["filled_fields"] = ", ".join(r["filled"])
    r["pulled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return r


rows, failed = [], []
for i, sym in enumerate(SYMBOLS, 1):
    try:
        rows.append(pull_one(sym))
        print(f"[{i}/{len(SYMBOLS)}] OK     {sym}")
    except Exception as e:
        failed.append(sym)
        print(f"[{i}/{len(SYMBOLS)}] FAILED {sym}: {e}")
    time.sleep(1)

df = pd.DataFrame(rows).reindex(columns=COLUMNS)
df.to_csv("nifty50_fundamentals.csv", index=False)

blank = df[LEVEL1 + LEVEL2].isna().sum()
print(f"\nSaved {len(df)} rows. Failed: {', '.join(failed) or 'none'}")
print("Blank values left (banks have no current assets or liabilities):")
print(blank[blank > 0].to_string() or "none")