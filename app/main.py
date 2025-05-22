# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import create_db_and_tables, get_session, engine, Base
from app.core.config import settings
from app.crud.user import create_user, get_user_by_username
from app.models.user import User, UserRole
from app.schemas.user import UserCreate

app = FastAPI(
    title="Bolão Balde de Lixo API",
    description="API para o sistema de bolão de futebol do Brasileirão.",
    version="1.0.0",
)

# --- Configuração CORS ---
frontend_url_env = os.getenv("FRONTEND_URL")
# Para produção, FRONTEND_URL DEVE ser definida e sem barra no final.
# Ex: https://seu-site.vercel.app
# Para desenvolvimento local, defina no seu .env: FRONTEND_URL=http://localhost:4200

origins_to_allow = []

if frontend_url_env:
    # Remove a barra final da URL, se houver, para consistência
    cleaned_frontend_url = frontend_url_env.rstrip('/')
    origins_to_allow.append(cleaned_frontend_url)
    print(f"INFO: CORS - FRONTEND_URL definida como: {cleaned_frontend_url}")
else:
    # Permite localhost para desenvolvimento se FRONTEND_URL não estiver definida
    origins_to_allow.append("http://localhost:4200")
    print("AVISO: FRONTEND_URL não definida no ambiente. CORS permitirá http://localhost:4200 por padrão.")
    print("         Defina FRONTEND_URL para o seu ambiente de produção (ex: Railway).")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_to_allow,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("INFO: Evento de startup da API iniciado.")
    print("INFO: Tentando criar tabelas do banco de dados (se não existirem)...")
    try:
        from app.models.user import User # Importar modelos aqui
        from app.models.game import Game
        from app.models.bet import Bet
        Base.metadata.create_all(bind=engine)
        print("INFO: Base.metadata.create_all(engine) executado.")
    except Exception as e_create_tables:
        print(f"ERRO CRÍTICO: Falha ao executar create_all para tabelas: {e_create_tables}")
        return

    print("INFO: Verificando/Criando usuário administrador padrão...")
    db_startup: Session = None
    try:
        db_startup = next(get_session())
        admin_username_to_check = "ADMIN"

        stmt = select(User).where(User.username == admin_username_to_check)
        existing_admin_user = db_startup.execute(stmt).scalars().first()

        if existing_admin_user:
            print(f"INFO: Usuário '{existing_admin_user.username}' (ID: {existing_admin_user.id}) já existe no banco de dados. Não criando novamente.")
        else:
            print(f"INFO: Usuário '{admin_username_to_check}' não encontrado. Tentando criar...")
            admin_password = os.getenv("ADMIN_PASSWORD")

            if not admin_password:
                default_unsafe_password = "DefaultChangeThisPassword123!"
                print(f"AVISO CRÍTICO: ADMIN_PASSWORD não definida no ambiente! Usando senha padrão insegura: '{default_unsafe_password}'")
                admin_password = default_unsafe_password
            
            # Verificar novamente para o caso de concorrência (pouco provável no startup)
            check_again = get_user_by_username(admin_username_to_check, db_startup)
            if check_again:
                print(f"INFO: Usuário ADMIN foi criado por outro processo ou já existia antes da segunda verificação. Username: {check_again.username}")
            else:
                admin_user_data = UserCreate(username=admin_username_to_check, password=admin_password, role=UserRole.ADMIN)
                try:
                    created_admin = create_user(db=db_startup, user_create=admin_user_data)
                    print(f"INFO: Usuário administrador padrão '{created_admin.username}' CRIADO com sucesso com ID: {created_admin.id}.")
                except Exception as e_create_admin:
                    print(f"ERRO CRÍTICO: Falha ao tentar criar usuário administrador '{admin_username_to_check}': {e_create_admin}")
                    db_startup.rollback()
    except Exception as e_startup_session:
        print(f"ERRO CRÍTICO: Falha na lógica de startup (sessão ou consulta): {e_startup_session}")
    finally:
        if db_startup:
            db_startup.close()
            print("INFO: Sessão de banco de dados do startup fechada.")
    print("INFO: Evento de startup da API concluído.")


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Bolão Balde de Lixo! (FastAPI + MySQL no Railway)"}

from app.api.api_v1.api import api_router as main_api_router
app.include_router(main_api_router, prefix="/api/v1")

db_url_display = "NÃO DEFINIDA OU INVÁLIDA"
if settings.DATABASE_URL and '@' in settings.DATABASE_URL:
    db_url_parts = settings.DATABASE_URL.split('@')
    if len(db_url_parts) > 1:
        host_and_db_part = db_url_parts[-1].split('/')
        if host_and_db_part:
            db_url_display = host_and_db_part[0]

print(f"INFO: API pronta. DATABASE_URL aponta para (host:port): {db_url_display}")
# Para obter a configuração real do middleware CORS após a inicialização:
# Iterar por app.user_middleware para encontrar o CORSMiddleware e inspecionar suas options
# Aqui, apenas imprimimos o que pretendíamos configurar:
print(f"INFO: Configuração CORS pretendida para origins: {origins_to_allow} com allow_credentials=True")