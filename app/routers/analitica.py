"""Endpoints analiticos.

Cada endpoint ejecuta una de las consultas de `queries/` en Athena y devuelve
los resultados ya convertidos a JSON.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.athena import (
    CATALOGO,
    VISTAS,
    AthenaError,
    AthenaNoConfigurado,
    ejecutar,
    sql_de_consulta,
    sql_de_vista,
)
from app.config import get_settings
from app.schemas import Catalogo, ConsultaDisponible, RespuestaConsulta, SqlDeConsulta

router = APIRouter(prefix="/analitica", tags=["analitica"])
settings = get_settings()


async def _correr(nombre: str, limite: int) -> RespuestaConsulta:
    try:
        resultado = await ejecutar(sql_de_consulta(nombre), limite=limite)
    except AthenaNoConfigurado as e:
        # 503: el servicio esta vivo, lo que falta es configuracion de AWS.
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e)) from e
    except AthenaError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return RespuestaConsulta(
        consulta=nombre,
        execution_id=resultado.execution_id,
        estado=resultado.estado,
        columnas=resultado.columnas,
        filas=resultado.filas,
        total_filas=len(resultado.filas),
        ms_ejecucion=resultado.ms_ejecucion,
        datos_escaneados_bytes=resultado.datos_escaneados,
    )


@router.get("", response_model=Catalogo, summary="Consultas y vistas disponibles")
def catalogo() -> Catalogo:
    """Lista que se puede consultar, sin ejecutar nada en Athena."""
    return Catalogo(
        base_glue=settings.glue_database,
        workgroup=settings.athena_workgroup,
        consultas=[
            ConsultaDisponible(nombre=n, archivo=a, endpoint=f"/analitica/{n}")
            for n, a in CATALOGO.items()
        ],
        vistas=[
            ConsultaDisponible(nombre=n, archivo=a, endpoint=f"/analitica/vistas/{n}")
            for n, a in VISTAS.items()
        ],
    )


@router.get(
    "/morosidad-por-edificio",
    response_model=RespuestaConsulta,
    summary="Deuda y tasa de morosidad por edificio",
)
async def morosidad(limite: int = Query(1000, ge=1, le=10000)) -> RespuestaConsulta:
    """Cruza edificios y unidades (PostgreSQL) con cuotas y pagos (MySQL)."""
    return await _correr("morosidad-por-edificio", limite)


@router.get(
    "/recaudacion-mensual",
    response_model=RespuestaConsulta,
    summary="Emitido contra cobrado, mes a mes",
)
async def recaudacion(limite: int = Query(1000, ge=1, le=10000)) -> RespuestaConsulta:
    return await _correr("recaudacion-mensual", limite)


@router.get(
    "/incidencias-por-categoria",
    response_model=RespuestaConsulta,
    summary="Incidencias por edificio, categoria y prioridad",
)
async def incidencias(limite: int = Query(1000, ge=1, le=10000)) -> RespuestaConsulta:
    """Cruza incidencias (MongoDB) con unidades y edificios (PostgreSQL)."""
    return await _correr("incidencias-por-categoria", limite)


@router.get(
    "/ocupacion-areas-comunes",
    response_model=RespuestaConsulta,
    summary="Uso de las areas comunes por dia de la semana",
)
async def ocupacion(limite: int = Query(1000, ge=1, le=10000)) -> RespuestaConsulta:
    return await _correr("ocupacion-areas-comunes", limite)


@router.get(
    "/prediccion-area-comun",
    response_model=RespuestaConsulta,
    summary="Que area comun sera la mas visitada el proximo mes",
)
async def prediccion(limite: int = Query(1000, ge=1, le=10000)) -> RespuestaConsulta:
    """Tendencia de reservas con funciones de ventana. Lo pidio el ACL."""
    return await _correr("prediccion-area-comun", limite)


@router.get(
    "/sql/{nombre}",
    response_model=SqlDeConsulta,
    summary="Ver el SQL de una consulta sin ejecutarla",
)
def ver_sql(nombre: str) -> SqlDeConsulta:
    """Util para mostrar en la demo que consulta se esta corriendo."""
    if nombre not in CATALOGO:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Consulta desconocida: {nombre}")
    return SqlDeConsulta(nombre=nombre, archivo=CATALOGO[nombre], sql=sql_de_consulta(nombre))


@router.post(
    "/vistas/{nombre}",
    summary="Crear o reemplazar una de las vistas en Athena",
    status_code=status.HTTP_201_CREATED,
)
async def crear_vista(nombre: str) -> dict:
    if nombre not in VISTAS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Vista desconocida: {nombre}")

    try:
        resultado = await ejecutar(sql_de_vista(nombre))
    except AthenaNoConfigurado as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e)) from e
    except AthenaError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return {
        "vista": nombre,
        "estado": resultado.estado,
        "execution_id": resultado.execution_id,
    }
