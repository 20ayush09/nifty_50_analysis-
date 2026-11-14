SELECT TOP (1000) [symbol]
      ,[company_name]
      ,[sector]
      ,[industry]
      ,[is_financial]
      ,[price]
      ,[eps]
      ,[net_profit]
      ,[total_debt]
      ,[equity]
      ,[market_cap]
      ,[revenue]
      ,[operating_income]
      ,[total_assets]
      ,[current_assets]
      ,[current_liabilities]
      ,[dividend_per_share]
      ,[book_value_per_share]
      ,[free_cash_flow]
      ,[shares_outstanding]
      ,[pe_yahoo]
      ,[income_year_end]
      ,[balance_year_end]
      ,[cashflow_year_end]
      ,[years_match]
      ,[pulled_at]
  FROM [stock_analytical_project_1].[dbo].[nifty50_fundamentals]
  --where total_debt is null (DONE)
 --where operating_income is null 
  --where current_assets is null 
  --where current_liabilities is null 
  --where dividend_per_share is null 
  --where pe_yahoo is null
  
  


  