import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(
        # Trỏ đường dẫn chính xác đến file .env của bạn
        env_file="/home/mbw2025/fastapi_2/proj_1/.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    @property
    def POSTGRES_URL(self):
        user = quote_plus(self.POSTGRES_USER)
        pwd = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = DatabaseSettings()