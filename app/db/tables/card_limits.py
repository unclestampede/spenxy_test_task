from sqlalchemy import Column, Enum, Float, Integer
from sqlalchemy.orm import relationship

from app.db_config import Base


class CardLimits(Base):
    """Класс лимитов карты"""

    id = Column(Integer, primary_key=True, index=True)
    settings_id = Column(Integer, ForeignKey("cardsettings.id"))
    interval = Column(Enum(LimitType), nullable=False, default=LimitType.all_time)
    amount = Column(Float, nullable=False, default=1000)

    settings = relationship("CardSettings", back_populates="limits")
