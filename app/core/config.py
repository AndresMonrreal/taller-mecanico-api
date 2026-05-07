from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER : str
    DB_PASS : str
    DB_HOST : str
    DB_PORT : str
    DB_SERVICE : str
    
    PROJECT_NAME : str = "Taller Pro API"
    API_V1_STR : str = "/api/v1"
    
    class Config:
        env_file  = ".env"
        
settings = Settings()        
    
    