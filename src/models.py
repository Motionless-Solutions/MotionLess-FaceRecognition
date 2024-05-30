from sqlalchemy import Column, Integer, String
from .database import Base


class User(Base):
    """
    SQLAlchemy ORM model for the 'users' table.

    Attributes:
    id (int): The primary key of the user. This field is auto-incremented.
    username (str): The unique username of the user. This field is indexed for fast lookup.
    hashed_password (str): The hashed password of the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
