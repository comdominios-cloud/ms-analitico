-- ============================================================
-- Consulta 2: recaudacion mensual
-- ------------------------------------------------------------
-- Une cuotas y pagos.
--
-- Responde: mes a mes, cuanto se emitio en cuotas contra cuanto se cobro
-- realmente, y que porcentaje de cobranza representa.
-- ============================================================

WITH emitido AS (
    SELECT
        c.periodo                                   AS periodo,
        SUM(CAST(c.monto AS DECIMAL(12,2)))         AS monto_emitido,
        COUNT(*)                                    AS cuotas_emitidas
    FROM cuotas c
    GROUP BY c.periodo
),
cobrado AS (
    SELECT
        c.periodo                                        AS periodo,
        SUM(CAST(p.monto_pagado AS DECIMAL(12,2)))       AS monto_cobrado,
        COUNT(*)                                         AS pagos_registrados
    FROM pagos p
    JOIN cuotas c ON CAST(c.id AS BIGINT) = CAST(p.cuota_id AS BIGINT)
    GROUP BY c.periodo
)
SELECT
    e.periodo,
    ROUND(e.monto_emitido, 2)                     AS monto_emitido,
    ROUND(COALESCE(c.monto_cobrado, 0), 2)        AS monto_cobrado,
    ROUND(e.monto_emitido - COALESCE(c.monto_cobrado, 0), 2) AS saldo_pendiente,
    e.cuotas_emitidas,
    COALESCE(c.pagos_registrados, 0)              AS pagos_registrados,
    ROUND(100.0 * COALESCE(c.monto_cobrado, 0) / NULLIF(e.monto_emitido, 0), 2)
                                                  AS pct_cobranza
FROM emitido e
LEFT JOIN cobrado c ON c.periodo = e.periodo
ORDER BY e.periodo
