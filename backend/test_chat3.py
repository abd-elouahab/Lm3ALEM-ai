"""Test the fixed 2-turn chat flow with a real image."""
from app.ai.chat import chat_with_ai
import traceback, base64, urllib.request

# Download a real test image
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        img_bytes = resp.read()
    IMG = base64.b64encode(img_bytes).decode()
    print(f"Image loaded: {len(img_bytes)} bytes")
except Exception as e:
    print(f"Cannot download image: {e}")
    # Fallback - create a minimal proper JPEG (100x100 gray)
    import struct, zlib
    # 10x10 white PNG
    def make_png(w, h):
        def chunk(name, data):
            c = zlib.crc32(name + data) & 0xffffffff
            return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)
        raw = b'\x00' + b'\xff' * (w * 3) + b'\n'
        raw = raw * h
        ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
        idat = chunk(b'IDAT', zlib.compress(raw))
        iend = chunk(b'IEND', b'')
        return b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend
    img_bytes = make_png(10, 10)
    IMG = base64.b64encode(img_bytes).decode()
    print(f"Created fallback image: {len(img_bytes)} bytes")

print("\n=== Turn 1: first_message ===")
try:
    r = chat_with_ai(IMG, [], True)
    print("SUCCESS - message:", r.get("message", "")[:120])
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
        print("SUCCESS - message:", r2.get("message", "")[:120])
        print("is_final:", r2.get("is_final"))
    except Exception:
        traceback.print_exc()
