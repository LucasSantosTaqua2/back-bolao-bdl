# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

# CORRIGIDO: Importar Base e garantir que engine está correto

from app.core.database import get_session, engine, Base# create\_db\_and\_tables não é mais necessária aqui se chamamos Base.metadata.create\_all
from app.core.config import settings
from app.crud.user import create_user, get_user_by_username
from app.models.user import User, UserRole # Modelos SQLAlchemy, UserRole agora terá valores MAIÚSCULOS
from app.schemas.user import UserCreate

app = FastAPI(
title="Bolão Balde de Lixo API",
description="API para o sistema de bolão de futebol do Brasileirão.",
version="1.0.0",
)

# \--- Configuração CORS ---

frontend\_url\_env = os.getenv("FRONTEND\_URL")
origins\_to\_allow = []
cors\_print\_message\_suffix = "(allow\_credentials=True)" \# Definido com base na configuração abaixo

if frontend\_url\_env:
cleaned\_frontend\_url = frontend\_url\_env.rstrip('/')
origins\_to\_allow.append(cleaned\_frontend\_url)
cors\_print\_message\_main = f"INFO: CORS - FRONTEND\_URL definida. Origins permitidas: {origins\_to\_allow}"
else:
origins\_to\_allow.append("http://localhost:4200")
cors\_print\_message\_main = "AVISO: FRONTEND\_URL não definida. CORS permitirá http://localhost:4200 por padrão. Defina FRONTEND\_URL para produção."

app.add\_middleware(
CORSMiddleware,
allow\_origins=origins\_to\_allow,
allow\_credentials=True, \# Mantido como True, pois é necessário para tokens
allow\_methods=["*"],
allow\_headers=["*"],
)

@app.on\_event("startup")
def on\_startup():
print("INFO: Evento de startup da API iniciado.")
print("INFO: Tentando criar tabelas do banco de dados (se não existirem)...")
try:
\# Importar todos os modelos garante que eles estão registados com Base.metadata
from app.models.user import User
from app.models.game import Game
from app.models.bet import Bet
Base.metadata.create\_all(bind=engine) \# Usa a Base e engine importados
print("INFO: Base.metadata.create\_all(engine) executado.")
except Exception as e\_create\_tables:
print(f"ERRO CRÍTICO: Falha ao executar create\_all para tabelas: {e\_create\_tables}")
return
