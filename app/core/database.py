# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # <<< NOVO: Importe declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import DeclarativeMeta # Para o type hint de Base

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine: Engine = create_engine(DATABASE_URL, echo=True) # Remova connect_args, pois é para SQLite

# *** NOVO: Crie a Base declarativa aqui ***
# Esta 'Base' será herdada por TODOS os seus modelos SQLAlchemy
Base: DeclarativeMeta = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    from app.models.user import User
    from app.models.game import Game
    from app.models.bet import Bet

    print("Tentando executar Base.metadata.create_all(engine)...") 
    try:
        Base.metadata.create_all(engine) 
        print("Base.metadata.create_all(engine) executado com sucesso.") 
    except Exception as e:
        print(f"ERRO durante Base.metadata.create_all: {e}")

def get_session():
    """Fornece uma sessão de banco de dados para cada requisição da API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
