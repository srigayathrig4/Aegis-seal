import os
from detector import ai_probability

def run(folder, expected):
    correct = 0
    files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    for name in files:
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            p = ai_probability(f.read())
        guess = "ai" if p >= 0.5 else "human"
        correct += guess == expected
        print(f"{folder}/{name}: {p * 100:.1f}% AI -> {guess}")
    return correct, len(files)

h_ok, h_n = run("samples/human", "human")
a_ok, a_n = run("samples/ai", "ai")
print(f"\nHuman texts correct: {h_ok}/{h_n}")
print(f"AI texts correct: {a_ok}/{a_n}")