from pathlib import Path
import secrets
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from face_recognizer import face_recognizer

app = FastAPI()

images_base_path = Path("images")


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
async def add_image(name: str, image: UploadFile = File(...)):
    """
    Adds an image of a person to a folder structure with a randomized filename
    and preserves the original image format.

    Args:
        name (str): Name of the person in the image.
        image (UploadFile): The uploaded image file.

    Returns:
        dict: A dictionary containing a message indicating success or failure
              and the saved filename.
    """
    try:
        # Validate image format
        try:
            image_object = Image.open(image.file)  # Open the image in memory
            image_object.verify()  # Check for valid image format
        except (IOError, SyntaxError):
            raise HTTPException(
                status_code=400, detail="Uploaded file is not a valid image."
            )

        # Create the base "images" folder if it doesn't exist
        images_base_path.mkdir(parents=True, exist_ok=True)

        # Create a subfolder for the person's name
        person_folder = images_base_path / name
        person_folder.mkdir(parents=True, exist_ok=True)

        # Generate a random alphanumeric string (10 characters) for filename
        random_filename = secrets.token_urlsafe(10)

        # Extract and preserve original image extension
        filename = f"{random_filename}.{image.content_type.split('/')[-1]}"
        filepath = person_folder / filename

        # Save the image to the created filepath
        contents = await image.read()
        with open(filepath, "wb") as f:
            f.write(contents)

        return {"message": f"Image for {name} saved successfully! Filename: {filename}"}

    except Exception as e:
        print(f"Error saving image: {e}")
        return {"message": "Error saving image. Please try again."}
