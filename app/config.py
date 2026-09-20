"""Configuracion del microservicio analitico.

No tiene base de datos propia: consulta con Athena sobre el catalogo de Glue,
construido a partir de los archivos que ingesta-datos deposita en S3.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Las consultas viven en archivos .sql, no incrustadas en el codigo: asi se
# pueden revisar, versionar y ejecutar tal cual en la consola de Athena.
DIR_CONSULTAS = Path(__file__).resolve().parent.parent / "queries"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ms-analitico"
    app_env: str = "development"
    app_port: int = 8005
    log_level: str = "info"

    aws_region: str = "us-east-1"

    glue_database: str = "condominio_db"
    athena_workgroup: str = "primary"
    athena_output_s3: str = ""
    athena_query_timeout: int = 60

    # Cuanto esperar entre consultas del estado de una ejecucion.
    athena_poll_seconds: float = 1.0

    @property
    def configurado(self) -> bool:
        """Athena exige un bucket donde dejar los resultados."""
        return bool(self.athena_output_s3)


@lru_cache
def get_settings() -> Settings:
    return Settings()
