from fastapi import FastAPI, UploadFile, File
from face_recognizer import face_recognizer

app = FastAPI()


@app.post("/recognizer")
async def recognize(image: UploadFile = File(...)):
    results = face_recognizer(image.file)
    return results
