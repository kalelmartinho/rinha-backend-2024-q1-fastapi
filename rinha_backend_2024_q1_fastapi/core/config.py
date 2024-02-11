from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DB_DRIVER: str = "postgresql+asyncpg"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_URL: str = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    DB_POOL: int = 5
    DB_OVERFLOW: int = 10


settings = Config()
