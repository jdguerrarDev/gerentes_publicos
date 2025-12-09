from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://postgres:password@localhost:5432/gerentesPublicos"
    )
    
    class Config:
        env_file = ".env"

settings = Settings()