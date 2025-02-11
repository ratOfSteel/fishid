import time
import cv2
from ultralytics import YOLO

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # Папка, где лежит `model.py`
MODEL_PATH = BASE_DIR / "best.pt"

model = YOLO(str(MODEL_PATH))

def predict_class(path: str):

    start_time = time.time()

    results = model.predict(path, conf=0.4)

    predicted_classes = []

    for result in results:
        probs = result.probs
        if probs is not None:
            predicted_classes.append(probs.top1)

    if not predicted_classes:
        predicted_classes = ['No object']

    result_image = results[0].plot()
    result_image_path = path.replace(".jpg", "_result.jpg")
    cv2.imwrite(result_image_path, result_image)

    proc_time = round(time.time() - start_time, 2)

    return ', '.join(predicted_classes), proc_time, result_image_path