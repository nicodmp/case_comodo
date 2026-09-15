-- Query é composta por CTEs (tabelas temporárias, que são usadas somente em tempo de execução)

-- 1ª Tabela temporária (campanha por soma de gasto) 
WITH custo_por_campanha as (

SELECT 
    campanha_id, 
    sum(
        gasto
        ) 
        as custo_por_campanha 
    FROM investimento_midia 
    group by 1
),

 -- 2º Tabela temporária (campanha por contagem de leads)
lead_por_campanha as (

SELECT 
    campanha_id, 
    count (
        distinct lead_id
        ) 
        as lead_por_campanha 
    FROM leads group by 1

)

-- Select das tabelas temporárias com cálculo de custo/lead
SELECT 
t1.campanha_id, 
t1.custo_por_campanha, 
t2.lead_por_campanha,
round(
    t1.custo_por_campanha/t2.lead_por_campanha,2
    ) -- arredondar o valor para 2 casas decimais
as custo_lead_campanha
from custo_por_campanha t1
INNER JOIN lead_por_campanha t2 -- INNER (para campanha que existe duas tabelas ao mesmo tempo)
on t1.campanha_id = t2.campanha_id
order by round(
    t1.custo_por_campanha/t2.lead_por_campanha,2
    )asc -- ordena do melhor ao pior valor
