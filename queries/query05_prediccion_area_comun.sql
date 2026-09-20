-- ============================================================
-- Consulta 5: prediccion del area comun mas visitada el proximo mes
-- ------------------------------------------------------------
-- Requerimiento que pidio el ACL:
--   "Integrar la tendencia de los usuarios a las areas comunes.
--    Calcular que area comun sera la mas visitada el siguiente mes."
--
-- Enfoque: se cuentan las reservas por area y por mes, se calcula la
-- tendencia con funciones de ventana (promedio movil de 3 meses y variacion
-- contra el mes anterior) y se proyecta el mes siguiente sumando la tendencia
-- al promedio movil. Gana el area con la proyeccion mas alta.
--
-- Es una proyeccion lineal simple, no un modelo estadistico: con pocos meses
-- de historia es lo razonable, y se explica en una linea.
-- ============================================================

WITH por_mes AS (
    SELECT
        r.area_comun,
        date_trunc('month', from_iso8601_timestamp(r.fecha_inicio)) AS mes,
        COUNT(*) AS visitas
    FROM reservas r
    WHERE r.fecha_inicio IS NOT NULL
      AND r.estado IN ('CONFIRMADA', 'COMPLETADA')
    GROUP BY r.area_comun,
             date_trunc('month', from_iso8601_timestamp(r.fecha_inicio))
),
tendencia AS (
    SELECT
        area_comun,
        mes,
        visitas,
        LAG(visitas) OVER (PARTITION BY area_comun ORDER BY mes) AS mes_anterior,
        AVG(CAST(visitas AS DOUBLE)) OVER (
            PARTITION BY area_comun ORDER BY mes
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS promedio_3m
    FROM por_mes
),
ultimo AS (
    SELECT
        area_comun,
        mes,
        visitas,
        mes_anterior,
        promedio_3m,
        ROW_NUMBER() OVER (PARTITION BY area_comun ORDER BY mes DESC) AS orden
    FROM tendencia
)
SELECT
    area_comun,
    mes                                                   AS ultimo_mes,
    visitas                                               AS visitas_ultimo_mes,
    ROUND(promedio_3m, 2)                                 AS promedio_3_meses,
    COALESCE(visitas - mes_anterior, 0)                   AS variacion_vs_mes_anterior,
    GREATEST(
        ROUND(promedio_3m + COALESCE(visitas - mes_anterior, 0), 0),
        0
    )                                                     AS proyeccion_proximo_mes
FROM ultimo
WHERE orden = 1
ORDER BY proyeccion_proximo_mes DESC
