import aiosqlite


# only for sqlite
class BaseRepository:
    def __init__(self, db_path: str):
        self.__db_path = db_path
        self.__connection: aiosqlite.Connection | None = None

    async def init(self):
        self.connection = await aiosqlite.connect(self.__db_path)
    
    async def close(self):
        if self.__connection:
            self.__connection.close()
            self.__connection = None
