import base64
from app.ai.vision import _call_grok
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)

# Make a dummy dummy image
with open("test.jpg", "wb") as f:
    f.write(b"dummy image data")

with open("test.jpg", "rb") as f:
    img = f.read()

print("Using API KEY:", settings.XAI_API_KEY[:8], "...")
res = _call_grok(img, "What is this?", settings.XAI_API_KEY)
print("Result:", res)
