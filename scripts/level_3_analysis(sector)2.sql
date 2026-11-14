select symbol,company_name,
  case
        -- Financials
        when symbol in ('HDFCBANK','ICICIBANK','SBIN','AXISBANK','KOTAKBANK',
                     'INDUSINDBK','BAJFINANCE','BAJAJFINSV','SHRIRAMFIN',
                     'HDFCLIFE','SBILIFE','JIOFIN','BSE')
            then 'Financials'

        -- IT
        when symbol in ('TCS','INFY','HCLTECH','TECHM','WIPRO')
            then 'IT'

        -- Energy & Utilities
        when symbol in ('RELIANCE','ONGC','NTPC','POWERGRID')
            then 'Energy & Utilities'

        -- Consumer
        when symbol in ('HINDUNILVR','ITC','NESTLEIND','TATACONSUM',
                     'TITAN','ASIANPAINT','ETERNAL','ZOMATO','TRENT')
            then 'Consumer'

        -- Auto
        when symbol in ('MARUTI','M&M','BAJAJ-AUTO','EICHERMOT',
                     'TATAMOTORS','TMPV')
            then 'Auto'

        -- Healthcare
        when symbol in ('SUNPHARMA','CIPLA','DRREDDY','APOLLOHOSP')
            then 'Healthcare'

        -- Materials
        when symbol in ('TATASTEEL','JSWSTEEL','HINDALCO','COALINDIA',
                     'ADANIENT','ULTRACEMCO','GRASIM')
            then 'Materials'

        -- Industrials & Services
        when symbol in ('LT','BEL','ADANIPORTS','INDIGO','BHARTIARTL')
            then 'Industrials & Services'

        else 'Unmapped'
    end as sector
from nifty50_fundamentals