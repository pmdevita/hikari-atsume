class MigrationIsEmpty(Exception):
    pass


class ServerDefaultRequired(Exception):
    def __init__(self, model_name: str, column_name: str) -> None:
        super().__init__(
            f'Non-null column "{column_name}" being added to already existing model "{model_name}". '
            f"Please specify a server_default for the column or make it nullable."
        )
