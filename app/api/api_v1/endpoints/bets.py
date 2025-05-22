# app/api/v1/endpoints/bets.py

from typing import List, Annotated
from datetime import datetime, timezone # Mantenha datetime e timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import get_current_active_user
from app.core.database import get_session

from app.schemas.bet import BetsSubmissionRequest, BetRead
from app.models.bet import Bet
from app.models.game import Game
from app.models.user import User
from app.models.game import GameStatus

from app.crud.bet import create_bet, get_user_bets_by_round, get_user_bet_for_game # get_user_bet_for_game

router = APIRouter()

@router.post("/", response_model=List[BetRead], status_code=status.HTTP_201_CREATED)
async def create_user_bets(
    bets_request: BetsSubmissionRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session)
):
    """
    Registra múltiplas apostas para o usuário logado em uma transação única.
    """
    if not bets_request.bets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma aposta fornecida."
        )

    created_bets = []
    game_ids = [bet.game_id for bet in bets_request.bets]

    # 1. Verificar se todos os jogos existem e se nenhum deles já começou/terminou
    games_in_db = session.execute(
        select(Game).where(Game.id.in_(game_ids))
    ).scalars().all()

    if len(games_in_db) != len(game_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um ou mais jogos não foram encontrados."
        )

    now_utc = datetime.now(timezone.utc)

    for game in games_in_db:
        # <<< MUDANÇA CRÍTICA AQUI >>>
        # Torna game.game_datetime "aware" (com fuso horário UTC) para comparação
        # Se ele já tiver tzinfo (o que é raro com MySQL DATETIME), usa o existente.
        game_datetime_aware = game.game_datetime.replace(tzinfo=timezone.utc) if game.game_datetime.tzinfo is None else game.game_datetime

        if game_datetime_aware <= now_utc or game.status != GameStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível apostar no jogo '{game.home_team} x {game.away_team}' (ID: {game.id}) pois ele já começou ou terminou."
            )

        existing_bet = get_user_bet_for_game(current_user.id, game.id, session)
        if existing_bet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Você já fez uma aposta para o jogo '{game.home_team} x {game.away_team}' (ID: {game.id})."
            )

    for bet_data in bets_request.bets:
        new_bet_obj = create_bet(bet_data, current_user.id, session)
        created_bets.append(new_bet_obj)

    return created_bets

@router.get("/", response_model=List[BetRead])
async def get_user_bets(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session)
):
    """
    Retorna todas as apostas do usuário logado.
    """
    bets = session.execute(
        select(Bet).where(Bet.user_id == current_user.id)
    ).scalars().all()
    return bets

# --------------------------------------------------
# NOVO ENDPOINT: Obter Apostas de um Usuário por Rodada
# --------------------------------------------------
@router.get("/my-bets-by-round/{round_number}", response_model=List[BetRead])
async def read_user_bets_by_round(
    round_number: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session)
):
    """
    Retorna as apostas do usuário logado para uma rodada específica.
    """
    bets = get_user_bets_by_round(current_user.id, round_number, session)
    return bets