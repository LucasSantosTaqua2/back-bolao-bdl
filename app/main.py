    # app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text # Adicione text para consultas raw se necessário

from app.core.database import create_db_and_tables, get_session
from app.core.config import settings
from app.crud.user import create_user # Certifique-se que esta função faz session.add() e session.commit() ou session.flush()
from app.models.user import User, UserRole
from app.schemas.user import UserCreate

app = FastAPI(
        title="Bolão Balde de Lixo API",
        description="API para o sistema de bolão de futebol do Brasileirão.",
        version="1.0.0",
    )

    # --- Configuração CORS ---
frontend_url = os.getenv("FRONTEND_URL")
allow_credentials_setting = True

if frontend_url:
        origins = [frontend_url]
        allow_all_origins_for_print = False
else:
        print("-------------------------------------------------------------------------------------------")
        print("AVISO DE SEGURANÇA: A variável de ambiente FRONTEND_URL não está definida!")
        print("CORS será configurado para permitir TODAS as origens, MAS 'allow_credentials' será FALSE.")
        print("Isso significa que a autenticação e outras funcionalidades que dependem de credenciais")
        print("NÃO FUNCIONARÃO CORRETAMENTE até que FRONTEND_URL seja definida no seu ambiente de produção.")
        print("Configure FRONTEND_URL no Railway com a URL do seu frontend no Vercel.")
        print("-------------------------------------------------------------------------------------------")
        origins = ["*"]
        allow_credentials_setting = False
        allow_all_origins_for_print = True

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials_setting,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
def on_startup():
        print("Evento de startup: Iniciando aplicação...")
        print("Evento de startup: Tentando criar tabelas se necessário...")
        create_db_and_tables() # Esta função já tem seus próprios prints
        print("Evento de startup: Verificação de tabelas (chamada a create_db_and_tables) concluída.")

        print("Evento de startup: Verificando se o usuário administrador padrão existe...")
        try:
            with next(get_session()) as session:
                # Maneira mais explícita de verificar se há algum utilizador
                result = session.execute(select(User.id).limit(1)).first() # Pega apenas o ID, limita a 1
                
                # Debug: Imprimir o que foi retornado pela consulta
                print(f"Evento de startup: Resultado da consulta por usuário existente: {result}")

                if result is None: # Se result for None, a tabela está vazia ou não há utilizadores
                    print("Evento de startup: Nenhum usuário encontrado na tabela 'user'. Criando usuário administrador padrão...")
                    
                    admin_password = os.getenv("ADMIN_PASSWORD", "L1u1c1a1s1!@")
                    if admin_password == "L1u1c1a1s1!@":
                        print("AVISO DE SEGURANÇA: Usando senha padrão para o usuário admin. Configure ADMIN_PASSWORD em produção!")

                    admin_user_data = UserCreate(username="ADMIN", password=admin_password, role=UserRole.ADMIN)
                    
                    try:
                        print(f"Evento de startup: Tentando criar usuário: {admin_user_data.username}")
                        # Assumindo que create_user adiciona à sessão e faz commit ou flush
                        created_admin = create_user(db=session, user_create=admin_user_data) 
                        # Se create_user não faz commit, precisamos fazer aqui:
                        # session.commit() # Descomente se create_user não fizer commit
                        print(f"Evento de startup: Usuário administrador padrão '{created_admin.username}' supostamente criado com ID: {created_admin.id}.")
                        
                        # Verificação adicional após a tentativa de criação
                        # admin_in_db = session.get(User, created_admin.id) # Requer que o ID seja retornado e a sessão atualizada
                        # if admin_in_db:
                        # print(f"Evento de startup: Confirmação - Usuário '{admin_in_db.username}' encontrado no BD após criação.")
                        # else:
                        # print(f"Evento de startup: ERRO - Usuário '{created_admin.username}' NÃO encontrado no BD após suposta criação.")

                    except Exception as e_create:
                        print(f"Evento de startup: ERRO ao tentar criar usuário administrador: {e_create}")
                        session.rollback() # Reverter em caso de erro na criação
                else:
                    # Se result não for None, significa que a consulta retornou pelo menos uma linha (um ID)
                    print(f"Evento de startup: Usuário(s) já existente(s) na tabela 'user' (ID encontrado: {result[0]}). Não criando admin padrão.")
        except Exception as e_session:
            print(f"Evento de startup: ERRO durante a obtenção da sessão ou consulta de usuário: {e_session}")


@app.get("/")
def read_root():
        return {"message": "Bem-vindo à API do Bolão Balde de Lixo! (FastAPI + MySQL no Railway)"}

from app.api.api_v1.api import api_router as main_api_router
app.include_router(main_api_router, prefix="/api/v1")

print(f"API pronta. Conectando ao banco: {settings.DATABASE_URL.split('@')[-1].split('/')[0] if settings.DATABASE_URL else 'DATABASE_URL NÃO DEFINIDA'}")
if allow_all_origins_for_print:
        print(f"CORS configurado para permitir TODAS as origens (allow_credentials={allow_credentials_setting}). É CRUCIAL definir FRONTEND_URL para produção!")
else:
        print(f"CORS configurado para permitir as seguintes origens: {origins} (allow_credentials={allow_credentials_setting})")

    