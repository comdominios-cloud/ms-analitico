# ms-analitico

Microservicio **analitico**: ejecuta consultas SQL sobre **AWS Athena** usando el
catalogo de **AWS Glue** y expone los resultados como API REST.

> CS2032 Cloud Computing - UTEC | Proyecto: Sistema de Administracion de Condominios

## Responsable

Integrante a cargo de **data science**. Trabaja junto con el repositorio
[`ingesta-datos`](../ingesta-datos), que es el que alimenta el bucket S3 sobre el
que corre Athena.

## Dominio

No tiene base de datos propia ni llama a los otros microservicios. Lee el **data
lake**: los CSV/JSON que los 3 contenedores de `ingesta-datos` depositan en S3,
catalogados por un crawler de AWS Glue y consultados con Athena.

```
MySQL / PostgreSQL / MongoDB
        │
        ▼  (ingesta-datos: 3 contenedores Python)
    Bucket S3 (CSV / JSON)
        │
        ▼  (crawler)
    AWS Glue Data Catalog
        │
        ▼  (SQL)
    AWS Athena ──> ms-analitico (8005) ──> API Gateway ──> web-condominio
```

Responde preguntas que ninguna API transaccional puede responder sola, porque
cruzan las tres bases: morosidad por edificio, recaudacion mensual, incidencias
por categoria y ocupacion de areas comunes.

## Stack

| Elemento    | Tecnologia                          |
|-------------|-------------------------------------|
| Lenguaje    | Python 3.12                         |
| Framework   | FastAPI                             |
| Motor de consultas | AWS Athena (via boto3)       |
| Catalogo    | AWS Glue Data Catalog               |
| Almacenamiento | Amazon S3                        |
| Base de datos propia | **Ninguna**                |
| Documentacion | Swagger-UI en `/docs`             |
| Contenedor  | Docker                              |

## Puerto asignado

**8005**

| Microservicio       | Puerto |
|---------------------|--------|
| ms-residentes       | 8001   |
| ms-pagos            | 8002   |
| ms-incidencias      | 8003   |
| ms-ficha-residente  | 8004   |
| ms-analitico        | **8005** |
| web-condominio (dev)| 5173   |

## Endpoints REST planificados

> Andamiaje: aun no implementados. Cada endpoint corresponde a un archivo de
> [`queries/`](queries/).

| # | Metodo | Ruta | Consulta que ejecuta | Consumido por |
|---|--------|------|----------------------|---------------|
| 1 | `GET` | `/analitica/morosidad-por-edificio` | `query01_morosidad_por_edificio.sql` | **frontend** |
| 2 | `GET` | `/analitica/recaudacion-mensual?desde=&hasta=` | `query02_recaudacion_mensual.sql` | **frontend** |
| 3 | `GET` | `/analitica/incidencias-por-categoria` | `query03_incidencias_por_categoria.sql` | frontend |
| 4 | `GET` | `/analitica/ocupacion-areas-comunes` | `query04_ocupacion_areas_comunes.sql` | frontend |
| 5 | `POST`| `/athena/consultas` | Lanza una consulta y devuelve su `queryExecutionId` | frontend |
| 6 | `GET` | `/athena/consultas/{execution_id}` | Estado y resultados de una consulta lanzada | frontend |
| 7 | `GET` | `/health` | Health check del servicio | infra |

Los dos endpoints que consume directamente el **frontend** son
`GET /analitica/morosidad-por-edificio` y `GET /analitica/recaudacion-mensual`.

Documentacion interactiva: `http://localhost:8005/docs` (Swagger-UI).

## Consultas y vistas

En [`queries/`](queries/) estan los placeholders de las **4 consultas** y las
**2 vistas** de Athena exigidas por el curso. Detalle en
[queries/README.md](queries/README.md).

## Variables de entorno

Copiar [.env.example](.env.example) a `.env` y completar. **Nunca** commitear `.env`
ni credenciales de AWS.

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `APP_NAME` | Nombre del servicio | `ms-analitico` |
| `APP_PORT` | Puerto de escucha | `8005` |
| `APP_ENV` | Entorno de ejecucion | `development` / `production` |
| `LOG_LEVEL` | Nivel de logging | `info` |
| `AWS_REGION` | Region de AWS | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Access key | *(sin valor en el repo)* |
| `AWS_SECRET_ACCESS_KEY` | Secret key | *(sin valor en el repo)* |
| `AWS_SESSION_TOKEN` | Token de sesion (AWS Academy) | *(sin valor en el repo)* |
| `GLUE_DATABASE` | Base del catalogo de Glue | `condominio_db` |
| `GLUE_CATALOG_ID` | Id del catalogo (opcional) | *(vacio = cuenta actual)* |
| `ATHENA_WORKGROUP` | Workgroup de Athena | `primary` |
| `ATHENA_OUTPUT_S3` | Bucket de resultados de Athena | `s3://BUCKET/athena-results/` |
| `DATA_LAKE_S3` | Bucket con los datos crudos de ingesta | `s3://BUCKET/raw/` |
| `ATHENA_QUERY_TIMEOUT` | Espera maxima por consulta (s) | `60` |

> **Credenciales:** en la EC2 lo correcto es adjuntar un **IAM Role** con permisos
> de Athena/Glue/S3 en vez de llaves estaticas. Las variables `AWS_*` estan solo
> para desarrollo local o para las credenciales temporales de AWS Academy.

## Como levantar con Docker

```bash
cp .env.example .env      # completar region, buckets y credenciales
docker build -t ms-analitico .
docker run --rm -p 8005:8005 --env-file .env ms-analitico
```

Luego abrir `http://localhost:8005/docs`.

### En la EC2 (docker compose del proyecto)

```yaml
services:
  ms-analitico:
    build: .
    ports: ["8005:8005"]
    env_file: .env
```

```bash
docker compose up --build
```

## Estructura

```
app/
├── main.py       # instancia FastAPI (stub)
├── routers/      # endpoints analiticos
├── athena/       # cliente boto3: ejecutar consulta y esperar resultado
├── schemas/      # esquemas Pydantic de las respuestas
└── config/       # settings de AWS, Glue y Athena
queries/
├── query01..query04_*.sql   # 4 consultas (placeholders)
└── view01..view02_*.sql     # 2 vistas de Athena (placeholders)
tests/
```

## Estado

Andamiaje inicial. Sin endpoints, sin cliente de Athena y con las consultas SQL
como placeholders.
