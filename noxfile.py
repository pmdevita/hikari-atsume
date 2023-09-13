from nox_poetry import session
import platform


@session
def lint(session):
    session.install("black")
    session.run("black", "atsume")


@session
def mypy(session):
    if platform.system() != "Windows":
        session.install("uvloop", "black")
    session.install("mypy", "sqlalchemy-stubs", ".")
    session.run("mypy", "--strict", "-p", "atsume")
