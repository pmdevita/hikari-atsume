from atsume.db import Model
import ormar


class HiCounter(Model):
    user: int = ormar.BigInteger(
        primary_key=True
    )  # Discord User IDs need to be stored as big integers
    count: int = ormar.Integer(default=0)
