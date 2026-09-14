WITH custo_por_campanha as 
(

SELECT campanha_id, sum(cast(gasto as double)) as custo_por_campanha  FROM "trading_data_mngmt_index_data_dev"."investimento_midia" group by 1

),

lead_por_campanha as (

SELECT campanha_id, count( distinct lead_id) as lead_por_campanha FROM "trading_data_mngmt_index_data_dev"."leads" group by 1

)

SELECT t1.campanha_id, t1.custo_por_campanha, t2.lead_por_campanha,

round(t1.custo_por_campanha/t2.lead_por_campanha,2) as custo_lead_campanha


from custo_por_campanha t1
LEFT JOIN lead_por_campanha t2
on t1.campanha_id = t2.campanha_id

order by t1.custo_por_campanha/t2.lead_por_campanha asc
