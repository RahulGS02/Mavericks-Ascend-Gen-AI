from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create database engine with Supabase-optimized settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Reduced for Supabase pooler limits
    max_overflow=10,  # Reduced overflow
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_timeout=30,  # Connection timeout
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30 second query timeout
    },
    echo=settings.ENVIRONMENT == "development"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Dependency to get database session
def get_db():
    """
    Database session dependency for FastAPI routes.
    Ensures proper session handling and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
