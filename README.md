# Nifty 50 Quant Stock Screener

Rank all 50 Nifty 50 stocks on value, quality, and risk. Python pulls the data. SQL Server calculates the measures and ranks. Power BI shows the results.

![Valuation and Quality Scorecard](images/valuation_quality_scorecard.png)

---

## Business question

Which Nifty 50 companies give the best mix of low valuation, high profitability, and low debt?

An investor cannot compare 50 balance sheets by hand. This project turns raw fundamentals into three clear views:

1. **Fundamentals** – how big, how profitable, how indebted.
2. **Efficiency** – how well each company turns assets and sales into profit.
3. **Ranking** – a weighted score that places each stock in a quintile.

---

## Key findings

Results come from one data snapshot. See [Limitations](#limitations).

| Theme | Result |
|---|---|
| Top weighted rank | COALINDIA (85.71%), INFY (84.08%), ITC (82.04%), HEROMOTOCO and TCS (81.22%) |
| Highest ROE | NESTLEIND (79.99%), TMPV (73.52%), TCS (45.89%) |
| Lowest P/E | ONGC (5.9), COALINDIA (7.4), SBIN (10.6) |
| Lowest debt to equity | MARUTI (0.001), BEL (0.003), CIPLA (0.018) |
| Highest dividend yield | COALINDIA (10.21%), INFY (4.51%), WIPRO (4.02%) |
| Highest ROA | TCS (26.98%), INFY (20.14%), HCLTECH (14.31%) |
| Universe averages | Average ROE 18.88%, median P/E 29.75, average P/B 6.01 |

**Reading the result:** Three IT names (INFY, TCS, HCLTECH) sit in the top six. COALINDIA ranks first. It shows a low P/E (7.4), a 26.11% ROE, and a 10.21% dividend yield. Compare each stock with its sector before you draw a conclusion.

---

## Architecture

```
yfinance (.NS tickers)
        │
        ▼
Python script  ──►  nifty50_fundamentals.csv
        │
        ▼
SQL Server: stock_analytical_project_1.dbo.nifty50_fundamentals
        │
        ├── Level 1: core ratios
        ├── Level 2: efficiency ratios
        └── Level 3: sector z-scores and weighted ranking
        │
        ▼
Power BI (3 report pages)
```

---

## Tech stack

| Layer | Tool |
|---|---|
| Data source | yfinance (Yahoo Finance), NSE tickers with `.NS` suffix |
| Import | Python, `pandas`, `yfinance` |
| Storage and logic | SQL Server (T-SQL) |
| Visualization | Power BI |

---

## Repository structure

```
├── import_os.py                    # Pulls data, saves nifty50_fundamentals.csv
├── level_1_analysis.sql            # Core ratios
├── level_2_analysis.sql            # Efficiency ratios
├── level_3_analysis_sector_2.sql   # Sector mapping (view: vw_sector_divide)
├── level_3_analysis_3.sql          # Sector z-scores
├── level_3_analytical_01.sql       # Weighted percentile rank and quintiles
├── images/                         # Dashboard screenshots
└── README.md
```

---

## Data pipeline (Python)

`import_os.py` pulls data for 50 symbols and saves one CSV.

- **Source:** `yfinance`, with `.NS` added to each symbol.
- **Units:** All money values are in rupees.
- **Rate limit:** The script waits 1 second between symbols.
- **Gap filling:** If a value is blank, the script calculates it from other fields. The `filled_fields` column records each filled field. This keeps the process traceable.
- **Audit columns:** `filled_fields` and `pulled_at` (timestamp).
- **Failed symbols:** The script prints them at the end.
- **Banks:** Banks have no current assets or current liabilities. These stay blank.

**Fields by analysis level**

| Level | Fields |
|---|---|
| 1 | price, eps, net_profit, total_debt, equity, market_cap |
| 2 | revenue, operating_income, total_assets, current_assets, current_liabilities, dividend_per_share, book_value_per_share, free_cash_flow |
| 3 | sector, is_financial |

---

## Analysis levels

### Level 1 – Core ratios (`level_1_analysis.sql`)

| Measure | Formula | How to read it |
|---|---|---|
| ROE | net_profit ÷ equity | Higher means more profit on owner capital |
| P/E | price ÷ eps (NULL if eps < 0) | Lower can mean cheaper |
| Earnings yield | eps ÷ price | Higher means more earnings per rupee paid |
| D/E | total_debt ÷ equity | Lower means less financial risk |
| Market cap (₹ crore) | market_cap ÷ 10,000,000 | Shows company size |

### Level 2 – Efficiency ratios (`level_2_analysis.sql`)

| Measure | Formula | How to read it |
|---|---|---|
| Net profit margin % | net_profit ÷ revenue | Profit kept from each rupee of sales |
| Operating margin % | operating_income ÷ revenue | Core business profit before interest and tax |
| ROA | net_profit ÷ total_assets | Profit made from all assets |
| Current ratio | current_assets ÷ current_liabilities | Short-term liquidity. Above 1 is safer |
| Dividend yield % | dividend_per_share ÷ price | Cash return to shareholders |
| P/B | price ÷ book_value_per_share | Price compared with book value |

### Level 3 – Sector context and ranking

**Sector mapping** (`level_3_analysis_sector_2.sql`)
Each symbol maps to one of eight sectors: Financials, IT, Energy & Utilities, Consumer, Auto, Healthcare, Materials, and Industrials & Services. Any symbol not in the list shows as `Unmapped`.

**Sector z-scores** (`level_3_analysis_3.sql`)
The query calculates z-scores for P/E, D/E, and ROE inside each sector.

`z = (value − sector average) ÷ sector standard deviation`

This shows how a stock compares with its own peers. A bank and a steel company have different normal debt levels, so sector context matters.

**Weighted percentile rank** (`level_3_analytical_01.sql`)
The query ranks all 50 stocks on three measures using `PERCENT_RANK()`, then combines them.

| Measure | Rank direction | Weight |
|---|---|---|
| D/E | Lower is better | 40% |
| P/E | Lower is better | 40% |
| ROE | Higher is better | 20% |

`weighted_rank = 0.40 × rank_DE + 0.40 × rank_PE + 0.20 × rank_ROE`

`NTILE(5)` then splits stocks into quintiles. **Quintile 1 is the top group. Quintile 5 is the bottom group.**

**Missing data rules**

- Negative EPS gives P/E = NULL. The rank treats NULL P/E as the worst value.
- NULL D/E ranks as the worst value.
- NULL ROE ranks as the lowest value.

---

## Dashboard

### Page 1 – Valuation & Quality Scorecard
Weighted rank, value-versus-quality scatter plot, sector quintiles, composite z-score, and a z-score heat map. Filters: grade, company, sector.

![Valuation and Quality Scorecard](images/valuation_quality_scorecard.png)

### Page 2 – Company Valuation & Efficiency Ratios
Top 10 current ratio, price to book, and return on assets. Top 5 dividend yield. Net and operating profit margin.

![Valuation and Efficiency Ratios](images/valuation_efficiency_ratios.png)

### Page 3 – Fundamental Financial Overview
Bottom 10 debt to equity and P/E. Market cap treemap by sector. ROE for all companies.

![Fundamental Financial Overview](images/fundamental_financial_overview.png)

---

## How to run

1. **Install packages.**
   ```bash
   pip install yfinance pandas
   ```
2. **Run the import script.**
   ```bash
   python import_os.py
   ```
   Output: `nifty50_fundamentals.csv`.
3. **Load the data.** Load the CSV into SQL Server: database `stock_analytical_project_1`, table `dbo.nifty50_fundamentals`.
4. **Create the sector view.** Create `vw_sector_divide` from `level_3_analysis_sector_2.sql`. The Level 3 z-score query needs this view.
5. **Run the SQL files.** Run Level 1, Level 2, and Level 3 in order.
6. **Open Power BI.** Connect to your SQL Server. Refresh the data.

Update the `SYMBOLS` list in the script if NSE changes the Nifty 50 index.

---

## Limitations

- **Single snapshot.** Each run captures data at one time (`pulled_at`). Results change with each pull.
- **Free data.** yfinance data can be late, incomplete, or revised. The script fills some gaps by calculation. Check the `filled_fields` column.
- **Banks and financials.** D/E, current ratio, and P/E do not carry the same meaning for banks. The `is_financial` flag exists for this reason.
- **Manual sector map.** The sector list is hard-coded. New index members show as `Unmapped` until you add them.
- **Small peer groups.** Some sectors have few companies. Sector z-scores are less stable with small samples.
- **Not investment advice.** The ranking is a screening tool. It does not replace full company research.

---

## Next steps

- Add a sector-neutral ranking next to the market-wide ranking.
- Add historical snapshots to track rank changes over time.
- Add bank-specific measures (for example, NIM and NPA) for Financials.

---

## Author

**Ayush**

- GitHub: [github.com/20ayush09](https://github.com/20ayush09)
- LinkedIn: [linkedin.com/in/ayush-agarwal-9270672bb](https://www.linkedin.com/in/ayush-agarwal-9270672bb/)