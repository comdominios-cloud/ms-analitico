"""Health check."""

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["salud"])
settings = get_settings()


@router.get("/health", summary="Health check del servicio")
def health() -> dict:
    """Informa tambien si Athena esta configurado.

    El servicio puede estar sano y aun asi no poder consultar, si falta el
    bucket de resultados. Distinguir las dos cosas evita perder tiempo
    buscando el problema en el lugar equivocado.
    """
    return {
        "status": "ok",
        "service": settings.app_name,
        "athena_configurado": settings.configurado,
        "base_glue": settings.glue_database,
        "region": settings.aws_region,
    }
