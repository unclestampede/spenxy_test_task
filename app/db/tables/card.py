from uuid import uuid4

from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.db_config import Base


class Card(Base):
    """Класс карты"""

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True, default=None)
    cardholder_id = Column(Integer, ForeignKey("cardholder.id"), nullable=True, default=None)
    cardholder_type = Column(Enum(CardholderType), nullable=False, default=CardholderType.client)
    bin_id = Column(Integer, ForeignKey("bin.id"), default=1)
    form_factor = Column(Enum(CardFormFactor), nullable=False, default=CardFormFactor.virtual)
    request_uuid = Column(String, unique=True, nullable=False, default=str(uuid4()))
    card_id = Column(String, nullable=True, default=None, index=True)
    nick_name = Column(String, nullable=True, default=None, index=True)
    bank_nick_name = Column(String, nullable=True)
    created_at = Column(String, nullable=True, default=None)
    mask_number = Column(String)
    status = Column(String, nullable=True, default=None)
    brand = Column(String, nullable=True, default=None)
    activate_on_issue = Column(Boolean, default=True)

    user = relationship("User", back_populates="cards", uselist=False)
    cardholder = relationship("CardHolder", back_populates="cards")
    settings = relationship("CardSettings", back_populates="card", uselist=False, cascade="all,delete")
    transactions = relationship("Transaction", back_populates="card")
    balance = relationship("CardBalance", back_populates="card", uselist=False, cascade="all,delete")
    bin = relationship("Bin", back_populates="cards")
    sensitive_data = relationship("CardSensitiveData", back_populates="card", uselist=False, cascade="all,delete")
