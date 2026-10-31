import json
from c2pa import Reader


def check_image(path):
    """Look for Content Credentials (C2PA) in an image file.

    Returns (status, generator):
      "none"    - no credentials found (this does NOT mean the image is real)
      "valid"   - credentials found and the signature check passed
      "invalid" - credentials found, but the signature check failed
      "found"   - credentials found, validation state unknown
      "error"   - the file could not be read
    """
    try:
        reader = Reader(path)
    except Exception as e:
        if "ManifestNotFound" in f"{type(e).__name__} {e}":
            return "none", ""
        return "error", ""

    try:
        store = json.loads(reader.json())
        manifest = store.get("manifests", {}).get(store.get("active_manifest"), {})
        info = manifest.get("claim_generator_info") or [{}]
        if isinstance(info, dict):
            info = [info]
        generator = info[0].get("name") or manifest.get("claim_generator", "unknown")

        try:
            state = str(reader.get_validation_state())
        except Exception:
            state = "unknown"

        if state in ("Valid", "Trusted"):
            return "valid", generator
        if state == "Invalid":
            return "invalid", generator
        return "found", generator
    except Exception:
        return "error", ""
    finally:
        try:
            reader.close()
        except Exception:
            pass