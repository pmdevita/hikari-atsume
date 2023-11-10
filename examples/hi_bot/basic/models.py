from atsume.db import Model
import ormar


class HiCounter(Model):
    # Discord User IDs/Snowflakes need to be stored as big integers
    # Autoincrement should be turned off if you use a Snowflake as a primary key
    user: int = ormar.BigInteger(primary_key=True, autoincrement=False)
    count: int = ormar.Integer(default=0)
