from sqlalchemy.ext.asyncio import AsyncSession


class CardSettingsDao:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_card(card_id: str):
        pass

    async def update():
        pass
