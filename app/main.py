"""Punto de entrada de ms-analitico.

Microservicio analitico: ejecuta consultas SQL sobre AWS Athena usando el
catalogo de AWS Glue, construido a partir de los archivos CSV/JSON que
ingesta-datos deposita en S3.

Responde preguntas que ninguna API transaccional puede responder sola, porque
cruzan las tres bases del proyecto: PostgreSQL, MySQL y MongoDB.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analitica, athena, salud

settings = get_settings()

app = FastAPI(
    title="ms-analitico",
    description=(
        "Microservicio analitico. Ejecuta consultas sobre **AWS Athena** usando "
        "el catalogo de **AWS Glue**.\n\n"
        "Las consultas viven en archivos `.sql` dentro de `queries/`, no "
        "incrustadas en el codigo: asi se pueden revisar y ejecutar tal cual en "
        "la consola de Athena. `GET /analitica/sql/{nombre}` devuelve el SQL de "
        "cada una sin ejecutarla."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(salud.router)
app.include_router(analitica.router)
app.include_router(athena.router)
