"""Database utilities and connection management."""
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config import settings
from logger import logger

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def init_db():
    """Initialize database connections."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def execute_query(query: str, params: dict = None):
    """Execute a raw SQL query."""
    with get_db() as db:
        try:
            result = db.execute(text(query), params or {})
            db.commit()
            return result.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise


def fetch_query(query: str, params: dict = None):
    """Fetch results from a query."""
    with get_db() as db:
        try:
            result = db.execute(text(query), params or {})
            return result.fetchall()
        except Exception as e:
            logger.error(f"Query fetch failed: {e}")
            raise
