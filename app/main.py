"""Punto de entrada de ms-analitico.

ANDAMIAJE: solo instancia la aplicacion FastAPI y expone Swagger-UI.
Este microservicio no tiene base de datos propia: ejecuta consultas SQL
sobre AWS Athena (catalogo de AWS Glue) y devuelve los resultados.
"""

from fastapi import FastAPI

app = FastAPI(
    title="ms-analitico",
    description=(
        "Microservicio analitico. Ejecuta consultas sobre AWS Athena usando el "
        "catalogo de AWS Glue construido a partir de los datos que ingesta-datos "
        "deposita en S3."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "ms-analitico"}


# TODO: app.include_router(...) por cada router de app/routers/
# TODO: cliente boto3 de Athena en app/athena/ (start_query_execution + polling)
