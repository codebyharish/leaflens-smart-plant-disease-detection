from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision import models, transforms


@dataclass
class Prediction:
    label: str
    confidence: float
    alternatives: list[tuple[str, float]]


class DiseaseClassifier:
    """Loads the checkpoint produced by train.py and predicts one leaf class."""

    def __init__(self, checkpoint_path: str | Path, labels_path: str | Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.labels = json.loads(Path(labels_path).read_text(encoding="utf-8"))
        self.model = models.convnext_tiny(weights=None)
        self.model.classifier[2] = torch.nn.Linear(self.model.classifier[2].in_features, len(self.labels))
        state = torch.load(checkpoint_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state["model_state"] if "model_state" in state else state)
        self.model.to(self.device).eval()
        self.preprocess = transforms.Compose([
            transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(),
            transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ])

    @torch.inference_mode()
    def predict(self, image: Image.Image, top_k: int = 3, selected_crop: str | None = None) -> Prediction:
        tensor = self.preprocess(image.convert("RGB")).unsqueeze(0).to(self.device)
        probabilities = torch.softmax(self.model(tensor)[0], dim=0).cpu().numpy()
        if selected_crop and selected_crop != "Auto detect":
            allowed = np.array([label.split("___", 1)[0] == selected_crop for label in self.labels])
            if allowed.any():
                probabilities = probabilities * allowed
                probabilities = probabilities / probabilities.sum()
        indices = np.argsort(probabilities)[::-1][:top_k]
        alternatives = [(self.labels[int(i)], float(probabilities[i])) for i in indices]
        return Prediction(alternatives[0][0], alternatives[0][1], alternatives)
