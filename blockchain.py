import hashlib
import json
from datetime import datetime, timezone

def make_hash(data):
    text = json.dumps(data, sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.add_block({"note": "Genesis block"})

    def add_block(self, data):
        previous_hash = self.chain[-1]["hash"] if self.chain else "0"
        block = {
            "index": len(self.chain),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "previous_hash": previous_hash,
        }
        block["hash"] = make_hash(block)
        self.chain.append(block)
        return block

    def is_valid(self):
        for i, block in enumerate(self.chain):
            body = {k: v for k, v in block.items() if k != "hash"}
            if block["hash"] != make_hash(body):
                return False, i
            if i > 0 and block["previous_hash"] != self.chain[i - 1]["hash"]:
                return False, i
        return True, None

if __name__ == "__main__":
    bc = Blockchain()
    bc.add_block({"text_id": 1, "score": 12.7})
    bc.add_block({"text_id": 2, "score": 100.0})
    print("Valid before tampering:", bc.is_valid())

    bc.chain[1]["data"]["score"] = 5.0   # secretly change a saved result
    print("Valid after tampering:", bc.is_valid())