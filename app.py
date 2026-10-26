from __future__ import annotations

import importlib
import json
from pathlib import Path
import streamlit as st
from PIL import Image

from src.inference import DiseaseClassifier
import src.knowledge_base as knowledge_base
importlib.reload(knowledge_base)
from src.severity import estimate_severity

ROOT = Path(__file__).parent
MODEL, LABELS = ROOT / "models" / "best_model.pt", ROOT / "models" / "labels.json"

st.set_page_config(page_title="LeafLens | Plant Health", page_icon="Leaf", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
:root{--ink:#10261a;--muted:#456051;--green:#146b3a;--line:#d8e8d8}
.stApp{background:#f4f8f2;color:var(--ink)} [data-testid="stAppViewContainer"] *{color:var(--ink)}
[data-testid="stSidebar"]{background:#123c29} [data-testid="stSidebar"] *{color:#f6fff6!important}
.block-container{max-width:1180px;padding-top:2.3rem;padding-bottom:3rem}
.hero{background:linear-gradient(120deg,#103c29,#176b3c 60%,#278b51);border-radius:24px;padding:2.1rem 2.3rem;margin-bottom:1.5rem;box-shadow:0 12px 32px #1c4d2d33}
.hero h1{color:#fff!important;font-size:2.5rem;margin:0 0 .3rem}.hero p{color:#e1f5e4!important;margin:0;font-size:1.05rem}.eyebrow{color:#bdf08e!important;font-size:.75rem;font-weight:800;letter-spacing:.12em}
.title{color:#143c25!important;font-size:1.22rem;font-weight:800;margin:.55rem 0 .75rem}
[data-testid="stMetric"]{background:#fff;padding:1rem;border:1px solid var(--line);border-radius:16px;box-shadow:0 3px 14px #1f4a2b0d}[data-testid="stMetricLabel"] p{color:var(--muted)!important;font-weight:650}[data-testid="stMetricValue"]{color:var(--green)!important;font-weight:800}
.card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:1.25rem 1.35rem;margin:.3rem 0 1rem;box-shadow:0 3px 14px #1f4a2b0d}.card h3{color:#143c25!important;margin:0 0 .6rem}.card p,.card li{color:#294534!important;line-height:1.6}
.pill{display:inline-block;background:#e4f5d4;color:#245e35!important;padding:.27rem .62rem;border-radius:999px;font-size:.8rem;font-weight:750;margin:0 .35rem .35rem 0}.warning{background:#fff7df;border-left:5px solid #d69e24;border-radius:10px;padding:.9rem 1rem;color:#5d4310!important}.critical{background:#fff0ed;border-left:5px solid #cf4c35;border-radius:10px;padding:.9rem 1rem;color:#632217!important}
.stFileUploader{background:#fff;border:1px dashed #72a47a;border-radius:16px;padding:.6rem 1rem}.stFileUploader label,[data-testid="stFileUploaderDropzone"] *{color:#173b25!important}.stTabs [data-baseweb="tab-list"]{gap:8px}.stTabs [data-baseweb="tab"]{background:#e8f1e7;border-radius:10px;padding:.55rem .85rem;color:#284633!important}.stTabs [aria-selected="true"]{background:#17683b!important;color:#fff!important}.stTabs [aria-selected="true"] *{color:#fff!important}
[data-testid="stMetricValue"] div{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;font-size:1.45rem!important;line-height:1.15!important}
</style>""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="Loading the trained plant-health model...")
def load_model() -> DiseaseClassifier:
    return DiseaseClassifier(MODEL, LABELS)

def card(title: str, items: tuple[str, ...]) -> None:
    content = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(f"<div class='card'><h3>{title}</h3><ul>{content}</ul></div>", unsafe_allow_html=True)

st.markdown("""<section class="hero"><div class="eyebrow">AI-ASSISTED PLANT HEALTH SCREENING</div><h1>LeafLens</h1><p>Upload a leaf photo to identify the likely crop and condition, assess visible damage, and receive clear next steps.</p></section>""", unsafe_allow_html=True)
crop_options = ["Auto detect"]
if LABELS.exists():
    crop_options += sorted({item.split("___", 1)[0] for item in json.loads(LABELS.read_text(encoding="utf-8"))})
with st.sidebar:
    st.markdown("## LeafLens")
    st.caption("Plant-health screening")
    selected_crop = st.selectbox("Plant type", crop_options, format_func=lambda item: item.replace("_", " ") if item != "Auto detect" else "Auto detect")
    st.caption("Auto detect is recommended if you are unsure.")
    st.markdown("### Better result")
    st.markdown("Daylight  •  One leaf  •  Sharp focus")
    st.caption("Screening only — verify any treatment locally.")

if not (MODEL.exists() and LABELS.exists()):
    st.error("Model files are missing. Train the model first, then reload.")
    st.code("python train.py --data data\\PlantVillage\\raw\\color --epochs 15 --batch-size 16", language="powershell")
    st.stop()

st.markdown("<div class='title'>Start a plant-health check</div>", unsafe_allow_html=True)
upload = st.file_uploader("Drop a JPG, PNG, or WEBP leaf image here", type=["jpg", "jpeg", "png", "webp"])
if not upload:
    st.markdown("<div class='card'><h3>What you will receive</h3><span class='pill'>Crop prediction</span><span class='pill'>Disease / healthy status</span><span class='pill'>Confidence</span><span class='pill'>Visible severity screen</span><span class='pill'>Treatment guidance</span><p>For the most useful result, upload a single well-lit close-up of the leaf.</p></div>", unsafe_allow_html=True)
    st.stop()

image = Image.open(upload).convert("RGB")
with st.spinner("Analysing leaf features and symptoms..."):
    result = load_model().predict(image, selected_crop=selected_crop)
    crop, condition = knowledge_base.display_label(result.label)
    healthy = "healthy" in result.label.lower()
    severity, area, overlay = estimate_severity(image, healthy)
    advice = knowledge_base.advice_for(result.label)
    overview_text = getattr(advice, "overview", getattr(advice, "summary", "Field confirmation is recommended."))
    symptoms_text = getattr(advice, "symptoms", ("Inspect several leaves to confirm the visible pattern.",))
    spread_text = getattr(advice, "spread", "The cause and spread need local confirmation.")
    prevention_text = getattr(advice, "prevention", getattr(advice, "remedies", ("Improve airflow and sanitation.",)))
    medication_text = getattr(advice, "medication", getattr(advice, "remedies", ("Confirm the diagnosis before choosing any product.",)))
    alert_text = getattr(advice, "alert", "Contact a local agricultural expert for a high-impact or uncertain case.")

left, right = st.columns((1.02, 1.35), gap="large")
with left: st.image(image, caption="Uploaded plant image", use_container_width=True)
with right:
    st.markdown("<div class='title'>Screening result</div>", unsafe_allow_html=True)
    a,b,c = st.columns(3); a.metric("Likely crop", crop); b.metric("Likely condition", condition); c.metric("Confidence", f"{result.confidence:.1%}")
    if result.confidence < .65: st.markdown("<div class='warning'><b>Low-confidence result.</b> Retake the photo in daylight and confirm locally before treatment.</div>", unsafe_allow_html=True)
    elif healthy: st.success("No disease class was predicted. Keep monitoring—early symptoms can be difficult to see.")
    else: st.info("Use the treatment plan below as a discussion guide, not a pesticide prescription.")
    st.markdown(f"<div class='card'><h3>Visible severity: {severity}</h3><p>Approximate discoloured area: <b>{area:.1f}%</b> of the detected leaf. This image-only screen can confuse shadows, ageing, pests, and mechanical damage with disease.</p></div>", unsafe_allow_html=True)

overview, symptoms, treatment, analysis = st.tabs(["Overview", "Symptoms & spread", "Treatment plan", "Image analysis"])
with overview:
    st.markdown(f"<div class='card'><h3>What this result means</h3><p>{overview_text}</p></div>", unsafe_allow_html=True); card("Do this now", advice.actions); card("Prevention for the next crop cycle", prevention_text)
with symptoms:
    card("Likely signs to inspect", symptoms_text); st.markdown(f"<div class='card'><h3>How it can spread</h3><p>{spread_text}</p></div><div class='critical'><b>When to get local help:</b> {alert_text}</div>", unsafe_allow_html=True)
with treatment:
    st.markdown("<div class='warning'><b>Before using any product:</b> Confirm the disease, make sure it is registered for your crop and location, and follow its label exactly. Do not use a dose, mixture, or frequency suggested by an app.</div>", unsafe_allow_html=True); card("Treatment / medication options to discuss locally", medication_text)
with analysis:
    st.image(overlay, caption="Red overlay: areas possibly discoloured or damaged", use_container_width=True); st.caption("This is an explainable visual aid, not a disease-lesion segmentation model.")
    st.markdown("<div class='title'>Other likely predictions</div>", unsafe_allow_html=True)
    for label, probability in result.alternatives[1:]:
        alt_crop, alt_condition = knowledge_base.display_label(label); st.progress(float(probability), text=f"{alt_crop} — {alt_condition}: {probability:.1%}")
