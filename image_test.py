import os
from PIL import Image
from transformers import pipeline

MODELS = [
    "capcheck/ai-human-generated-image-detection",
    "NYUAD-ComNets/NYUAD_AI-generated_images_detector",
]

FOLDERS = ["samples/images_real", "samples/images_ai"]

for model_name in MODELS:
    print(f"\n########## {model_name} ##########")
    detector = pipeline("image-classification", model=model_name, top_k=None)

    for folder in FOLDERS:
        print(f"\n=== {folder} ===")
        for name in sorted(os.listdir(folder)):
            if not name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            image = Image.open(os.path.join(folder, name)).convert("RGB")
            results = detector(image)
            scores = ", ".join(f"{r['label']}: {r['score'] * 100:.1f}%" for r in results)
            print(f"{name} -> {scores}")