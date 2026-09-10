from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite connection configuration with thread check disabled for multithreaded FastAPI worker
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=False)

# A development machine should still be able to run the demo when its optional
# remote PostgreSQL instance is unreachable (for example, offline judging).
if not settings.DATABASE_URL.startswith("sqlite") and settings.ENVIRONMENT == "development":
    try:
        with engine.connect():
            pass
    except SQLAlchemyError as exc:
        print(f"[VARUNA] Remote database unavailable; using local SQLite: {exc}")
        engine = create_engine("sqlite:///./varuna.db", connect_args={"check_same_thread": False}, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
