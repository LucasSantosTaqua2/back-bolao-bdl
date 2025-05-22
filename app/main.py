# app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables, get_session
from app.core.config import settings # Importa as configurações
from app.crud.user import create_user
from app.models.user import User, UserRole
# Removidos imports não utilizados de Game e Bet para este trecho, adicione se necessário
# from app.models.game import Game
# from app.models.bet import Bet

from app.schemas.user import UserCreate

from sqlalchemy import select

app = FastAPI(
    title="Bolão Balde de Lixo API",
    description="API para o sistema de bolão de futebol do Brasileirão.",
    version="1.0.0",
)

# --- Configuração CORS ---
frontend_url = os.getenv("FRONTEND_URL")
allow_credentials_setting = True  # Por padrão, queremos permitir credenciais

if frontend_url:
    origins = [frontend_url]
    # Adicione outras origens específicas se necessário, ex: uma URL de staging
    origins.append("https://bolao-bdl-2025.vercel.app/")
    allow_all_origins_for_print = False
else:
    print("-------------------------------------------------------------------------------------------")
    print("AVISO DE SEGURANÇA: A variável de ambiente FRONTEND_URL não está definida!")
    print("CORS será configurado para permitir TODAS as origens, MAS 'allow_credentials' será FALSE.")
    print("Isso significa que a autenticação e outras funcionalidades que dependem de credenciais")
    print("NÃO FUNCIONARÃO CORRETAMENTE até que FRONTEND_URL seja definida no seu ambiente de produção.")
    print("Configure FRONTEND_URL no Railway com a URL do seu frontend no Vercel.")
    print("-------------------------------------------------------------------------------------------")
    origins = ["*"] # Fallback para permitir todas as origens
    allow_credentials_setting = False # Se origins é ["*"], allow_credentials DEVE ser False.
    allow_all_origins_for_print = True


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials_setting, # Usa a configuração ajustada
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Evento que é executado quando a aplicação inicia. Cria as tabelas do BD."""
    print("Iniciando aplicação e criando tabelas se necessário...")
    create_db_and_tables() # Esta função já tem seus próprios prints
    # print("Verificação de tabelas concluída.") # Removido, pois create_db_and_tables já loga

    with next(get_session()) as session:
        existing_user = session.execute(select(User)).scalars().first()

        if not existing_user:
            print("Nenhum usuário encontrado. Criando usuário administrador padrão...")
            
            admin_password = os.getenv("ADMIN_PASSWORD", "L1u1c1a1s1!@")
            if admin_password == "L1u1c1a1s1!@":
                 print("AVISO DE SEGURANÇA: Usando senha padrão para o usuário admin. Configure ADMIN_PASSWORD em produção!")

            admin_user_data = UserCreate(username="ADMIN", password=admin_password, role=UserRole.ADMIN)
            create_user(admin_user_data, session)
            print(f"Usuário administrador padrão '{admin_user_data.username}' criado com sucesso.")
        else:
            print("Usuário(s) já existente(s). Não criando admin padrão.")


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Bolão Balde de Lixo! (FastAPI + MySQL no Railway)"}


# Assumindo que você tenha um router em app.api.api_v1.api
from app.api.api_v1.api import api_router as main_api_router
app.include_router(main_api_router, prefix="/api/v1")

print(f"API pronta. Conectando ao banco: {settings.DATABASE_URL.split('@')[-1].split('/')[0] if settings.DATABASE_URL else 'DATABASE_URL NÃO DEFINIDA'}")
if allow_all_origins_for_print:
    print(f"CORS configurado para permitir TODAS as origens (allow_credentials={allow_credentials_setting}). É CRUCIAL definir FRONTEND_URL para produção!")
else:
    print(f"CORS configurado para permitir as seguintes origens: {origins} (allow_credentials={allow_credentials_setting})")

