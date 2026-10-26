# Data layout

Place external data here; no dataset is bundled with this project.

```text
data/
  PlantVillage/
    raw/color/
      Apple___Apple_scab/
      Apple___Black_rot/
      ...
  PlantDoc_test/              # class-per-folder copy reserved for final evaluation
```

Never mix `PlantDoc_test` into model selection or augmentation. For a final field evaluation, make its label names exactly match the `models/labels.json` naming convention or prepare a documented mapping.
