class MigrationIsEmpty(Exception):
    """
    Alembic is attempting to automatically generate a migration that would have no commands in it.
    This exception is being used to interrupt the migration generation to avoid an empty file and
    to properly notify the user there are no changes to be made.
    """
    pass


class ServerDefaultRequired(Exception):
    """
    A non-null column is being added to a model without a default provided. In such a case, since null is
    not allowed, any currently existing rows on the table would have no default value for the column
    and the creation command would fail.
    """
    def __init__(self, model_name: str, column_name: str) -> None:
        super().__init__(
            f'Non-null column "{column_name}" being added to already existing model "{model_name}". '
            f"Please specify a server_default for the column or make it nullable."
        )
