from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', validate_default=False)
    GOOGLE_API_KEY: str = ""
    APP_NAME: str = "sauluh"
    DB_URL: str = ""
    QDRANT_CLUSTER: str =""
    QDRANT_API_KEY: str =""
    SERVER_SIDE_CALL: str = ""
    CLIENT_SIDE_CALL: str = ""

settings = Settings()