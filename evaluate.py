"""Evaluate a trained model on an untouched folder-per-class test dataset."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from src.inference import DiseaseClassifier


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True, help="Held-out folder-per-class dataset")
    parser.add_argument("--model", type=Path, default=Path("models/best_model.pt"))
    parser.add_argument("--labels", type=Path, default=Path("models/labels.json"))
    parser.add_argument("--out", type=Path, default=Path("outputs/evaluation")); args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    classifier = DiseaseClassifier(args.model, args.labels)
    transform = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize((.485, .456, .406), (.229, .224, .225))])
    dataset = datasets.ImageFolder(args.data, transform=transform)
    loader = DataLoader(dataset, batch_size=32, shuffle=False)
    predicted, actual = [], []
    with torch.inference_mode():
        for x, y in loader:
            logits = classifier.model(x.to(classifier.device)); predicted.extend(logits.argmax(1).cpu().tolist()); actual.extend(y.tolist())
    report = classification_report(actual, predicted, target_names=dataset.classes, output_dict=True, zero_division=0)
    (args.out / "classification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    pd.DataFrame(confusion_matrix(actual, predicted), index=dataset.classes, columns=dataset.classes).to_csv(args.out / "confusion_matrix.csv")
    print(f"Macro F1: {report['macro avg']['f1-score']:.4f}")
    print(f"Saved report to {args.out}")


if __name__ == "__main__":
    main()
