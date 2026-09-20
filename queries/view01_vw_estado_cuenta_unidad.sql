-- ============================================================
-- Vista 1: vw_estado_cuenta_unidad
-- ------------------------------------------------------------
-- Una fila por unidad con su edificio, lo emitido, lo pagado, el saldo y la
-- cantidad de cuotas impagas.
--
-- Cruza PostgreSQL (edificios, unidades) con MySQL (cuotas, pagos). Sirve de
-- base para la consulta de morosidad y para los tableros del frontend.
-- ============================================================

CREATE OR REPLACE VIEW vw_estado_cuenta_unidad AS
WITH pagado_por_cuota AS (
    SELECT
        CAST(p.cuota_id AS BIGINT)                 AS cuota_id,
        SUM(CAST(p.monto_pagado AS DECIMAL(12,2))) AS pagado
    FROM pagos p
    GROUP BY CAST(p.cuota_id AS BIGINT)
)
SELECT
    CAST(u.id AS BIGINT)                          AS unidad_id,
    u.codigo                                      AS unidad,
    e.nombre                                      AS edificio,
    CAST(u.piso AS INTEGER)                       AS piso,
    COUNT(c.id)                                   AS cuotas_emitidas,
    ROUND(COALESCE(SUM(CAST(c.monto AS DECIMAL(12,2))), 0), 2)  AS total_emitido,
    ROUND(COALESCE(SUM(pc.pagado), 0), 2)                       AS total_pagado,
    ROUND(
        COALESCE(SUM(CAST(c.monto AS DECIMAL(12,2))), 0)
        - COALESCE(SUM(pc.pagado), 0)
    , 2)                                          AS saldo_pendiente,
    SUM(CASE
            WHEN CAST(c.monto AS DECIMAL(12,2)) - COALESCE(pc.pagado, 0) > 0
            THEN 1 ELSE 0
        END)                                      AS cuotas_impagas
FROM unidades u
JOIN edificios e          ON CAST(e.id AS BIGINT) = CAST(u.edificio_id AS BIGINT)
LEFT JOIN cuotas c        ON CAST(c.unidad_id AS BIGINT) = CAST(u.id AS BIGINT)
LEFT JOIN pagado_por_cuota pc ON pc.cuota_id = CAST(c.id AS BIGINT)
GROUP BY CAST(u.id AS BIGINT), u.codigo, e.nombre, CAST(u.piso AS INTEGER)
