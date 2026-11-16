select 
symbol,
company_name ,
round(100*(net_profit/nullif(revenue,0)),4) as [net_profit%],
round(100*(operating_income/nullif(revenue,0)),4)  as [operating_profit%],
round(100*(net_profit/nullif(total_assets,0)),4) as [ROA],
current_assets/nullif(current_liabilities,0) as [Current_ratio],
round(100*(dividend_per_share/nullif(price,0)),4) as [Divident_yeild],
round(price/nullif(book_value_per_share,0),4) as [pb]
from nifty50_fundamentals