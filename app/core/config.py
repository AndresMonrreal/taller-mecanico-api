from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración general de la aplicación cargada desde variables de entorno.
    """
    DB_USER: str         # Usuario de la base de datos Oracle
    DB_PASS: str         # Contraseña de la base de datos Oracle
    DB_HOST: str         # Host de la base de datos
    DB_PORT: str         # Puerto de conexión
    DB_SERVICE: str      # Nombre del servicio de Oracle
    DB_DSN: str          # DSN completo para la conexión
    WALLET_LOCATION: str   # Ruta al wallet de Oracle ATP
    WALLET_PASSWORD: str   # Contraseña del wallet
    SECRET_KEY: str        # Llave secreta para firmar tokens JWT
    PROJECT_NAME: str = "Taller Pro API"  # Nombre del proyecto
    API_V1_STR: str = "/api/v1"           # Prefijo base para los endpoints
    OPENAI_API_KEY: str   # API key para OpenAI / Claude
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=".env"
    )


settings = Settings()