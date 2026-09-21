-- ============================================================
-- Consulta 3: incidencias por categoria y edificio
-- ------------------------------------------------------------
-- Une 3 tablas de DOS motores distintos: incidencias viene de MongoDB
-- (ms-incidencias) y unidades y edificios de PostgreSQL (ms-residentes).
--
-- Responde: que tipo de problema se reporta mas en cada edificio, con que
-- prioridad, y cuantos siguen sin resolver.
-- ============================================================

SELECT
    e.nombre                          AS edificio,
    i.categoria                       AS categoria,
    i.prioridad                       AS prioridad,
    COUNT(*)                          AS total,
    SUM(CASE WHEN i.estado IN ('ABIERTA', 'EN_PROCESO') THEN 1 ELSE 0 END)
                                      AS sin_resolver,
    SUM(CASE WHEN i.estado IN ('RESUELTA', 'CERRADA') THEN 1 ELSE 0 END)
                                      AS resueltas,
    ROUND(
        100.0 * SUM(CASE WHEN i.estado IN ('RESUELTA', 'CERRADA') THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
    , 2)                              AS pct_resolucion
FROM incidencias i
JOIN unidades  u ON CAST(u.id AS BIGINT) = CAST(i.unidad_id AS BIGINT)
JOIN edificios e ON CAST(e.id AS BIGINT) = CAST(u.edificio_id AS BIGINT)
GROUP BY e.nombre, i.categoria, i.prioridad
ORDER BY total DESC, edificio
