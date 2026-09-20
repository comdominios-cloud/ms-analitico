# Consultas de Athena - ms-analitico

Cada archivo `.sql` de esta carpeta contiene una consulta **completa y lista
para ejecutar** en Athena. El microservicio las lee de aca en tiempo de
ejecucion: no estan incrustadas en el codigo, asi se pueden revisar, versionar
y correr tal cual en la consola de Athena.

`GET /analitica/sql/{nombre}` devuelve el SQL de cada una sin ejecutarla.

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

Tres formas:

1. **Desde el microservicio**, que es lo habitual:
   `GET /analitica/morosidad-por-edificio`
2. **Desde la consola de Athena**, copiando el contenido del archivo y
   seleccionando la base `condominio_db`.
3. **De forma asincronica**, para consultas largas:
   `POST /athena/consultas?nombre=...` devuelve un `execution_id`, y
   `GET /athena/consultas/{execution_id}` trae el resultado cuando termina.

Las vistas se crean con `POST /analitica/vistas/{nombre}`.

## Sobre los CAST

El crawler de Glue infiere los tipos de los CSV, y no siempre acierta con los
numericos. Por eso las consultas hacen `CAST` explicito en los campos que se
suman o se comparan: asi funcionan igual si el catalogo los dejo como texto.

## Por que estas consultas necesitan Athena

Las cinco cruzan tablas que viven en **bases distintas**: `edificios`,
`unidades` y `residentes` en PostgreSQL; `cuotas` y `pagos` en MySQL;
`incidencias` y `reservas` en MongoDB.

Ningun microservicio puede hacer ese JOIN, porque cada uno solo ve su propia
base. Recien cuando `ingesta-datos` vuelca todo a S3 y Glue lo cataloga como
tablas, Athena puede consultarlas juntas.
