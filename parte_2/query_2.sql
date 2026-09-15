WITH contagem_stage AS ( -- CTE que busca quantos leads por campanha e define numeros para as etapas
    SELECT
        etapa_atual,
        campanha_id,
        -- Definir as ordem da etapas
        CASE
            WHEN etapa_atual = 'novo' THEN 1
            WHEN etapa_atual = 'qualificado' THEN 2
            WHEN etapa_atual = 'em_atendimento' THEN 3
            WHEN etapa_atual = 'briefing_realizado' THEN 4
            WHEN etapa_atual = 'proposta' THEN 5
            WHEN etapa_atual = 'vendido' THEN 6
            WHEN etapa_atual = 'perdido' THEN 7
        END AS ordem_etapa,
        COUNT(DISTINCT lead_id) AS total_leads
    FROM leads
    WHERE etapa_atual <> 'perdido' -- remove os perdidos
    GROUP BY
        campanha_id,
        etapa_atual
),
-- Criar o funil
funnel AS (
    SELECT
        campanha_id,
        etapa_atual,
        ordem_etapa,
        total_leads,
        LEAD(total_leads) OVER ( -- Window function que traz o próximo lead na ordem predefinida, ex: ordem_etapa = 1 vai retornar o valor da ordem etapa = 2
            PARTITION BY campanha_id
            ORDER BY ordem_etapa
        ) AS leads_proxima_etapa
    FROM contagem_stage
)

SELECT
    campanha_id,
    etapa_atual,
    total_leads,
    leads_proxima_etapa,
    ROUND(
        100.0 * (total_leads - leads_proxima_etapa)
        / NULLIF(total_leads, 0),
        2
    ) AS perda_percentual
FROM funnel
ORDER BY
    campanha_id,
    ordem_etapa;
