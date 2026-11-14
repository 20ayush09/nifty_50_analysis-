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
)
, stdev_measure as 
(
select 
sd1.symbol,
sd1.company_name ,
pe,
roe,
de,
avg(pe) over(partition by sector ) as a_pe,
avg(roe) over(partition by sector ) as a_roe ,
avg(de) over(partition by sector ) as a_de,
stdev(pe) over(partition by sector ) stdev_pe,
stdev(roe) over (partition by sector ) stdev_roe,
stdev(de) over(partition by sector ) stdev_de 
from measures as m1
join vw_sector_divide as sd1 
on m1.company_name = sd1.company_name 
)
select 
sd.symbol,
sd.sector,
1*(pe-a_pe)/nullif(stdev_pe,0) as z_pe ,
1*(de-a_de)/nullif(stdev_de,0) as z_de ,
(roe -a_roe)/nullif(stdev_roe,0) as z_roe
from vw_sector_divide as sd
join stdev_measure  as m
on m.company_name = sd.company_name 
order by sector