import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Ensure SQLite directory exists
if "sqlite" in settings.DATABASE_URL:
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

# Standard SQLite URL for universal zero-dependency execution
sync_db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "sqlite:///")
engine = create_engine(sync_db_url, connect_args={"check_same_thread": False} if "sqlite" in sync_db_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class AsyncSessionWrapper:
    """Async wrapper over SQLAlchemy session for seamless FastAPI async endpoint compatibility."""
    def __init__(self, session):
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    def add(self, instance):
        self.session.add(instance)

    async def commit(self):
        self.session.commit()

    async def refresh(self, instance):
        self.session.refresh(instance)

    async def close(self):
        self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def AsyncSessionLocal():
    return AsyncSessionWrapper(SessionLocal())


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    Base.metadata.create_all(bind=engine)
