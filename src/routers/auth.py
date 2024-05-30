from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .. import schemas

from src import models, database
from src.config.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password):
    """
    Hashes a plain text password using a secure hashing algorithm.

    Args:
    password (str): The plain text password to be hashed.

    Returns:
    str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    Verifies that a plain text password matches the hashed password.

    Args:
    plain_password (str): The plain text password to verify.
    hashed_password (str): The hashed password to compare against.

    Returns:
    bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JSON Web Token (JWT) for authentication.

    Args:
    data (dict): The data to encode in the token.
    expires_delta (timedelta, optional): The time duration until the token expires. Defaults to None.

    Returns:
    str: The encoded JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_username(db: Session, username: str):
    """
    Retrieves a user from the database by their username.

    Args:
    db (Session): The database session.
    username (str): The username to search for.

    Returns:
    models.User: The user object if found, None otherwise.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user(db: Session, token: str):
    """
    Retrieves a user from the database by decoding the provided JWT.

    Args:
    db (Session): The database session.
    token (str): The JWT to decode.

    Raises:
    HTTPException: If the token is invalid or the user is not found.

    Returns:
    models.User: The user object if found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    Registers a new user in the database.

    Args:
    user (schemas.UserCreate): The user data for registration.
    db (Session): The database session.

    Raises:
    HTTPException: If the username is already registered.

    Returns:
    models.User: The newly registered user object.
    """
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_current_user(
    db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)
):
    """
    Retrieves the current authenticated user from the database.

    Args:
    db (Session): The database session.
    token (str): The OAuth2 token for authentication.

    Returns:
    models.User: The current authenticated user object.
    """
    return get_user(db, token)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    """
    Authenticates a user and returns an access token.

    Args:
    form_data (OAuth2PasswordRequestForm): The login form data containing username and password.
    db (Session): The database session.

    Raises:
    HTTPException: If the username or password is incorrect.

    Returns:
    dict: A dictionary containing the access token and token type.
    """
    db_user = get_user_by_username(db, form_data.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/users/me", response_model=schemas.UserOut)
# def read_users_me(current_user: models.User = Depends(get_user)):
#     return current_user
