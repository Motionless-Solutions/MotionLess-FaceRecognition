import os
import face_recognition
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw


def face_recognizer(image_path):

    image = face_recognition.load_image_file(image_path)

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


# if __name__ == "__main__":
#     image_path = "C:\\Users\\ynyas\\Downloads\\profile pic.jpg"
#     results = face_recognizer(image_path)

#     image = Image.open(image_path)
#     draw = ImageDraw.Draw(image)

#     for result in results:
#         top, right, bottom, left = (
#             result["top"],
#             result["right"],
#             result["bottom"],
#             result["left"],
#         )
#         draw.rectangle([left, top, right, bottom], outline="red")
#         draw.text((left, top), result["name"], fill="red")

#     image.show()
