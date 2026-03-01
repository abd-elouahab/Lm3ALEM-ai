"""Test the fixed 2-turn chat flow with the local broken_pipe.jpg."""
from app.ai.chat import chat_with_ai
import traceback, base64, os

img_path = r"d:\Hackathon_Project\broken_pipe.jpg"
if os.path.exists(img_path):
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    IMG = base64.b64encode(img_bytes).decode()
    print(f"Image loaded: {len(img_bytes)} bytes, base64 len: {len(IMG)}")
else:
    print("NO IMAGE FILE FOUND")
    exit(1)

print("\n=== Turn 1: first_message ===")
try:
    r = chat_with_ai(IMG, [], True)
    print("SUCCESS - message:", r.get("message", "")[:120])
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
        print("SUCCESS - message:", r2.get("message", "")[:120])
        print("is_final:", r2.get("is_final"))
    except Exception:
        traceback.print_exc()
