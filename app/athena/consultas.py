"""Carga de las consultas SQL desde los archivos de `queries/`."""

from functools import lru_cache
from pathlib import Path

from app.config import DIR_CONSULTAS


class ConsultaNoEncontrada(FileNotFoundError):
    pass


# Nombre corto que usa la API -> archivo con el SQL
CATALOGO = {
    "morosidad-por-edificio": "query01_morosidad_por_edificio.sql",
    "recaudacion-mensual": "query02_recaudacion_mensual.sql",
    "incidencias-por-categoria": "query03_incidencias_por_categoria.sql",
    "ocupacion-areas-comunes": "query04_ocupacion_areas_comunes.sql",
    "prediccion-area-comun": "query05_prediccion_area_comun.sql",
}

VISTAS = {
    "vw_estado_cuenta_unidad": "view01_vw_estado_cuenta_unidad.sql",
    "vw_actividad_residente": "view02_vw_actividad_residente.sql",
}


def _leer(archivo: str) -> str:
    ruta: Path = DIR_CONSULTAS / archivo

    if not ruta.is_file():
        raise ConsultaNoEncontrada(f"No existe el archivo de consulta: {archivo}")

    # Athena rechaza el punto y coma final.
    return ruta.read_text(encoding="utf-8").strip().rstrip(";")


@lru_cache
def sql_de_consulta(nombre: str) -> str:
    if nombre not in CATALOGO:
        raise ConsultaNoEncontrada(f"Consulta desconocida: {nombre}")
    return _leer(CATALOGO[nombre])


@lru_cache
def sql_de_vista(nombre: str) -> str:
    if nombre not in VISTAS:
        raise ConsultaNoEncontrada(f"Vista desconocida: {nombre}")
    return _leer(VISTAS[nombre])
