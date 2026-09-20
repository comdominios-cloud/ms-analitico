"""Ejecucion de consultas en AWS Athena.

Athena no es sincronico: se lanza la consulta, devuelve un identificador, y hay
que preguntar por el estado hasta que termine. Este modulo encapsula ese ciclo
y devuelve los resultados ya convertidos a diccionarios.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings

settings = get_settings()

ESTADOS_FINALES = {"SUCCEEDED", "FAILED", "CANCELLED"}


class AthenaNoConfigurado(RuntimeError):
    """Falta ATHENA_OUTPUT_S3: Athena necesita donde dejar los resultados."""


class AthenaError(RuntimeError):
    """La consulta fallo, se cancelo o no termino a tiempo."""


@dataclass
class Resultado:
    execution_id: str
    estado: str
    filas: list[dict[str, Any]] = field(default_factory=list)
    columnas: list[str] = field(default_factory=list)
    ms_ejecucion: int | None = None
    datos_escaneados: int | None = None


def _cliente():
    if not settings.configurado:
        raise AthenaNoConfigurado(
            "Falta configurar ATHENA_OUTPUT_S3 con el bucket de resultados de Athena"
        )
    return boto3.client("athena", region_name=settings.aws_region)


def lanzar(sql: str) -> str:
    """Inicia la consulta y devuelve su identificador de ejecucion."""
    try:
        r = _cliente().start_query_execution(
            QueryString=sql,
            QueryExecutionContext={"Database": settings.glue_database},
            WorkGroup=settings.athena_workgroup,
            ResultConfiguration={"OutputLocation": settings.athena_output_s3},
        )
    except (BotoCoreError, ClientError) as e:
        raise AthenaError(f"No se pudo lanzar la consulta: {e}") from e

    return r["QueryExecutionId"]


def estado(execution_id: str) -> dict:
    try:
        r = _cliente().get_query_execution(QueryExecutionId=execution_id)
    except (BotoCoreError, ClientError) as e:
        raise AthenaError(f"No se pudo consultar el estado: {e}") from e

    ejecucion = r["QueryExecution"]
    estado_actual = ejecucion["Status"]["State"]
    estadisticas = ejecucion.get("Statistics", {})

    return {
        "estado": estado_actual,
        "motivo": ejecucion["Status"].get("StateChangeReason"),
        "ms_ejecucion": estadisticas.get("EngineExecutionTimeInMillis"),
        "datos_escaneados": estadisticas.get("DataScannedInBytes"),
    }


def resultados(execution_id: str, limite: int = 1000) -> tuple[list[str], list[dict]]:
    """Trae los resultados paginando, y arma diccionarios con los nombres de columna."""
    try:
        paginador = _cliente().get_paginator("get_query_results")
        columnas: list[str] = []
        filas: list[dict] = []

        for pagina in paginador.paginate(
            QueryExecutionId=execution_id, PaginationConfig={"MaxItems": limite}
        ):
            if not columnas:
                columnas = [
                    c["Name"]
                    for c in pagina["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
                ]

            for i, fila in enumerate(pagina["ResultSet"]["Rows"]):
                # Athena devuelve la cabecera como primera fila de la primera pagina.
                if not filas and i == 0:
                    continue
                valores = [celda.get("VarCharValue") for celda in fila["Data"]]
                filas.append(dict(zip(columnas, valores)))
    except (BotoCoreError, ClientError) as e:
        raise AthenaError(f"No se pudieron leer los resultados: {e}") from e

    return columnas, filas


async def ejecutar(sql: str, limite: int = 1000) -> Resultado:
    """Lanza la consulta, espera a que termine y devuelve los resultados."""
    execution_id = await asyncio.to_thread(lanzar, sql)

    esperado = 0.0
    info: dict = {}

    while esperado < settings.athena_query_timeout:
        info = await asyncio.to_thread(estado, execution_id)

        if info["estado"] in ESTADOS_FINALES:
            break

        await asyncio.sleep(settings.athena_poll_seconds)
        esperado += settings.athena_poll_seconds
    else:
        raise AthenaError(
            f"La consulta no termino en {settings.athena_query_timeout}s "
            f"(execution_id {execution_id})"
        )

    if info["estado"] != "SUCCEEDED":
        raise AthenaError(
            f"La consulta termino en {info['estado']}: {info.get('motivo') or 'sin detalle'}"
        )

    columnas, filas = await asyncio.to_thread(resultados, execution_id, limite)

    return Resultado(
        execution_id=execution_id,
        estado=info["estado"],
        columnas=columnas,
        filas=filas,
        ms_ejecucion=info.get("ms_ejecucion"),
        datos_escaneados=info.get("datos_escaneados"),
    )
