from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Carrega configuração do .env e variáveis de ambiente."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    
    # LLM
    openai_api_key: SecretStr
    llm_model: str = "openai:gpt-4o-mini"
    
    # Banco
    database_url: SecretStr
    
    # Redis
    redis_url: SecretStr
    
    # Logfire
    logfire_token: SecretStr = SecretStr("")
    
    # App
    app_env: str = "development"
    log_level: str = "INFO"
    jwt_secret: SecretStr = Field(min_length=32)


# Instância única usada em todo o projeto
settings = Settings()