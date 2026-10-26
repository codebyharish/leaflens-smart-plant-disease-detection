"""Fine-tune ConvNeXt-Tiny on a folder-per-class PlantVillage download."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms


def set_seed(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)


def make_loaders(root: Path, batch_size: int, workers: int):
    train_tf = transforms.Compose([
        transforms.Resize((256, 256)), transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(), transforms.RandomRotation(20),
        transforms.ColorJitter(0.25, 0.25, 0.15, 0.05), transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        transforms.RandomErasing(p=0.15),
    ])
    eval_tf = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
    base = datasets.ImageFolder(root)
    indices = list(range(len(base)))
    train_idx, val_idx = train_test_split(indices, test_size=0.15, random_state=42, stratify=base.targets)
    train_set = Subset(datasets.ImageFolder(root, transform=train_tf), train_idx)
    val_set = Subset(datasets.ImageFolder(root, transform=eval_tf), val_idx)
    return (DataLoader(train_set, batch_size, shuffle=True, num_workers=workers, pin_memory=True),
            DataLoader(val_set, batch_size, shuffle=False, num_workers=workers, pin_memory=True), base.classes)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True, help="Folder with one directory per PlantVillage class")
    parser.add_argument("--epochs", type=int, default=15); parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-4); parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--out", type=Path, default=Path("models")); args = parser.parse_args()
    set_seed(42); args.out.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, val_loader, labels = make_loaders(args.data, args.batch_size, args.workers)
    (args.out / "labels.json").write_text(json.dumps(labels, indent=2), encoding="utf-8")
    weights = models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1
    model = models.convnext_tiny(weights=weights); model.classifier[2] = nn.Linear(model.classifier[2].in_features, len(labels)); model.to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1); optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    best = 0.0
    for epoch in range(args.epochs):
        model.train()
        for x, y in train_loader:
            optimizer.zero_grad(); loss = criterion(model(x.to(device)), y.to(device)); loss.backward(); optimizer.step()
        model.eval(); correct = total = 0
        with torch.inference_mode():
            for x, y in val_loader:
                pred = model(x.to(device)).argmax(1).cpu(); correct += int((pred == y).sum()); total += len(y)
        acc = correct / total; scheduler.step(); print(f"epoch {epoch + 1}/{args.epochs}: validation accuracy={acc:.4f}")
        if acc > best:
            best = acc; torch.save({"model_state": model.state_dict(), "validation_accuracy": acc}, args.out / "best_model.pt")
    print(f"Best validation accuracy: {best:.4f}. Model saved to {args.out / 'best_model.pt'}")


if __name__ == "__main__":
    main()
