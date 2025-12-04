from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings."""
    
    # Database
    database_url: str = (
        "postgresql+psycopg://postgres:101310@localhost:5432/gerentesPublicos"
    )
    
    # API
    api_title: str = "API Seguimiento Gerentes Publicos"
    api_description: str = "API para gestión de compromisos y acciones"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "Info"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    """
    Obtiene la instancia de Settings.
    """
    return Settings()