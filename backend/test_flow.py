import requests
import json
import base64
import os

BASE_URL = "http://localhost:8000"

# Note: We create a dummy image locally to test vision analysis without breaking it
with open("test.jpg", "wb") as f:
    f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06")

print("1. Testing AI Analysis (/jobs/analyze)")
with open("test.jpg", "rb") as f:
    res = requests.post(f"{BASE_URL}/jobs/analyze", files={"file": f}, data={
        "client_comment": "Water is leaking from the sink pipe very fast",
        "client_name": "John Doe",
        "client_phone": "12345678"
    })

print(f"Analyze Status Code: {res.status_code}")
try:
    analysis = res.json()
    print("Analysis Response:", json.dumps(analysis, indent=2))
except Exception as e:
    print(f"Error parsing analysis response: {res.text}")
    exit(1)

print("\n2. Testing Job Creation (/jobs)")
res2 = requests.post(f"{BASE_URL}/jobs", json={
    "problem_type": analysis.get("problem_type", "plombier"),
    "symptom": "Water is leaking from the sink pipe very fast",
    "client_name": "John Doe",
    "client_phone": "12345678",
    "photo_url": "test.jpg",
    "city": "Agadir",
    "client_latitude": 30.4278,
    "client_longitude": -9.5981,
    "ai_description": analysis.get("description"),
    "diagnosis_notes": analysis.get("diagnosis_notes"),
    "severity": analysis.get("severity"),
    "surface_area_m2": analysis.get("surface_area_m2"),
    "complexity": analysis.get("complexity"),
    "estimated_price_min": analysis.get("price_min"),
    "estimated_price_max": analysis.get("price_max"),
    "estimated_duration_hours": analysis.get("duration_hours")
})

print(f"Create Job Status Code: {res2.status_code}")
try:
    job = res2.json()
    print("Job Response:", json.dumps(job, indent=2))
    job_id = job.get("id")
except Exception as e:
    print(f"Error parsing job response: {res2.text}")
    exit(1)

print(f"\n3. Testing Matching (/match) for Job {job_id}")
res3 = requests.post(f"{BASE_URL}/match", json={"job_id": job_id})
print(f"Match Status Code: {res3.status_code}")
try:
    print("Match Response:", json.dumps(res3.json(), indent=2))
except Exception as e:
    print(f"Error parsing match response: {res3.text}")

# Clean up
os.remove("test.jpg")
