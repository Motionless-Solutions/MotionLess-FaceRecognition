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

    face_locations = face_recognition.face_locations(image)

    known_encodings = []
    known_names = []

    for filename in os.listdir("assets"):
        known_image = face_recognition.load_image_file(os.path.join("assets", filename))
        known_encoding = face_recognition.face_encodings(known_image)[0]

        known_encodings.append(known_encoding)
        known_names.append(os.path.splitext(filename)[0])

    face_encodings = face_recognition.face_encodings(image, face_locations)
    results = []

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

        result = {
            "top": face_location[0],
            "right": face_location[1],
            "bottom": face_location[2],
            "left": face_location[3],
            "name": name,
        }

        results.append(result)

    return results
