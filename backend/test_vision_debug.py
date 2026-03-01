import os
import sys
import logging
import io
from PIL import Image

sys.path.append('d:/Hackathon_Project/backend')

# Configure logging to print to stdout
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from app.ai.vision import analyze_job_photo

def test():
    # Create a generic test image representing a water leak (blue)
    img = Image.new('RGB', (100, 100), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    # Run the photo analyzer
    print("\n--- Starting Analysis ---")
    result = analyze_job_photo(image_bytes=image_bytes, client_comment="Water is leaking from the pipe")
    print("\n--- Final Result ---")
    print(result)

if __name__ == "__main__":
    test()
