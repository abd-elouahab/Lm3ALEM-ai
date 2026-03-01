import sys, base64, json
sys.path.insert(0, '.')
from app.ai.chat import chat_with_ai

# Minimal 1x1 JPEG base64
jpeg_1x1 = (
    "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U"
    "HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgN"
    "DRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
    "MjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAA"
    "AAAAAAAAAAAAAAAAAP/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAAAAAA"
    "AAAA/9oADAMBAAIRAxEAPwCwABmX/9k="
)

print("=== Turn 1 ===")
try:
    r1 = chat_with_ai(jpeg_1x1, [], True)
    print("OK:", r1.get("message", "")[:80])
    img_desc = r1.get("image_description", "")
    print("IMG DESC:", img_desc[:80])
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Turn 2 ===")
history = [
    {"role": "assistant", "content": r1["message"]},
    {"role": "system", "content": f"IMAGE: {img_desc}"},
    {"role": "user", "content": "فوق فالسقف"},
]
try:
    r2 = chat_with_ai(jpeg_1x1, history, False)
    print("OK:", r2.get("message", "")[:80], "is_final:", r2.get("is_final"))
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("All good!")
