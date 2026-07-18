from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import logging

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    logging.warning("DATABASE_URL is not set. Using a local SQLite fallback.")
    DATABASE_URL = "sqlite:///./codygrow.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()