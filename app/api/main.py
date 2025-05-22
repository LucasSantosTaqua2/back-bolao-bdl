from fastapi import APIRouter
from app.api.api_v1.api import api_router as api_v1_router # <--- Importe o router da v1

api_router = APIRouter()
api_router.include_router(api_v1_router, prefix="/v1") # Inclui a versão 1 da API