-- ============================================================
-- Consulta 1: morosidad por edificio
-- ------------------------------------------------------------
-- Une 4 tablas del catalogo: edificios, unidades, cuotas y pagos.
--
-- Responde: por cada edificio, cuanta deuda hay acumulada y que porcentaje
-- de sus unidades tiene al menos una cuota sin cancelar del todo.
--
-- Esta pregunta no la puede responder ningun microservicio solo: los
-- edificios y unidades viven en PostgreSQL (ms-residentes) y las cuotas y
-- pagos en MySQL (ms-pagos). Solo se cruzan aca, sobre los archivos en S3.
-- ============================================================

WITH pagado_por_cuota AS (
    SELECT
        CAST(p.cuota_id AS BIGINT)            AS cuota_id,
        SUM(CAST(p.monto_pagado AS DECIMAL(12,2))) AS pagado
    FROM pagos p
    GROUP BY CAST(p.cuota_id AS BIGINT)
),
saldo_por_unidad AS (
    SELECT
        CAST(c.unidad_id AS BIGINT) AS unidad_id,
        SUM(CAST(c.monto AS DECIMAL(12,2)) - COALESCE(pc.pagado, 0)) AS saldo,
        SUM(CASE
                WHEN CAST(c.monto AS DECIMAL(12,2)) - COALESCE(pc.pagado, 0) > 0
                THEN 1 ELSE 0
            END) AS cuotas_impagas
    FROM cuotas c
    LEFT JOIN pagado_por_cuota pc ON pc.cuota_id = CAST(c.id AS BIGINT)
    GROUP BY CAST(c.unidad_id AS BIGINT)
)
SELECT
    e.nombre                                   AS edificio,
    COUNT(DISTINCT u.id)                       AS unidades_totales,
    COUNT(DISTINCT CASE WHEN s.cuotas_impagas > 0 THEN u.id END) AS unidades_morosas,
    ROUND(COALESCE(SUM(s.saldo), 0), 2)        AS deuda_total,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN s.cuotas_impagas > 0 THEN u.id END)
        / NULLIF(COUNT(DISTINCT u.id), 0)
    , 2)                                       AS tasa_morosidad_pct
FROM edificios e
JOIN unidades u        ON CAST(u.edificio_id AS BIGINT) = CAST(e.id AS BIGINT)
LEFT JOIN saldo_por_unidad s ON s.unidad_id = CAST(u.id AS BIGINT)
GROUP BY e.nombre
ORDER BY deuda_total DESC
