from typing import Any, Dict, List

from fastapi import Depends, Query
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_config import get_session
from app.models import UpdateCardSettings
from app.services import CardManipulationService

router = APIRouter()


@router.put(
    "/card/update",
    response_model=FullClientCardOut,
    openapi_extra={
        "x-codeSamples": [
            {"lang": "Python", "source": update_card_python, "label": "Python"},
            {"lang": "Java", "source": update_card_java, "label": "Java"},
            {"lang": "PHP", "source": update_card_php, "label": "PHP"},
        ]
    },
)
async def update_card(
    *,
    db: AsyncSession = Depends(get_session),
    data_in: UpdateCardSettings,
    card_id: str = Query(default=None, description='Unique Identifier for card'),
    current_users: Dict[str, Any] = Depends(dependences.get_current_client_user),
    card_manipulation_service: CardManipulationService = Depends(),
) -> Any:
    return await card_manipulation_service.update_card(
        db=db, data_in=data_in, card_id=card_id, current_users=current_users
    )


@router.put(
    "/card/update/multiple",
    response_model=FullClientCardOut,
    openapi_extra={
        "x-codeSamples": [
            {"lang": "Python", "source": update_card_python, "label": "Python"},
            {"lang": "Java", "source": update_card_java, "label": "Java"},
            {"lang": "PHP", "source": update_card_php, "label": "PHP"},
        ]
    },
)
async def update_card_status_multiple(
    *,
    db: AsyncSession = Depends(get_session),
    card_id_list: List[str] = Query(default=None, description='List of unique Identifiers for cards'),
    status: str = Query(default=None, description='New status for cards'),
    current_users: Dict[str, Any] = Depends(dependences.get_current_client_user),
    card_manipulation_service: CardManipulationService = Depends(),
) -> Any:
    await card_manipulation_service.update_card_status_multiple(
        db=db, card_list=card_id_list, status=status, current_users=current_users
    )
