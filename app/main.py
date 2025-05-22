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
# Lê a URL do frontend da variável de ambiente.
# Se FRONTEND_URL não estiver definida, permite todas as origens (NÃO RECOMENDADO PARA PRODUÇÃO FINAL).
# Certifique-se de definir FRONTEND_URL nas variáveis de ambiente do seu serviço no Railway.
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins = [
        frontend_url,
        # Adicione outras origens específicas se necessário, ex: uma URL de staging
    ]
    allow_all_origins = False
else:
    print("AVISO DE SEGURANÇA: FRONTEND_URL não definida. Permitindo todas as origens para CORS. Configure FRONTEND_URL em produção!")
    origins = ["*"] # Fallback para permitir todas as origens se a variável não estiver definida
    allow_all_origins = True


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Usa a lista de origens definida acima
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Se allow_origins é ["*"], allow_credentials deve ser False,
    # mas como podemos ter uma URL específica, mantemos True.
    # O FastAPI/Starlette lida com isso corretamente.
)


@app.on_event("startup")
def on_startup():
    """Evento que é executado quando a aplicação inicia. Cria as tabelas do BD."""
    print("Iniciando aplicação e criando tabelas se necessário...")
    create_db_and_tables()
    print("Verificação de tabelas concluída.")

    with next(get_session()) as session:
        existing_user = session.execute(select(User)).scalars().first()

        if not existing_user:
            print("Nenhum usuário encontrado. Criando usuário administrador padrão...")
            
            # Lê a senha do admin da variável de ambiente.
            # Se ADMIN_PASSWORD não estiver definida, usa um valor padrão (NÃO SEGURO PARA PRODUÇÃO).
            # Certifique-se de definir ADMIN_PASSWORD nas variáveis de ambiente do seu serviço no Railway.
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

print(f"API pronta. Conectando ao banco: {settings.DATABASE_URL.split('@')[-1].split('/')[0]}") # Mostra parte da URL do DB sem a senha
if allow_all_origins:
    print("CORS configurado para permitir TODAS as origens.")
else:
    print(f"CORS configurado para permitir as seguintes origens: {origins}")

