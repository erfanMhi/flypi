from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    GROQ_API_TIMEOUT: float = 30.0
    MODEL_NAME: str = "llama-3.2-90b-vision-preview"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 1024
    SEED: int = 42
    GROQ_API_KEY: str = ""
    
    # Network settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # SSL/TLS Settings
    SSL_KEYFILE: str = "certs/key.pem"
    SSL_CERTFILE: str = "certs/cert.pem"
    USE_HTTPS: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 