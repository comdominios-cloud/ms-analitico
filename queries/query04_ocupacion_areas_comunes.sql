-- ============================================================
-- Consulta 4: ocupacion de las areas comunes
-- ------------------------------------------------------------
-- Une reservas (MongoDB) con unidades y edificios (PostgreSQL).
--
-- Responde: que area comun se usa mas, en que dia de la semana, y que
-- porcentaje de las reservas termina cancelado.
-- ============================================================

WITH reservas_normalizadas AS (
    SELECT
        r.area_comun,
        r.estado,
        CAST(r.unidad_id AS BIGINT)                          AS unidad_id,
        from_iso8601_timestamp(r.fecha_inicio)               AS inicio
    FROM reservas r
    WHERE r.fecha_inicio IS NOT NULL
)
SELECT
    e.nombre                                     AS edificio,
    r.area_comun                                 AS area_comun,
    day_of_week(r.inicio)                        AS dia_semana,
    COUNT(*)                                     AS total_reservas,
    SUM(CASE WHEN r.estado = 'CANCELADA' THEN 1 ELSE 0 END) AS canceladas,
    ROUND(
        100.0 * SUM(CASE WHEN r.estado = 'CANCELADA' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
    , 2)                                         AS pct_canceladas
FROM reservas_normalizadas r
JOIN unidades  u ON CAST(u.id AS BIGINT) = r.unidad_id
JOIN edificios e ON CAST(e.id AS BIGINT) = CAST(u.edificio_id AS BIGINT)
GROUP BY e.nombre, r.area_comun, day_of_week(r.inicio)
ORDER BY total_reservas DESC
