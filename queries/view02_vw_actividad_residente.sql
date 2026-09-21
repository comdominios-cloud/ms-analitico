-- ============================================================
-- Vista 2: vw_actividad_residente
-- ------------------------------------------------------------
-- Una fila por residente cruzando las TRES bases: sus datos y su unidad
-- (PostgreSQL), sus pagos (MySQL), y sus incidencias y reservas (MongoDB).
--
-- Es la version analitica y en lote de lo que ms-ficha-residente resuelve en
-- linea para un residente puntual.
-- ============================================================

CREATE OR REPLACE VIEW vw_actividad_residente AS
WITH pagos_por_unidad AS (
    SELECT
        CAST(c.unidad_id AS BIGINT)                AS unidad_id,
        COUNT(p.id)                                AS pagos_realizados,
        SUM(CAST(p.monto_pagado AS DECIMAL(12,2))) AS monto_pagado
    FROM cuotas c
    JOIN pagos p ON CAST(p.cuota_id AS BIGINT) = CAST(c.id AS BIGINT)
    GROUP BY CAST(c.unidad_id AS BIGINT)
),
incidencias_por_residente AS (
    SELECT
        CAST(i.residente_id AS BIGINT) AS residente_id,
        COUNT(*)                       AS incidencias_reportadas,
        SUM(CASE WHEN i.estado IN ('ABIERTA', 'EN_PROCESO') THEN 1 ELSE 0 END)
                                       AS incidencias_abiertas
    FROM incidencias i
    WHERE i.residente_id IS NOT NULL
    GROUP BY CAST(i.residente_id AS BIGINT)
),
reservas_por_residente AS (
    SELECT
        CAST(v.residente_id AS BIGINT) AS residente_id,
        COUNT(*)                       AS reservas_realizadas
    FROM reservas v
    WHERE v.residente_id IS NOT NULL
    GROUP BY CAST(v.residente_id AS BIGINT)
)
SELECT
    CAST(r.id AS BIGINT)                       AS residente_id,
    r.nombres,
    r.apellidos,
    r.tipo                                     AS tipo_residente,
    u.codigo                                   AS unidad,
    e.nombre                                   AS edificio,
    COALESCE(pu.pagos_realizados, 0)           AS pagos_realizados,
    ROUND(COALESCE(pu.monto_pagado, 0), 2)     AS monto_pagado,
    COALESCE(ir.incidencias_reportadas, 0)     AS incidencias_reportadas,
    COALESCE(ir.incidencias_abiertas, 0)       AS incidencias_abiertas,
    COALESCE(rr.reservas_realizadas, 0)        AS reservas_realizadas
FROM residentes r
JOIN unidades  u ON CAST(u.id AS BIGINT) = CAST(r.unidad_id AS BIGINT)
JOIN edificios e ON CAST(e.id AS BIGINT) = CAST(u.edificio_id AS BIGINT)
LEFT JOIN pagos_por_unidad          pu ON pu.unidad_id   = CAST(u.id AS BIGINT)
LEFT JOIN incidencias_por_residente ir ON ir.residente_id = CAST(r.id AS BIGINT)
LEFT JOIN reservas_por_residente    rr ON rr.residente_id = CAST(r.id AS BIGINT)
