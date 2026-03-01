"""Test 2-turn chat with a locally generated valid PNG."""
from app.ai.chat import chat_with_ai
import traceback, base64, struct, zlib

def make_png(w=100, h=100):
    """Generate a valid w x h white PNG."""
    def chunk(name, data):
        crc = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', crc)
    # RGB image, row = filter byte(0x00) + w*3 pixels
    row = b'\x00' + b'\xff\x00\x00' * w  # red row
    raw = row * h
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(raw))
    iend = chunk(b'IEND', b'')
    return b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend

img_bytes = make_png(100, 100)
IMG = base64.b64encode(img_bytes).decode()
print(f"Generated PNG: {len(img_bytes)} bytes, base64: {len(IMG)} chars")
print(f"Magic bytes: {img_bytes[:4]}")

print("\n=== Turn 1: first_message ===")
try:
    r = chat_with_ai(IMG, [], True)
    print("SUCCESS!")
    print("message:", r.get("message", "")[:150])
    print("is_final:", r.get("is_final"))
    assistant_reply = r.get("message", "")
except Exception:
    traceback.print_exc()
    assistant_reply = ""

if assistant_reply:
    print("\n=== Turn 2: user reply ===")
    history = [
        {"role": "assistant", "content": assistant_reply},
        {"role": "user", "content": "التسريب كبير بزاف وبدا من أسبوع"},
    ]
    try:
        r2 = chat_with_ai(IMG, history, False)
        print("SUCCESS!")
        print("message:", r2.get("message", "")[:150])
        print("is_final:", r2.get("is_final"))
    except Exception:
        traceback.print_exc()
