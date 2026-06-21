import os
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv(Path(__file__).resolve().parent / ".env")

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent / "database" / "chatbot.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
if DATABASE_URL.startswith("sqlite:///./"):
    relative_path = DATABASE_URL.removeprefix("sqlite:///./")
    DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parent / relative_path}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_database() -> None:
    DEFAULT_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    from sql_models import AudioRecording, Conversation, Message, Participant  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_schema_columns()


def _ensure_schema_columns() -> None:
    inspector = inspect(engine)
    if "conversations" not in inspector.get_table_names():
        return

    conversation_columns = {
        column["name"] for column in inspector.get_columns("conversations")
    }
    if "question_sequence" in conversation_columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE conversations ADD COLUMN question_sequence TEXT NOT NULL DEFAULT '[]'")
        )
