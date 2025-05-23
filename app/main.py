# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

# CORRIGIDO: Importar Base e garantir que engine está correto.
# create_db_and_tables não é mais chamada diretamente aqui se Base.metadata.create_all é usado.
from app.core.database import get_session, engine, Base
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
# Para produção, FRONTEND_URL DEVE ser definida e sem barra no final.
# Ex: [https://seu-site.vercel.app](https://seu-site.vercel.app)
# Para desenvolvimento local, defina no seu .env: FRONTEND_URL=http://localhost:4200

origins_to_allow = []
cors_print_message_main = ""
# allow_credentials_is_true é assumido como True para a configuração abaixo
cors_print_message_suffix = "(allow_credentials=True)"


if frontend_url_env:
    # Remove a barra final da URL, se houver, para consistência
    cleaned_frontend_url = frontend_url_env.rstrip('/')
    if cleaned_frontend_url: # Adiciona apenas se não for uma string vazia após rstrip
        origins_to_allow.append(cleaned_frontend_url)
        cors_print_message_main = f"INFO: CORS - FRONTEND_URL definida. Origins permitidas: {origins_to_allow}"
    else: # Caso FRONTEND_URL seja apenas "/" ou vazia
        origins_to_allow.append("http://localhost:4200") # Fallback seguro
        cors_print_message_main = "AVISO: FRONTEND_URL definida mas resultou em string vazia após limpeza. CORS permitirá http://localhost:4200. Verifique FRONTEND_URL."

else:
    # Permite localhost para desenvolvimento se FRONTEND_URL não estiver definida
    origins_to_allow.append("http://localhost:4200")
    cors_print_message_main = "AVISO: FRONTEND_URL não definida no ambiente. CORS permitirá http://localhost:4200 por padrão."
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
        # Importar todos os modelos garante que eles estão registados com Base.metadata
        # ANTES de chamar create_all.
        from app.models.user import User # Assegure-se que UserRole é importado aqui ou no escopo global se usado
        from app.models.game import Game
        from app.models.bet import Bet
        Base.metadata.create_all(bind=engine) # Usa a Base e engine importados
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
            print(f"INFO: Usuário '{existing_admin_user.username}' (ID: {existing_admin_user.id}, Role: {existing_admin_user.role.value if existing_admin_user.role else 'N/A'}) já existe. Não criando novamente.")
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
                admin_user_data = UserCreate(username=admin_username_to_check, password=admin_password, role=UserRole.ADMIN) # UserRole.ADMIN virá do Enum corrigido
                try:
                    created_admin = create_user(db=db_startup, user_create=admin_user_data) 
                    print(f"INFO: Usuário '{created_admin.username}' (ID: {created_admin.id}, Role: {created_admin.role.value if created_admin.role else 'N/A'}) CRIADO com sucesso.")
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

from app.api.api_v1.api import api_router as api_v1_router 
app.include_router(api_v1_router, prefix="/api/v1")

db_url_display = "NÃO DEFINIDA OU INVÁLIDA"
if settings.DATABASE_URL and '@' in settings.DATABASE_URL:
    db_url_parts = settings.DATABASE_URL.split('@')
    if len(db_url_parts) > 1:
        host_and_db_part = db_url_parts[-1].split('/')
        if host_and_db_part:
            db_url_display = host_and_db_part[0] 

print(f"INFO: API pronta. DATABASE_URL aponta para (host:port): {db_url_display}")
print(f"{cors_print_message_main} {cors_print_message_suffix}")
