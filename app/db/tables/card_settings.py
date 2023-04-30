from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.db_config import Base


class CardSettings(Base):
    """Класс свойств карты"""

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("card.id"))
    active_from = Column(String, nullable=True, default=None)
    active_to = Column(String, nullable=True, default=None)
    allowed_transaction_count = Column(Enum(TransactionCount), nullable=False, default=TransactionCount.multiple)
    allowed_currencies = Column(String, nullable=True, default=None)

    limits = relationship("CardLimits", back_populates="settings", cascade="all,delete")
    card = relationship("Card", back_populates="settings")
