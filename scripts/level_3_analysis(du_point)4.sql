with measure as (
select symbol,
company_name ,
net_profit/revenue as [net_profit_margin],
revenue/total_assets as [asset_turnover],
total_assets /equity as [de],
net_profit/equity [ROE_check]
from nifty50_fundamentals)

select count(*)
from (
select 
k.company_name,
k.ROE_check,
net_profit_margin*asset_turnover*de  as roe
from measure as k ) t
where ROE_check != roe

select *
from nifty50_fundamentals