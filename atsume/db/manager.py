import logging
import typing

import alluka
import tanjun
import ormar
import databases
import sqlalchemy
from atsume.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.database: typing.Optional[databases.Database] = None
        self.engine: typing.Optional[sqlalchemy.engine.Engine] = None
        self.metadata = sqlalchemy.MetaData()

    def _create_database(self):
        self.database = databases.Database(settings.DATABASE_URL)


database = DatabaseManager()


def hook_database(client: alluka.Injected[tanjun.abc.Client]):
    @client.with_client_callback(tanjun.ClientCallbackNames.STARTING)
    async def on_starting(client: alluka.Injected[tanjun.abc.Client]):
        logger.info("Connecting to database...")
        if not database.engine:
            await database.database.connect()
            database.engine = sqlalchemy.create_engine(settings.DATABASE_URL)

        # Todo: Implement Alembic integration
        database.metadata.create_all(database.engine)

    @client.with_client_callback(tanjun.ClientCallbackNames.CLOSED)
    async def on_closed(client: alluka.Injected[tanjun.abc.Client]):
        if database.database:
            logger.info("Disconnecting from the database...")
            await database.database.disconnect()
            database.database = None
