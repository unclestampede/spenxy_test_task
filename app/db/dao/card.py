from sqlalchemy.ext.asyncio import AsyncSession


class CardDao:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(card_id: str):
        pass

    async def update():
        pass

    async def delete():
        pass
