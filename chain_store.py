import hashlib
import json
import sqlite3
from datetime import datetime, timezone

DB = "database.db"

def _conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def make_hash(body):
    text = json.dumps(body, sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()

def text_fingerprint(text):
    return hashlib.sha256(text.encode()).hexdigest()

def init_chain():
    conn = _conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chain_blocks (
            idx INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            hash TEXT NOT NULL
        )
    """)
    conn.commit()
    count = conn.execute("SELECT COUNT(*) AS n FROM chain_blocks").fetchone()["n"]
    conn.close()
    if count == 0:
        add_block({"note": "Genesis block"})

def add_block(data):
    conn = _conn()
    last = conn.execute(
        "SELECT * FROM chain_blocks ORDER BY idx DESC LIMIT 1"
    ).fetchone()
    index = last["idx"] + 1 if last else 0
    previous_hash = last["hash"] if last else "0"
    timestamp = datetime.now(timezone.utc).isoformat()

    body = {
        "index": index,
        "timestamp": timestamp,
        "data": data,
        "previous_hash": previous_hash,
    }
    block_hash = make_hash(body)

    conn.execute(
        "INSERT INTO chain_blocks (idx, timestamp, data, previous_hash, hash) VALUES (?, ?, ?, ?, ?)",
        (index, timestamp, json.dumps(data, sort_keys=True), previous_hash, block_hash),
    )
    conn.commit()
    conn.close()
    return block_hash

def verify_chain():
    conn = _conn()
    blocks = conn.execute("SELECT * FROM chain_blocks ORDER BY idx").fetchall()
    problems = []

    for i, b in enumerate(blocks):
        data = json.loads(b["data"])
        body = {
            "index": b["idx"],
            "timestamp": b["timestamp"],
            "data": data,
            "previous_hash": b["previous_hash"],
        }

        # Check 1: was this block's own content changed?
        if make_hash(body) != b["hash"]:
            problems.append(f"Block {b['idx']}: its contents were changed.")

        # Check 2: is the link to the previous block intact?
        if i > 0 and b["previous_hash"] != blocks[i - 1]["hash"]:
            problems.append(f"Block {b['idx']}: the link to the previous block is broken.")

        # Check 3: does the saved text and score still match this block?
        if "text_id" in data:
            row = conn.execute(
                "SELECT content, ai_score FROM text_checks WHERE id = ?",
                (data["text_id"],),
            ).fetchone()
            if row is not None:  # skipped if the user deleted the text
                if (text_fingerprint(row["content"]) != data["content_hash"]
                        or row["ai_score"] != data["score"]):
                    problems.append(
                        f"Block {b['idx']}: the saved text or score no longer matches its record."
                    )

    conn.close()
    return len(problems) == 0, problems, len(blocks)