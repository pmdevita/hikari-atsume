from nox_poetry import session

@session
def lint(session):
    session.install("black")
    session.run("black", "atsume")


@session
def mypy(session):
    session.install("mypy", "sqlalchemy-stubs", ".")
    session.run("mypy", "--strict", "-p", "atsume")
