from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dao import CardBalanceDao, CardDao, CardLimitsDao, CardSettingsDao
from app.db.interface import DBFacadeInterface
from app.db_config import get_session


class DBFacade(DBFacadeInterface):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session
        self._card_dao = CardDao(session=session)
        self._card_limits_dao = CardLimitsDao(session=session)
        self._card_balance_dao = CardBalanceDao(session=session)
        self._card_settings_dao = CardSettingsDao(session=session)

    async def commit(self) -> None:
        """Commit изменений"""
        await self._session.commit()

    async def get_card_by_id(self, card_id: str):
        """Получение карты по id"""
        return await self._card_dao.get_by_id(card_id)

    async def update_card(self):
        """Обновление карты"""
        await self._card_dao.update()

    async def delete_card(self):
        """Удаление карты"""
        await self._card_dao.delete()

    async def get_card_balance_by_id(self, card_id: str):
        """Получение баланса карты по id"""
        return await self._card_balance_dao.get_by_id(card_id)

    async def update_card_balance(self):
        """Обновление баланса карты"""
        await self._card_balance_dao.update()

    async def get_card_limits_by_id(self, card_id: str):
        """Получение лимитов карты по id"""
        return await self._card_limits_dao.get_by_id(card_id)

    async def update_card_limits(self):
        """Обновление лимитов карты"""
        await self._card_limits_dao.update()

    async def get_card_settings_by_id(self, card_id: str):
        """Получение параметров карты по id"""
        return await self._card_settings_dao.get_by_card(card_id)

    async def update_card_settings(self):
        """Обновление параметров карты"""
        await self._card_settings_dao.update()
