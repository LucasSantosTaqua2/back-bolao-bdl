# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session, engine, Base # create_db_and_tables não é mais necessária aqui se chamamos Base.metadata.create_all
from app.core.config import settings
from app.crud.user import create_user, get_user_by_username
from app.models.user import User, UserRole # UserRole agora com valores MAIÚSCULOS
from app.schemas.user import UserCreate

app = FastAPI(
    title="Bolão Balde de Lixo API",
    description="API para o sistema de bolão de futebol do Brasileirão.",
    version="1.0.0",
)

# --- Configuração CORS ---
frontend_url_env = os.getenv("FRONTEND_URL")
origins_to_allow = []
cors_print_message_main = ""
cors_print_message_suffix = "(allow_credentials=True)"

if frontend_url_env:
    cleaned_frontend_url = frontend_url_env.rstrip('/')
    origins_to_allow.append(cleaned_frontend_url)
    cors_print_message_main = f"INFO: CORS - FRONTEND_URL definida. Origins permitidas: {origins_to_allow}"
else:
    origins_to_allow.append("http://localhost:4200")
    cors_print_message_main = "AVISO: FRONTEND_URL não definida. CORS permitirá http://localhost:4200 por padrão. Defina FRONTEND_URL para produção."

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
        from app.models.user import User
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
            print(f"INFO: Usuário '{existing_admin_user.username}' (ID: {existing_admin_user.id}, Role: {existing_admin_user.role.value}) já existe. Não criando novamente.")
        else:
            print(f"INFO: Usuário '{admin_username_to_check}' não encontrado. Tentando criar...")
            admin_password = os.getenv("ADMIN_PASSWORD")

            if not admin_password:
                default_unsafe_password = "DefaultChangeThisPassword123!"
                print(f"AVISO CRÍTICO: ADMIN_PASSWORD não definida! Usando senha padrão insegura: '{default_unsafe_password}'")
                admin_password = default_unsafe_password
            
            check_again = get_user_by_username(admin_username_to_check, db_startup)
            if check_again:
                print(f"INFO: Usuário ADMIN foi criado por outro processo ou já existia antes da segunda verificação. Username: {check_again.username}")
            else:
                admin_user_data = UserCreate(username=admin_username_to_check, password=admin_password, role=UserRole.ADMIN)
                try:
                    created_admin = create_user(db=db_startup, user_create=admin_user_data)
                    print(f"INFO: Usuário '{created_admin.username}' (ID: {created_admin.id}, Role: {created_admin.role.value}) CRIADO com sucesso.")
                except Exception as e_create_admin:
                    print(f"ERRO CRÍTICO: Falha ao criar usuário '{admin_username_to_check}': {e_create_admin}")
                    db_startup.rollback()
    except Exception as e_startup_session:
        print(f"ERRO CRÍTICO: Falha na lógica de startup (sessão ou consulta de usuário): {e_startup_session}")
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
print(f"{cors_print_message_main} {cors_print_message_suffix}")
