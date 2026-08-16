from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database (MySQL 8.0.44)
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "solotalk"
    DB_PASSWORD: str = "change-me"
    DB_NAME: str = "solotalk"

    # JWT
    JWT_SECRET: str = "change-me-to-a-long-random-string"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Initial admin account (seeded on first startup)
    INITIAL_ADMIN_USERNAME: str = "admin"
    INITIAL_ADMIN_PASSWORD: str = "change-me"

    # Upload storage (local disk)
    UPLOAD_DIR: str = "/data/solotalk/uploads"

    # Rate limiting (application layer)
    RATE_LIMIT_DOWNLOAD_PER_MINUTE: int = 30

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
