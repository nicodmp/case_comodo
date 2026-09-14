WITH stage_counts AS (
    SELECT
        etapa_atua,
        campanha_id,
        CASE
            WHEN etapa_atua = 'novo' THEN 1
            WHEN etapa_atua = 'qualificado' THEN 2
            WHEN etapa_atua = 'em_atendimento' THEN 3
            WHEN etapa_atua = 'briefing_realizado' THEN 4
            WHEN etapa_atua = 'proposta' THEN 5
            WHEN etapa_atua = 'vendido' THEN 6
            WHEN etapa_atua = 'perdido' THEN 7
        END AS stage_order,
        COUNT(DISTINCT lead_id) AS total_leads
    FROM "trading_data_mngmt_index_data_dev"."leads"
    WHERE etapa_atua <> 'perdido'
    GROUP BY
        campanha_id,
        etapa_atua
),

funnel AS (
    SELECT
        campanha_id,
        etapa_atua,
        stage_order,
        total_leads,
        LEAD(total_leads) OVER (
            PARTITION BY campanha_id
            ORDER BY stage_order
        ) AS leads_next_stage
    FROM stage_counts
)

SELECT
    campanha_id,
    etapa_atua,
    total_leads,
    leads_next_stage,
    ROUND(
        100.0 * (total_leads - leads_next_stage)
        / NULLIF(total_leads, 0),
        2
    ) AS loss_percentage
FROM funnel
ORDER BY
    campanha_id,
    stage_order;
