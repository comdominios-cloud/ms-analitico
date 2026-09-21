"""Contratos de salida del microservicio analitico."""

from typing import Any

from pydantic import BaseModel, Field


class RespuestaConsulta(BaseModel):
    consulta: str
    execution_id: str
    estado: str
    columnas: list[str]
    filas: list[dict[str, Any]]
    total_filas: int
    ms_ejecucion: int | None = None
    datos_escaneados_bytes: int | None = None


class ConsultaDisponible(BaseModel):
    nombre: str
    archivo: str
    endpoint: str


class Catalogo(BaseModel):
    base_glue: str
    workgroup: str
    consultas: list[ConsultaDisponible]
    vistas: list[ConsultaDisponible]


class EjecucionLanzada(BaseModel):
    execution_id: str
    estado: str = "QUEUED"
    detalle: str = Field(
        default="Consultar GET /athena/consultas/{execution_id} para el resultado"
    )


class SqlDeConsulta(BaseModel):
    nombre: str
    archivo: str
    sql: str
