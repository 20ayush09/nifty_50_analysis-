with measures as 
(
select 
symbol, 
company_name ,
case when eps <0 then null else 
price/nullif(eps,0) 
end as [pe],
net_profit/nullif(equity,0) [ROE],
total_debt/nullif(equity,0) [de]
from nifty50_fundamentals
),
percentage_rank as (

select
symbol,
company_name,
per_rank_de,
per_rank_pe,
per_rank_roe,
(.40*per_rank_de)+(.40*per_rank_pe)+(.20*per_rank_roe) as [weighted_rank]
from (
select
symbol,
company_name,
PERCENT_RANK() over ( order by coalesce(pe,99999) desc) as per_rank_pe,
PERCENT_RANK() over ( order by coalesce(de,99999) desc) as per_rank_de ,
PERCENT_RANK() over (order by coalesce(ROE,0) asc) as per_rank_roe
from measures ) t
)
select *,
ntile (5) over(order by weighted_rank desc) as quintile 
from percentage_rank