import sys
import mimetypes
import c2pa
from c2pa import Reader

path = sys.argv[1]
print("c2pa version:", getattr(c2pa, "__version__", "unknown"))
print("Reader methods:", [m for m in dir(Reader) if not m.startswith("_")])

mime = mimetypes.guess_type(path)[0] or "image/png"

def try_open():
    attempts = []
    if hasattr(Reader, "from_file"):
        attempts.append(("Reader.from_file(path)", lambda: Reader.from_file(path)))
    attempts.append(("Reader(path)", lambda: Reader(path)))
    attempts.append(("Reader(mime, stream)", lambda: Reader(mime, open(path, "rb"))))

    for label, attempt in attempts:
        try:
            reader = attempt()
            print("Opened with:", label)
            return reader
        except Exception as e:
            print(f"{label} failed: {type(e).__name__}: {e}")
    return None

reader = try_open()
if reader is not None:
    try:
        print(reader.json()[:600])
    except Exception as e:
        print("json() failed:", type(e).__name__, e)