from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "ML Research Accelerator"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    EDA_SERVICE_INTERNAL_TOKEN: str = ""
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        return [
            origin.strip() 
            for origin in self.CORS_ORIGINS.split(",") 
            if origin.strip()
        ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()