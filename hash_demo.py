import hashlib

def make_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

print(make_hash("hello"))
print(make_hash("hello"))
print(make_hash("Hello"))
print(make_hash("hello world, this is a much longer sentence"))