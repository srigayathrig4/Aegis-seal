import os
import json
from c2pa import Reader

FOLDERS = ["samples/images_real", "samples/images_ai"]

def read_credentials(path):
    try:
        reader = Reader(path)
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:80]}"
    try:
        store = json.loads(reader.json())
        manifest = store.get("manifests", {}).get(store.get("active_manifest"), {})
        info = manifest.get("claim_generator_info") or [{}]
        if isinstance(info, dict):
            info = [info]
        generator = info[0].get("name") or manifest.get("claim_generator", "unknown")
        issuer = manifest.get("signature_info", {}).get("issuer", "unknown")
        try:
            state = reader.get_validation_state()
        except Exception:
            state = "unknown"
        return (generator, issuer, state), None
    finally:
        try:
            reader.close()
        except Exception:
            pass

for folder in FOLDERS:
    print(f"\n=== {folder} ===")
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue
        result, error = read_credentials(os.path.join(folder, name))
        if result is None:
            print(f"{name} -> none found ({error})")
        else:
            generator, issuer, state = result
            print(f"{name} -> FOUND: {generator} | issuer: {issuer} | validation: {state}")