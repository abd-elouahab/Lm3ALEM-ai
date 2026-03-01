import os
import sys
import logging
import io
import json
from PIL import Image

sys.path.append('d:/Hackathon_Project/backend')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('vision_debug.log', encoding='utf-8')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

from app.ai.vision import analyze_job_photo

def test():
    img = Image.new('RGB', (100, 100), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    result = analyze_job_photo(image_bytes=image_bytes, client_comment="Water is leaking from the pipe")
    
    with open('vision_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    test()
