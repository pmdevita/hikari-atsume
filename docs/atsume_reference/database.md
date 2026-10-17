# Database

## Installing the database libraries

You can install your database libraries along with Atsume using one of the following commands

### SQLite

```shell
pip install hikari-atsume[sqlite]
```

### MySQL/MariaDB

```shell
pip install hikari-atsume[mysql]
```

### PostgreSQL

```shell
pip install hikari-atsume[postgresql]
```


## Connecting to the database

You can set the database connection URL in your `local.py` file. Here are some examples depending
on your database of choice. For more information, check the
[SQLAlchemy docs](https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls).

### SQLite

```python
DATABASE_URL = "sqlite://db.sqlite"
```

### MySQL/MariaDB

```python
DATABASE_URL = "mysql+pymysql://username:password@hostname/database"
```

### PostgreSQL

```python
DATABASE_URL = "postgresql+psycopg2://username:password@hostname/database"
```
