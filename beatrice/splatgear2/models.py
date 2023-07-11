from atsume import db
import ormar


class Test(db.Model):
    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    name: str = ormar.String(max_length=100)

