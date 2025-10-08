from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
import logging


logger = logging.getLogger("echolens.db")


load_dotenv()


# grab db url from env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in environment variables. "
        "Please set it in your .env file."
    )


# connection pool config for docker
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))


# sqlalchemy engine with pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,           # keep this many connections open
    max_overflow=MAX_OVERFLOW,      # extra connections if needed
    pool_timeout=POOL_TIMEOUT,      # wait time for connection
    pool_recycle=POOL_RECYCLE,      # refresh connections every hour
    pool_pre_ping=True,             # test connection before use
    
    echo=False,                     # turn on for sql logging
    future=True,                    # use sqlalchemy 2.0 style
)


# session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# base for models
Base = declarative_base()


# log pool info on startup
logger.info(
    f"Database engine created with pool_size={POOL_SIZE}, "
    f"max_overflow={MAX_OVERFLOW}, pool_recycle={POOL_RECYCLE}s"
)


# fastapi db dependency
def get_db():
    """
    handles db session lifecycle
    rolls back on errors
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
    finally:
        db.close()


# check if db is reachable
def check_db_connection():
    """
    returns true if db connection works
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
