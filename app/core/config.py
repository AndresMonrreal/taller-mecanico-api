from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_SERVICE: str
    DB_DSN: str
    WALLET_LOCATION: str
    WALLET_PASSWORD: str
    SECRET_KEY: str
    PROJECT_NAME: str = "Taller Pro API"
    API_V1_STR: str = "/api/v1"
    OPENAI_API_KEY: str
    model_config = SettingsConfigDict(
        extra='ignore', 
        env_file=".env"
    )
    
    
settings = Settings()