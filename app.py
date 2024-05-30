from os import getenv
from dotenv import load_dotenv

from pathlib import Path
from typing import Optional, Annotated, Union
import secrets
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
import uvicorn

from src import models, schemas, database
from src.face_recognizer import face_recognizer
from src.database import get_db
from src.routers.auth import get_current_user, router as auth_router
from src.models import User


app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

images_base_path = Path("images")


@app.post("/recognizer")
async def recognize(image: UploadFile = File(...)):
    """
    Recognizes faces in an uploaded image.

    Args:
        image (UploadFile): The uploaded image file.

    Returns:
        list: A list of dictionaries containing face locations and names.
    """
    results = face_recognizer(image.file)
    return results


@app.post("/add_image")
async def add_image(name: str, image: UploadFile = File(...)):
    """
    Adds an image of a person to a user's private folder structure with a
    randomized filename and preserves the original image format. Requires JWT authentication.

    Args:
        name (str): Name of the person in the image.
        image (UploadFile): The uploaded image file.
        current_user (User): The authenticated user object.

    Returns:
        dict: A dictionary containing a message indicating success or failure
              and the saved filename.
    """

    try:
        # Validate image format
        try:
            image_object = Image.open(image.file)
            image_object.verify()
        except (IOError, SyntaxError):
            raise HTTPException(
                status_code=400, detail="Uploaded file is not a valid image."
            )

        # Get username from the authenticated user object
        # username = current_user.username

        # Create user's folder structure if it doesn't exist
        user_folder = images_base_path / name
        user_folder.mkdir(parents=True, exist_ok=True)

        # Generate a random alphanumeric string (10 characters) for filename
        random_filename = secrets.token_urlsafe(10)

        # Extract and preserve original image extension
        filename = f"{random_filename}.{image.content_type.split('/')[-1]}"
        filepath = user_folder / filename

        image = Image.open(image.file)
        image.save(filepath)

        # Save the image to the created filepath
        # contents = await image.read()
        # with open(filepath, "wb") as f:
        #     f.write(contents)

        return {"message": f"Image for {name} saved successfully! Filename: {filename}"}

    except Exception as e:
        print(f"Error saving image: {e}")
        raise HTTPException(
            status_code=500, detail="Error saving image. Please try again."
        )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
