"""Acceso directo a Athena: lanzar una consulta y recuperar su resultado.

Separado de los endpoints analiticos porque aca la ejecucion es asincronica:
se lanza, devuelve el identificador, y se consulta despues. Sirve para
consultas largas, donde esperar la respuesta en el mismo request no es viable.
"""

import asyncio

from fastapi import APIRouter, HTTPException, Query, status

from app.athena import (
    CATALOGO,
    AthenaError,
    AthenaNoConfigurado,
    estado,
    lanzar,
    resultados,
    sql_de_consulta,
)
from app.schemas import EjecucionLanzada

router = APIRouter(prefix="/athena", tags=["athena"])


@router.post(
    "/consultas",
    response_model=EjecucionLanzada,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Lanzar una consulta sin esperar el resultado",
)
async def lanzar_consulta(nombre: str = Query(description="Nombre de la consulta")) -> EjecucionLanzada:
    if nombre not in CATALOGO:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Consulta desconocida: {nombre}")

    try:
        execution_id = await asyncio.to_thread(lanzar, sql_de_consulta(nombre))
    except AthenaNoConfigurado as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e)) from e
    except AthenaError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return EjecucionLanzada(execution_id=execution_id)


@router.get(
    "/consultas/{execution_id}",
    summary="Estado y resultados de una consulta lanzada",
)
async def resultado_consulta(
    execution_id: str,
    limite: int = Query(1000, ge=1, le=10000),
) -> dict:
    try:
        info = await asyncio.to_thread(estado, execution_id)
    except AthenaNoConfigurado as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e)) from e
    except AthenaError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    respuesta = {"execution_id": execution_id, **info}

    # Los resultados solo existen si la consulta termino bien.
    if info["estado"] == "SUCCEEDED":
        columnas, filas = await asyncio.to_thread(resultados, execution_id, limite)
        respuesta |= {"columnas": columnas, "filas": filas, "total_filas": len(filas)}

    return respuesta
