from pathlib import Path
import secrets
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from src.face_recognizer import face_recognizer
from src.auth import (
    get_user_by_username,
    get_current_user,
    authenticate_user,
    create_access_token,
    User,
    users_db,
    pwd_context,
)

app = FastAPI()

images_base_path = Path("images")


@app.post("/register")
async def register(username: str, password: str):
    # Check for existing user
    if await get_user_by_username(username):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(password)
    new_user = User(username, hashed_password)
    users_db[username] = new_user  # Update user data in database
    return {"message": "User created successfully!"}


@app.post("/login")
async def login(username: str, password: str):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/recognizer")
async def recognize(image: UploadFile = File(...)):
    """
    Recognizes faces in an uploaded image.

    Args:
        image (UploadFile): The uploaded image file.

    Returns:
        dict: A dictionary containing the name of the person and the coordinates of the box around the face.
    """
    results = face_recognizer(image.file)
    return results


@app.post("/add_image")
async def add_image(
    name: str,
    image: UploadFile = File(...),
    token: str = Depends(get_current_user),
):
    """
    Adds an image of a person to a user's private folder structure with a
    randomized filename and preserves the original image format. requires JWT authentication

    Args:
        name (str): Name of the person in the image.
        image (UploadFile): The uploaded image file.
        token (str): User's access token (obtained through login).

    Returns:
        dict: A dictionary containing a message indicating success or failure
              and the saved filename.
    """

    try:
        # User is already authenticated through the "get_current_user" dependency

        # Validate image format
        try:
            image_object = Image.open(image.file)
            image_object.verify()
        except (IOError, SyntaxError):
            raise HTTPException(
                status_code=400, detail="Uploaded file is not a valid image."
            )

        # Get username from the authenticated user object
        username = token.username

        # Create user's folder structure if it doesn't exist
        user_folder = images_base_path / username / "pics"
        user_folder.mkdir(parents=True, exist_ok=True)

        # Generate a random alphanumeric string (10 characters) for filename
        random_filename = secrets.token_urlsafe(10)

        # Extract and preserve original image extension
        filename = f"{random_filename}.{image.content_type.split('/')[-1]}"
        filepath = user_folder / filename

        # Save the image to the created filepath
        contents = await image.read()
        with open(filepath, "wb") as f:
            f.write(contents)

        return {"message": f"Image for {name} saved successfully! Filename: {filename}"}

    except Exception as e:
        print(f"Error saving image: {e}")
        return {"message": "Error saving image. Please try again."}
