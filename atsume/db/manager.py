import logging
import typing

import alluka
import tanjun
import databases
import sqlalchemy
from atsume.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """A singleton to manage the database connection."""
    def __init__(self) -> None:
        self.database: typing.Optional[databases.Database] = None
        self.engine: typing.Optional[sqlalchemy.engine.Engine] = None

    def _create_database(self) -> None:
        self.database = databases.Database(settings.DATABASE_URL)


database = DatabaseManager()


def hook_database(client: alluka.Injected[tanjun.abc.Client]) -> None:
    """
    Tanjun lifecycle hooks to create and destroy the database connection when
    Tanjun is starting or finishing closing.
    """
    @client.with_client_callback(tanjun.ClientCallbackNames.STARTING)
    async def on_starting(client: alluka.Injected[tanjun.abc.Client]) -> None:
        logger.info("Connecting to database...")
        if not database.engine and database.database:
            await database.database.connect()
            database.engine = sqlalchemy.create_engine(settings.DATABASE_URL)

    @client.with_client_callback(tanjun.ClientCallbackNames.CLOSED)
    async def on_closed(client: alluka.Injected[tanjun.abc.Client]) -> None:
        if database.database:
            logger.info("Disconnecting from the database...")
            await database.database.disconnect()
            database.database = None
