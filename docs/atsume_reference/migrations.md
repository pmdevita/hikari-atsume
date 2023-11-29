# Migrations

Atsume integrates [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) 
for performing semi-automatic database migrations. A migration is a 
database operation that takes us from a previous definition of the 
models to the current. 

:::warning
Atsume's migrations are still under heavy development! While 
it can handle many simple tasks fine, it may not always catch 
more complicated model modifications. It's a good idea to always 
double-check the generated migration files before running them.
:::

## Limitations

Atsume's automatic generation of migrations largely shares the same list of 
limitations as Alembic. This notably includes:

- Changes to table, column, or constraint name
- Change of a column's `server_default`

To create migrations for these changes, they must be created manually, which is covered later.

Extending Alembic to add support for automatically generating these changes is 
on the roadmap.

## Commands

### Making Migrations

Migrations can be created with the `makemigrations` command.

```shell
python manage.py makemigrations
```

This will make new migrations for any changes in any currently loaded apps.

You can also specify to limit to just a single app.

```shell
python manage.py makemigrations -c my_component
```

### Upgrading and downgrading migrations

You can apply all generated migrations with the `upgrade` command.

```shell
python manage.py upgrade
```

You can also specify a specific app or revision number to upgrade to.

```shell
python manage.py upgrade my_component
```


## Auto-formatting Migrations

Migrations are automatically formatted if you have the `black` package installed. 

```shell
pip install black
```


