# app/core/config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Carrega DATABASE_URL da variável de ambiente.
    # Se não definida, usa o valor fornecido como fallback (idealmente, sempre defina no ambiente de produção).
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:kqCgYBBTkCfLhVwLhXlmIfCMMsCChCZK@gondola.proxy.rlwy.net:36663/railway"
    )
    
    # SECRET_KEY é crucial para segurança (ex: tokens JWT). DEVE ser definida no ambiente.
    SECRET_KEY: str 
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 horas

    # Configurações para carregar variáveis de ambiente.
    # Pydantic-settings tentará carregar de um arquivo .env se existir,
    # mas priorizará variáveis de ambiente do sistema (como as configuradas no Railway).
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Para verificar se as variáveis estão sendo carregadas como esperado (opcional, para debug):
# print(f"DATABASE_URL carregada: {settings.DATABASE_URL}")
# print(f"SECRET_KEY carregada: {'*' * len(settings.SECRET_KEY) if settings.SECRET_KEY else 'NÃO DEFINIDA'}")
