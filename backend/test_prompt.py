import os
import sys
import io
import json
import re

sys.path.append('d:/Hackathon_Project/backend')
from app.config import settings
from google.genai import Client, types as genai_types

def test_gemini():
    client = Client(api_key=settings.GOOGLE_GEMINI_API_KEY)
    
    prompt = """
You are an expert Moroccan home repair diagnostic assistant.
Analyze this home repair photo carefully.

Return ONLY a valid JSON object with exactly these fields:
{
  "problem_type": "<one of: zlayji|sebbagh|gebbas|plombier|electricien>",
  "description": "2-3 sentence description in French of exactly what you see and what needs to be repaired",
  "severity": <integer 1 to 5>,
  "surface_area_m2": <estimated float>,
  "complexity": "<simple|moyenne|complexe>",
  "nb_elements_affected": <integer>,
  "confidence": "<high|medium|low>",
  "diagnosis_notes": "brief explanation of why you chose this problem_type"
}

Problem type classification rules:
- zlayji     : broken/cracked tiles, floor damage, zellige issues
- sebbagh    : paint peeling, stains, wall discoloration, surface coating problems
- gebbas     : plaster cracks, ceiling damage, wall fissures, plaster falling off
- plombier   : water leaks, pipe issues, humidity stains from water, drainage problems, bathroom/kitchen water
- electricien: electrical outlets, wiring, switches, circuit breakers, lighting fixtures

Return ONLY the JSON. No markdown. No backticks. No extra text.
"""
    
    from PIL import Image
    # Create an image that looks like a water leak (blue)
    img = Image.new('RGB', (100, 100), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    # Image first, then prompt
    contents = [
        genai_types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        genai_types.Part.from_text(text=prompt)
    ]
    
    response = client.models.generate_content(model="gemini-1.5-flash", contents=contents)
    text = response.text
    print("--- RAW RESPONSE ---")
    print(text)
    print("--------------------")
    
    # Test JSON parsing as currently implemented
    try:
        t = re.sub(r"^```\w*\n?", "", text)
        t = re.sub(r"\n?```\s*$", "", t)
        t = t.strip()
        data = json.loads(t)
        print("Parsing successful!", data["problem_type"])
    except Exception as e:
        print("Parsing failed with current logic:", e)
        
    # Better logic
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            print("Parsing successful with regex search!", data["problem_type"])
    except Exception as e:
        print("Parsing failed with regex logic:", e)

if __name__ == "__main__":
    test_gemini()
