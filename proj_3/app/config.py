from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


_base_config = SettingsConfigDict(
    env_file="/home/mbw2025/fastapi_2/proj_3/.env",
    env_ignore_empty=True,
    extra="ignore",
)

class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    model_config = _base_config

    @property
    def POSTGRES_URL(self):
        user = quote_plus(self.POSTGRES_USER)
        pwd = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

class SecuritySettings(BaseSettings):

    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = _base_config


db_settings = DatabaseSettings()
security_settings = SecuritySettings()