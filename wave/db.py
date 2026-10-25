import click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def init_db() -> None:
    import wave.models  # noqa: F401

    db.create_all()


@click.command("init-db")
def init_db_command() -> None:
    init_db()
    click.echo("Initialized the database.")
