from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency that provides a new database session for each request.

    This function is used as a dependency in FastAPI routes to provide a
    database session. It ensures that the session is properly closed
    after the request is handled.

    Yields:
    db (Session): The database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
