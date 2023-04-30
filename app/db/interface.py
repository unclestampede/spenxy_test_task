from abc import ABC, abstractmethod


class DBFacadeInterface(ABC):
    @abstractmethod
    async def commit(self) -> None:
        """Commit изменений"""

    @abstractmethod
    async def get_card_by_id(self, card_id: str):
        """Получение карты по id"""

    @abstractmethod
    async def update_card(self):
        """Обновление карты"""

    @abstractmethod
    async def delete_card(self):
        """Удаление карты"""

    @abstractmethod
    async def get_card_balance_by_id(self, card_id: str):
        """Получение баланса карты по id"""

    @abstractmethod
    async def update_card_balance(self):
        """Обновление баланса карты"""

    @abstractmethod
    async def get_card_limits_by_id(self, card_id: str):
        """Получение лимитов карты по id"""

    @abstractmethod
    async def update_card_limits(self):
        """Обновление лимитов карты"""

    @abstractmethod
    async def get_card_settings_by_id(self, card_id: str):
        """Получение параметров карты по id"""

    @abstractmethod
    async def update_card_settings(self):
        """Обновление параметров карты"""
