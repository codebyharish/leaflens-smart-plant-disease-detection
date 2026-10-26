# Run LeafLens

## 1. Install Python once

Install **Python 3.10 or newer** from https://www.python.org/downloads/. During setup, select **Add Python to PATH**.

Close and reopen PowerShell after installation.

## 2. Set up this project

Open PowerShell in this folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Download the training dataset

```powershell
git clone https://github.com/spMohanty/plantvillage-dataset data/PlantVillage
```

You should now have a `data\PlantVillage\raw\color` folder containing folders such as `Apple___Apple_scab`.

## 4. Train the model

```powershell
python train.py --data data\PlantVillage\raw\color --epochs 15 --batch-size 32
```

Training can take from minutes (GPU) to many hours (CPU). When complete, it saves the model to `models\best_model.pt`.

## 5. Open the app

```powershell
streamlit run app.py
```

Open the local address printed in PowerShell, usually `http://localhost:8501`.

## Important

Never treat a plant using the app result alone. It is a student project and should be confirmed by a local agriculture expert where the decision matters.
