"""Cautious decision support shown after a plant-disease prediction."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CareAdvice:
    overview: str
    symptoms: tuple[str, ...]
    spread: str
    actions: tuple[str, ...]
    prevention: tuple[str, ...]
    medication: tuple[str, ...]
    alert: str


FUNGAL_MEDICATION = (
    "Ask a local agronomist for a fungicide registered for this exact crop and disease. Locally registered options may include copper compounds, chlorothalonil, mancozeb, or a labelled systemic fungicide.",
    "Rotate fungicide FRAC groups; repeatedly using one active ingredient encourages resistance.",
    "Use only the label dose, safety precautions, and pre-harvest interval. Do not mix products based on an app.",
)

DEFAULT = CareAdvice(
    "The image needs field confirmation before a treatment decision.",
    ("Symptoms can overlap with nutrient deficiency, pests, mechanical damage, or heat stress.",),
    "Spread and cause are uncertain from one image.",
    ("Photograph more leaves, including the underside.", "Clean tools and isolate heavily affected material."),
    ("Water at the soil line.", "Improve airflow and remove fallen plant debris."),
    ("Do not choose a pesticide until the diagnosis is confirmed locally.",),
    "Contact local agricultural extension staff for high-value crops or rapidly spreading symptoms.",
)

PROFILES: dict[str, CareAdvice] = {
    "healthy": CareAdvice("No disease symptoms were predicted in this photo.", ("Keep scouting because early infections can be subtle.",), "No active disease was predicted.", ("Inspect plants weekly, including undersides.", "Record new symptoms and weather conditions."), ("Use clean tools and disease-free planting material.", "Maintain balanced nutrition and keep foliage dry overnight."), ("No pesticide is recommended for a healthy prediction.",), "A healthy prediction does not guarantee that the plant is disease-free."),
    "bacterial_spot": CareAdvice("Bacterial spot can create dark lesions and spread quickly in warm, wet conditions.", ("Small dark spots may form yellow halos.", "Symptoms often worsen after rain or overhead irrigation."), "Splashing water, infected seed/transplants, hands, and tools can move bacteria.", ("Remove badly affected leaves with disinfected tools.", "Stop overhead watering and avoid handling wet plants."), ("Use clean seed/transplants and rotate susceptible crops.", "Increase spacing and remove crop residue."), ("After local confirmation, ask about a crop-labelled copper bactericide such as copper hydroxide or copper oxychloride.", "Copper products can damage plants and are not registered everywhere; follow the label."), "Confirm bacterial spot first: fungal leaf spots can look similar."),
    "early_blight": CareAdvice("Early blight commonly affects older tomato or potato leaves.", ("Brown lesions may have concentric target-like rings.", "Lower leaves can yellow and drop first."), "Spores persist in crop residue and spread by wind, rain splash, and tools.", ("Remove heavily infected lower leaves.", "Clear infected debris and reduce leaf wetness."), ("Rotate away from tomato/potato relatives.", "Mulch soil and improve plant spacing."), FUNGAL_MEDICATION, "Obtain a local diagnosis if symptoms are expanding quickly."),
    "late_blight": CareAdvice("Late blight is a fast-moving disease of potato and tomato, especially in cool, wet weather.", ("Irregular water-soaked brown lesions can enlarge quickly.", "White growth may appear on leaf undersides in humid weather."), "Wind and wet weather can disperse spores widely.", ("Inspect nearby plants immediately and isolate suspected plants.", "Follow local disposal guidance; do not compost confirmed infected foliage."), ("Avoid prolonged leaf wetness.", "Remove volunteer potato/tomato plants and monitor local alerts."), ("Contact local agricultural extension staff promptly; they can advise registered late-blight products for your crop.", "Do not rely on a single active ingredient or treat an image prediction as confirmed."), "High priority: late blight can cause major crop loss rapidly. Confirm locally today."),
    "powdery_mildew": CareAdvice("Powdery mildew is a fungal disease favoured by crowded growth and poor airflow.", ("White powdery patches may develop on either leaf surface.", "Leaves can curl, yellow, or distort."), "Spores move on wind, tools, clothing, and nearby infected plants.", ("Remove severely affected leaves and disinfect tools.", "Prune dense growth to improve air movement."), ("Use resistant varieties where available.", "Avoid excess nitrogen and prolonged humidity."), ("For a confirmed case, ask about labelled sulphur, potassium bicarbonate, horticultural oil, biological products, or fungicides for the crop.", "Check crop sensitivity and temperature restrictions on the label."), "Do not apply sulphur and oil products close together unless the label permits it."),
    "rust": CareAdvice("Rust diseases form orange, brown, or reddish powdery pustules.", ("Pustules often appear on leaf undersides.", "Severe infection can cause yellowing and leaf drop."), "Spores spread through air, wet foliage, clothing, and tools.", ("Remove heavily infected leaves early.", "Clean tools and avoid working in wet foliage."), ("Improve airflow and reduce leaf wetness.", "Remove volunteer hosts and crop debris."), FUNGAL_MEDICATION, "Check leaf undersides: nutrient issues can resemble rust from above."),
    "leaf_mold": CareAdvice("Leaf mould commonly develops under humid, poorly ventilated tomato conditions.", ("Yellow patches on upper surfaces may match olive/grey growth underneath.",), "Humidity and contaminated crop debris help the fungus persist.", ("Remove affected lower leaves and reduce humidity.", "Increase greenhouse ventilation."), ("Use resistant varieties and sanitize greenhouse surfaces.", "Avoid overcrowding plants."), FUNGAL_MEDICATION, "Inspect the lower leaf surface before treating."),
    "mosaic_virus": CareAdvice("Mosaic-virus-like symptoms are viral and cannot be cured with fungicides or antibiotics.", ("Mottled light/dark green patterns, distortion, or stunting may occur.",), "Viruses can move through infected planting material, sap, and insect vectors such as aphids or whiteflies.", ("Isolate symptomatic plants and disinfect hands/tools.", "Confirm before removing plants."), ("Use certified clean seed/transplants and resistant varieties.", "Manage insect vectors with integrated pest management."), ("There is no curative medication for plant viruses.", "A local expert may recommend vector-control products only if a vector is confirmed and the product is registered."), "Do not spray fungicide for a virus prediction; it will not cure infection."),
    "yellow_leaf_curl_virus": CareAdvice("Yellow leaf curl virus is often associated with whiteflies and has no curative spray.", ("Young leaves may curl upward, yellow, and become smaller.", "Plants may be stunted and set less fruit."), "Whiteflies and infected plants are primary sources of spread.", ("Isolate suspected plants and inspect for whiteflies.", "Remove confirmed infected plants according to local guidance."), ("Use insect-proof netting, weed control, clean transplants, and resistant varieties.",), ("There is no medicine that cures the virus.", "For whiteflies, use locally registered integrated pest management only after checking the pest and crop label."), "Treating the vector does not cure an infected plant."),
    "spider_mites": CareAdvice("Two-spotted spider mites are pests, not a fungal disease; they favour hot, dry conditions.", ("Fine stippling, bronzing, webbing, and tiny mites may occur under leaves.",), "Mites spread between touching plants and via tools, clothing, or air currents.", ("Inspect leaf undersides using a hand lens.", "Isolate heavily infested plants and gently rinse foliage where suitable."), ("Reduce dust and water stress.", "Encourage beneficial predators; avoid broad-spectrum insecticides."), ("Ask about locally registered insecticidal soap, horticultural oil, biological controls, or a crop-labelled miticide.", "Coverage of leaf undersides matters; follow the label and avoid spraying heat-stressed plants."), "Confirm mites visually: fungal spots need different management."),
    "citrus_greening": CareAdvice("Citrus greening (HLB) is a serious disease associated with psyllid vectors.", ("Blotchy uneven yellowing and misshapen fruit can occur.",), "It spreads through infected budwood and citrus psyllids.", ("Do not move suspected plants or propagation material.", "Contact local citrus extension services promptly."), ("Use certified clean nursery stock and official psyllid-management guidance.",), ("There is no reliable home remedy or curative medication. Follow official local instructions only.",), "High priority: suspected citrus greening should be confirmed by agricultural authorities."),
}


def advice_for(label: str) -> CareAdvice:
    key = label.lower().replace(" ", "_").replace("-", "_")
    for term, advice in PROFILES.items():
        if term in key:
            return advice
    if any(term in key for term in ("blight", "scab", "black_rot", "leaf_spot", "target_spot", "cercospora", "septoria", "anthracnose")):
        return CareAdvice("The prediction is consistent with a fungal leaf disease.", ("Leaf spots, discoloration, or dead tissue may appear; field confirmation is needed.",), "Fungal pathogens commonly spread via wind, wet foliage, splashing water, or crop debris.", ("Remove heavily affected foliage with clean tools.", "Avoid overhead watering and dispose of infected debris responsibly."), ("Improve spacing, airflow, sanitation, and crop rotation where practical.",), FUNGAL_MEDICATION, "Confirm the exact disease and crop label before choosing a product.")
    return DEFAULT


def display_label(raw_label: str) -> tuple[str, str]:
    parts = raw_label.replace("___", "|", 1).split("|", 1)
    crop = parts[0].replace("_", " ").replace("(maize)", "Maize").strip()
    condition = (parts[1] if len(parts) > 1 else raw_label).replace("_", " ").strip()
    return crop.title(), condition.title()
