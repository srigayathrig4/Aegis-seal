import sys
import struct
from collections import Counter
from PIL import Image

for path in sys.argv[1:]:
    with open(path, "rb") as f:
        data = f.read()

    pos, chunks = 8, []
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        name = data[pos + 4:pos + 8].decode("latin1")
        chunks.append((name, length))
        pos += 12 + length

    width, height = Image.open(path).size
    print(f"\n{path}")
    print(f"  file size: {len(data) / 1024:.0f} KB, dimensions: {width}x{height}")
    counts = Counter(name for name, _ in chunks)
    print("  blocks:", dict(counts))
    for name, length in chunks:
        if name not in ("IDAT", "IHDR", "IEND"):
            print(f"  extra block {name}: {length} bytes")