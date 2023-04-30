from sqlalchemy import Column, Float, Integer
from sqlalchemy.orm import relationship

from app.db_config import Base


class CardBalance(Base):
    """Класс балансов карты"""

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("card.id"))
    opening_balance = Column(Float, nullable=False, server_default="0")
    topup_balance = Column(Float, nullable=False, server_default="0")
    limit = Column(Float, nullable=False, server_default="1")
    limit_per_transaction = Column(Float, nullable=False, server_default="1")
    available = Column(Float, nullable=False, default=0)
    used = Column(Float, nullable=False, default=0)
    pending_balance = Column(Float, nullable=False, server_default="0")
    fees_balance = Column(Float, nullable=False, server_default="0")
    incoming_balance = Column(Float, nullable=False, server_default="0")
    withdrawal_balance = Column(Float, nullable=False, server_default="0")

    card = relationship("Card", back_populates="balance")
