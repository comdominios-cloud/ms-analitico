# Integrante responsable

| | |
|---|---|
| **Repositorio** | `ms-analitico` |
| **Integrante** | [@carloscondor1610](https://github.com/carloscondor1610) |
| **Rol** | Data Science |
| **Puerto** | 9005 publicado, 8005 interno |

## Alcance

`ms-analitico`: consultas y vistas de Athena sobre el catalogo de Glue. Va junto con [ingesta-datos](https://github.com/comdominios-cloud/ingesta-datos), que es tu prioridad para este avance.

> ### Esto va DESPUES del avance del 50%
>
> Para la entrega del 12/09 tu trabajo esta en
> [ingesta-datos](https://github.com/comdominios-cloud/ingesta-datos): VM de
> ingesta, bucket S3 y un contenedor con datos reales en S3. Glue, Athena y las
> consultas vienen despues, cuando haya datos en el bucket.
>
> Ojo con [queries/query05_prediccion_area_comun.sql](queries/query05_prediccion_area_comun.sql):
> es el requerimiento que pidio el ACL de predecir **que area comun sera la mas
> visitada el proximo mes**, y depende de `ingesta03` (las reservas viven en Mongo).

## Avance del 50% — entrega del 6 al 12 de septiembre

- [ ] Crawler de **Glue** sobre el bucket S3, base `condominio_db`
- [ ] Las **4 consultas** de [queries/](queries/) escritas y ejecutando en Athena
- [ ] Las **2 vistas** creadas
- [ ] La **5a consulta**: prediccion del area comun mas visitada
- [ ] Microservicio publicado en el puerto **9005** exponiendo los resultados
- [ ] Imagen en **Docker Hub**

---

## Como trabajamos

Cada repositorio pertenece a un integrante y se desarrolla de forma
**independiente**: las APIs con base de datos no se llaman entre si. La unica
integracion entre microservicios vive en `ms-ficha-residente`, y la del lado del
usuario en `web-condominio`.

Los cambios a este repositorio los define su responsable. Si otro integrante
necesita algo de esta API, se pide via issue en vez de tocar el codigo.

## Equipo

| Repositorio | Integrante | Rol | Puerto |
|---|---|---|---|
| [ms-residentes](https://github.com/comdominios-cloud/ms-residentes) | @Osomar1705 | API con BD - Python / PostgreSQL | 9001 |
| [ms-pagos](https://github.com/comdominios-cloud/ms-pagos) | @sebastianperez72 | API con BD - Java / MySQL | 9002 |
| [ms-incidencias](https://github.com/comdominios-cloud/ms-incidencias) | @fabianbot1331 | API con BD - lenguaje por definir / MongoDB | 9003 |
| [ms-ficha-residente](https://github.com/comdominios-cloud/ms-ficha-residente) | @Brisseth-raton | Backend / Infraestructura | 9004 |
| [web-condominio](https://github.com/comdominios-cloud/web-condominio) | @alxgr-08 | Frontend / Amplify | 5173 (dev) |
| [ms-analitico](https://github.com/comdominios-cloud/ms-analitico) | @carloscondor1610 | Data Science | 9005 |
| [ingesta-datos](https://github.com/comdominios-cloud/ingesta-datos) | @carloscondor1610 | Data Science | — |

> CS2032 Cloud Computing - UTEC | Sistema de Administracion de Condominios
