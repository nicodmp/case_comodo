WITH soma_contrato as ( -- lead por valor total do contrato
SELECT lead_id, sum(cast(valor_contrato as double)) as soma_contrato FROM vendas group by 1
),

soma_contrato_campanha as ( -- mesma tabela de cima com a coluna campanha_id

select t1.*,t2.campanha_id from soma_contrato t1
left join leads t2
on t1.lead_id = t2.lead_id
),

soma_contrato_campanha_lead as ( --soma o total de contratos da campanha e calcula quantidade de leads, e já calcula o ticket medio

select campanha_id, 
sum(soma_contrato) as receita_total, 
count (distinct lead_id) as contagem_leads, 
round(sum(soma_contrato)/count (distinct lead_id),2) as ticket_medio, 
max(soma_contrato) as cliente_maior_valor
from soma_contrato_campanha
group by 1
order by 5 desc
)

select campanha_id, receita_total, contagem_leads, ticket_medio, cliente_maior_valor, t2.lead_id as maior_cliente
from soma_contrato_campanha_lead t1
left join soma_contrato t2
on t1.cliente_maior_valor = t2.soma_contrato
order by cliente_maior_valor desc -- garante que o primeiro da lista seja o de maior valor
