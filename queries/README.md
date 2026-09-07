# Consultas de Athena - ms-analitico

Cada archivo `.sql` de esta carpeta es un **placeholder**: contiene el objetivo
de la consulta y un esqueleto SQL comentado. Se completan cuando el catalogo de
AWS Glue este creado sobre los datos que `ingesta-datos` sube a S3.

## Tablas esperadas en el catalogo de Glue

Provienen de los 3 contenedores de ingesta:

| Tabla de Glue | Origen | Formato en S3 |
|---------------|--------|---------------|
| `edificios`, `unidades`, `residentes`, `usuarios` | ms-residentes (PostgreSQL) | CSV |
| `cuotas`, `pagos` | ms-pagos (MySQL) | CSV |
| `incidencias`, `reservas` | ms-incidencias (MongoDB) | JSON |

## Contenido

| Archivo | Tipo | Objetivo |
|---------|------|----------|
| `query01_morosidad_por_edificio.sql` | consulta | Deuda y tasa de morosidad por edificio |
| `query02_recaudacion_mensual.sql` | consulta | Recaudacion mes a mes y comparativa con lo emitido |
| `query03_incidencias_por_categoria.sql` | consulta | Volumen y tiempo de resolucion de incidencias por categoria |
| `query04_ocupacion_areas_comunes.sql` | consulta | Uso de las areas comunes por franja horaria |
| `query05_prediccion_area_comun.sql` | consulta | **Que area comun sera la mas visitada el proximo mes** (pedido del ACL) |
| `view01_vw_estado_cuenta_unidad.sql` | vista | Estado de cuenta consolidado por unidad |
| `view02_vw_actividad_residente.sql` | vista | Actividad de cada residente (pagos + incidencias + reservas) |

## Como ejecutar

Desde la consola de Athena, seleccionando la base `condominio_db` y el workgroup
configurado en `ATHENA_WORKGROUP`; o desde este microservicio, que las ejecuta
con `boto3` (`start_query_execution` + polling de `get_query_execution`).
