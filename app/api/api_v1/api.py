# app/api/api_v1/api.py
from fastapi import APIRouter

# Importe os routers diretamente dos arquivos .py
from app.api.api_v1.endpoints.users import router as users_router
from app.api.api_v1.endpoints.games import router as games_router
from app.api.api_v1.endpoints.bets import router as bets_router # <--- NOVO: Importa o router de apostas


api_router = APIRouter()

# Inclua os routers existentes
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(games_router, prefix="/games", tags=["games"])

# <--- NOVO: Inclua o router de apostas
api_router.include_router(bets_router, prefix="/bets", tags=["bets"])