"""Standalone Flask web interface for LeafLens."""
from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path

from flask import Flask, render_template, request, session
from PIL import Image

from src.inference import DiseaseClassifier
from src.knowledge_base import advice_for, display_label
from src.severity import estimate_severity

ROOT = Path(__file__).parent
MODEL, LABELS = ROOT / "models" / "best_model.pt", ROOT / "models" / "labels.json"
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("LEAFLENS_SECRET", "leaflens-local-course-project")

classifier: DiseaseClassifier | None = None


def get_classifier() -> DiseaseClassifier:
    global classifier
    if classifier is None:
        classifier = DiseaseClassifier(MODEL, LABELS)
    return classifier


def image_data(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def list_crops() -> list[tuple[str, str]]:
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    raw = sorted({label.split("___", 1)[0] for label in labels})
    return [(crop, crop.replace("_", " ")) for crop in raw]


@app.route("/", methods=["GET", "POST"])
def index():
    result_data = None
    error = None
    recent = session.get("recent", [])
    crops = list_crops() if LABELS.exists() else []
    selected_crop = request.form.get("plant_type", "Auto detect")
    if request.method == "POST":
        file = request.files.get("leaf_image")
        if not file or not file.filename:
            error = "Choose a JPG, PNG, or WEBP image to start the check."
        elif not (MODEL.exists() and LABELS.exists()):
            error = "Model files are missing. Train the model before using this website."
        else:
            try:
                image = Image.open(file.stream).convert("RGB")
                prediction = get_classifier().predict(image, selected_crop=selected_crop)
                crop, condition = display_label(prediction.label)
                healthy = "healthy" in prediction.label.lower()
                severity, area, overlay = estimate_severity(image, healthy)
                guidance = advice_for(prediction.label)
                result_data = {
                    "crop": crop, "condition": condition, "confidence": round(prediction.confidence * 100, 1),
                    "severity": severity, "area": round(area, 1), "healthy": healthy,
                    "image": image_data(image), "overlay": image_data(Image.fromarray(overlay)),
                    "overview": guidance.overview, "symptoms": guidance.symptoms, "spread": guidance.spread,
                    "actions": guidance.actions, "prevention": guidance.prevention,
                    "medication": guidance.medication, "alert": guidance.alert,
                    "alternatives": [(display_label(label), round(score * 100, 1)) for label, score in prediction.alternatives[1:]],
                }
                entry = {"crop": crop, "condition": condition, "confidence": result_data["confidence"]}
                recent = [entry] + [old for old in recent if old != entry]
                session["recent"] = recent[:4]
            except Exception as exc:  # Keep a malformed upload from crashing the UI.
                error = f"This image could not be analysed: {exc}"
    return render_template("index.html", crops=crops, selected_crop=selected_crop, result=result_data, recent=recent, error=error)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
