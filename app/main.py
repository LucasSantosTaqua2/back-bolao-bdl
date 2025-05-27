# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

# Importações Corrigidas:
from app.core.database import get_session, engine, Base
from app.core.config import settings
from app.crud.user import create_user, get_user_by_username # get_user_by_username foi importado
from app.models.user import User, UserRole # UserRole agora com valores MAIÚSCULOS
from app.schemas.user import UserCreate

app = FastAPI(
    title="Bolão Balde de Lixo API",
    description="API para o sistema de bolão de futebol do Brasileirão.",
    version="1.0.0",
)

# --- Configuração CORS ATUALIZADA ---
frontend_url_env = os.getenv("FRONTEND_URL")

# Origens padrão para permitir o aplicativo móvel Capacitor
mobile_app_origins = [
    "capacitor://localhost",  # Para Capacitor (iOS e Android)
    "http://localhost"        # Para Capacitor Android (WebView)
    # Considere adicionar "ionic://localhost" se você usar o Ionic DevApp para testes
]

# Começa com as origens do app móvel
origins_to_allow = list(mobile_app_origins) # Cria uma cópia para poder modificar

cors_print_message_main = "" # Será definido abaixo
cors_print_message_suffix = "(allow_credentials=True)"

# Adiciona a FRONTEND_URL (para seu frontend web, se existir)
if frontend_url_env:
    cleaned_frontend_url = frontend_url_env.rstrip('/')
    if cleaned_frontend_url:
        if cleaned_frontend_url not in origins_to_allow: # Evita duplicatas
            origins_to_allow.append(cleaned_frontend_url)
        cors_print_message_main = f"INFO: CORS - FRONTEND_URL ('{cleaned_frontend_url}') e origens de app móvel configuradas."
    else:
        # Se FRONTEND_URL estiver vazia, usa um fallback para desenvolvimento web, se necessário
        default_web_dev_origin = "http://localhost:4200"
        if default_web_dev_origin not in origins_to_allow:
            origins_to_allow.append(default_web_dev_origin)
        cors_print_message_main = f"AVISO: FRONTEND_URL vazia. Configurando CORS para origens de app móvel e {default_web_dev_origin}."
else:
    # Se FRONTEND_URL não estiver definida, permite um fallback para desenvolvimento web
    default_web_dev_origin = "http://localhost:4200"
    if default_web_dev_origin not in origins_to_allow: # Só adiciona se não coberto por http://localhost
            origins_to_allow.append(default_web_dev_origin)
    cors_print_message_main = f"AVISO: FRONTEND_URL não definida. Configurando CORS para origens de app móvel e {default_web_dev_origin} por padrão."
    print("              Defina FRONTEND_URL para o seu ambiente de produção web (ex: Railway), se aplicável.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_to_allow,  # Lista atualizada de origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)
# --- Fim da Configuração CORS ---


@app.on_event("startup")
def on_startup():
    print("INFO: Evento de startup da API iniciado.")
    print("INFO: Tentando criar tabelas do banco de dados (se não existirem)...")
    try:
        # Importações dentro da função para evitar problemas de importação circular se os modelos dependerem do engine/Base
        from app.models.user import User
        from app.models.game import Game
        from app.models.bet import Bet
        Base.metadata.create_all(bind=engine)
        print("INFO: Base.metadata.create_all(engine) executado.")
    except Exception as e_create_tables:
        print(f"ERRO CRÍTICO: Falha ao executar create_all para tabelas: {e_create_tables}")
        return # Retorna para evitar continuar com a lógica de startup se as tabelas falharem

    print("INFO: Verificando/Criando usuário administrador padrão...")
    db_startup: Session = None 
    try:
        db_startup = next(get_session()) 
        admin_username_to_check = "ADMIN" # Usuário admin padrão

        # Verifica se o usuário admin já existe
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
            
            # Segurança extra: verificar novamente antes de criar, caso haja concorrência (raro no startup)
            check_again = get_user_by_username(admin_username_to_check, db_startup) 
            if check_again:
                print(f"INFO: Usuário ADMIN foi criado por outro processo ou já existia antes da segunda verificação. Username: {check_again.username}")
            else:
                admin_user_data = UserCreate(username=admin_username_to_check, password=admin_password, role=UserRole.ADMIN)
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

# Importa e inclui as rotas da v1 da API
from app.api.api_v1.api import api_router as api_v1_router 
app.include_router(api_v1_router, prefix="/api/v1")

# Informações de log no final, após a configuração do app
db_url_display = "NÃO DEFINIDA OU INVÁLIDA"
if settings.DATABASE_URL and '@' in settings.DATABASE_URL:
    db_url_parts = settings.DATABASE_URL.split('@')
    if len(db_url_parts) > 1:
        host_and_db_part = db_url_parts[-1].split('/')
        if host_and_db_part:
            db_url_display = host_and_db_part[0] 

print(f"INFO: API pronta. DATABASE_URL aponta para (host:port): {db_url_display}")
# Mensagem de log do CORS atualizada para mostrar todas as origens permitidas
print(f"{cors_print_message_main} Lista final de origens permitidas: {origins_to_allow} {cors_print_message_suffix}")
