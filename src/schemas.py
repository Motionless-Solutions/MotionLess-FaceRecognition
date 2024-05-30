from pydantic import BaseModel


class UserCreate(BaseModel):
    """
    Pydantic model for creating a new user.

    Attributes:
    username (str): The username for the new user.
    password (str): The password for the new user.
    """

    username: str
    password: str


class UserOut(BaseModel):
    """
    Pydantic model for representing a user in response data.

    Attributes:
    id (int): The unique identifier of the user.
    username (str): The username of the user.

    Config:
        orm_mode (bool): Enables ORM mode to allow compatibility with ORM objects.
    """

    id: int
    username: str

    class Config:
        orm_mode = True
