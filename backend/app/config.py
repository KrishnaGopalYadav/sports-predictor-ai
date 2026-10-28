from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sports Predictor AI"
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://sports:sports_local_dev@postgres:5432/sports_predictor"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
