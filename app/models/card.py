from dataclasses import dataclass
from typing import List, Optional

from pydantic import Field

from app.db.tables import CardSettings


@dataclass
class TransactionInfo:
    accountant: str
    receiver: str
    client: str
    initiator: str
    initiator_account: str
    receiver_account: str
    receiver_data: str
    admin_: str
    admin_account: str
    user_wallet: str


class UpdateCardSettings(CardSettings):
    """Класс входных данных для обновления карты"""

    nick_name: Optional[str] = Field(description="A nick name for the card.")
    status: Optional[str] = Field(
        default='ACTIVE', description="Card status, Allowed values are INACTIVE, ACTIVE, CLOSED"
    )
    limits: Optional[List[CardLimits]] = Field(description="Transaction limits based on interval and amount.")
