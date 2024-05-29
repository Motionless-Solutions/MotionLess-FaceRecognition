from io import BytesIO
import os
import face_recognition
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw


def face_recognizer(image_data):
    """
    Performs face recognition on an image provided as bytes.

    Args:
        image_data (bytes): The image data in a byte format.

    Returns:
        list: A list of dictionaries containing face locations and names
              (or "Unknown" if not recognized).
    """

    image_bytes = image_data.read()
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv.imdecode(image_array, cv.IMREAD_COLOR)

    if image is None:
        print("Error: Image could not be decoded.")
        return []

    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    if not face_encodings:
        print("No faces found in the image.")
        return []

    known_encodings = []
    known_names = []

    base_path = "images"
    for user_dir in os.listdir(base_path):
        user_images_folder = os.path.join(base_path, user_dir, "pics")
        if not os.path.isdir(user_images_folder):
            continue

        for filename in os.listdir(user_images_folder):
            file_path = os.path.join(user_images_folder, filename)
            try:
                known_image = face_recognition.load_image_file(file_path)
                known_encodings.extend(face_recognition.face_encodings(known_image))
                known_names.extend(
                    [user_dir] * len(face_recognition.face_encodings(known_image))
                )
            except Exception as e:
                print(f"Error processing image file '{file_path}': {e}")
                continue

    results = []

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

        face_location = {
            "top": face_location[0],
            "right": face_location[1],
            "bottom": face_location[2],
            "left": face_location[3],
        }

        results.append(
            {
                "face_location": face_location,
                "name": name,
            }
        )

    return results
