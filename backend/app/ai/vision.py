import json
import re
import base64
import logging
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

def _call_grok(image_bytes: bytes, prompt: str, api_key: str) -> str | None:
    """
    Call Grok vision API and return raw text response.
    Returns None on failure.
    """
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )
        
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        response = client.chat.completions.create(
            model="grok-4",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=600,
            temperature=0.1,
        )
        
        # response is an object — extract text content correctly
        raw_text = response.choices[0].message.content
        logger.info(f"VISION: Grok raw response: {raw_text[:300]}")
        return raw_text
        
    except Exception as e:
        logger.error(f"VISION: Grok call failed: {type(e).__name__}: {e}")
        return None


def _parse_response(raw_text: str) -> dict | None:
    """
    Parse raw string response from any vision API into structured dict.
    Returns None on failure.
    """
    if not raw_text or not raw_text.strip():
        logger.error("VISION: Empty response text")
        return None
    
    text = raw_text.strip()
    
    # Strip markdown code blocks
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    text = text.strip()
    
    # Extract JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    
    try:
        # THIS is the critical step — json.loads converts string to dict
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"VISION: JSON parse failed: {e}")
        logger.error(f"VISION: Text that failed to parse: {raw_text[:400]}")
        return None
    
    # Validate fields
    VALID_PROBLEM_TYPES = {"zlayji", "sebbagh", "gebbas", "plombier", "electricien"}
    VALID_COMPLEXITIES  = {"simple", "moyenne", "complexe"}
    VALID_CONFIDENCES   = {"high", "medium", "low"}
    
    problem_type = str(data.get("problem_type", "gebbas")).lower().strip()
    if problem_type not in VALID_PROBLEM_TYPES:
        logger.warning(f"VISION: Invalid problem_type '{problem_type}'")
        problem_type = "gebbas"
    
    complexity = str(data.get("complexity", "moyenne")).lower().strip()
    if complexity not in VALID_COMPLEXITIES:
        complexity = "moyenne"
    
    confidence = str(data.get("confidence", "low")).lower().strip()
    if confidence not in VALID_CONFIDENCES:
        confidence = "low"
    
    try:
        severity = max(1, min(5, int(data.get("severity", 3))))
    except (ValueError, TypeError):
        severity = 3
    
    try:
        surface_area = max(0.1, float(data.get("surface_area_m2", 1.0)))
    except (ValueError, TypeError):
        surface_area = 1.0
    
    try:
        nb_elements = max(1, int(data.get("nb_elements_affected", 1)))
    except (ValueError, TypeError):
        nb_elements = 1
    
    result = {
        "problem_type":        problem_type,
        "description":         str(data.get("description", "")),
        "diagnosis_notes":     str(data.get("diagnosis_notes", "")),
        "severity":            severity,
        "surface_area_m2":     surface_area,
        "complexity":          complexity,
        "nb_elements_affected":nb_elements,
        "confidence":          confidence,
    }
    
    logger.info(
        f"VISION: Parsed successfully — "
        f"problem_type={problem_type}, severity={severity}, "
        f"complexity={complexity}, confidence={confidence}"
    )
    return result


def analyze_job_photo(
    image_bytes: bytes | None = None,
    client_comment: str = "",
) -> dict:
    """
    Main entry point. Calls Grok vision and returns structured analysis.
    Never crashes — returns defaults on any failure.
    """
    defaults = {
        "problem_type":         "gebbas",
        "description":          "",
        "diagnosis_notes":      "",
        "severity":             3,
        "surface_area_m2":      1.0,
        "complexity":           "moyenne",
        "nb_elements_affected": 1,
        "confidence":           "low",
    }
    
    if not image_bytes:
        logger.error("VISION: No image_bytes provided")
        return defaults
    
    if not settings.XAI_API_KEY:
        logger.error("VISION: XAI_API_KEY is not set")
        return defaults
    
    comment_line = f"\nClient comment: {client_comment}" if client_comment.strip() else ""
    
    prompt = f"""You are an expert Moroccan home repair diagnostic assistant.
Analyze this home repair photo carefully.{comment_line}

Return ONLY a valid JSON object with exactly these fields:
{{
  "problem_type": "<one of: zlayji|sebbagh|gebbas|plombier|electricien>",
  "description": "2-3 sentence description in French of what you see",
  "severity": <integer 1 to 5>,
  "surface_area_m2": <estimated float>,
  "complexity": "<simple|moyenne|complexe>",
  "nb_elements_affected": <integer>,
  "confidence": "<high|medium|low>",
  "diagnosis_notes": "why you chose this problem_type"
}}

Classification rules:
- zlayji     : broken tiles, cracked floor, damaged zellige
- sebbagh    : paint peeling, wall stains, discoloration, mold marks
- gebbas     : plaster cracks, wall fissures, ceiling damage
- plombier   : water leaks, pipe issues, humidity stains from water
- electricien: outlets, wiring, switches, burnt marks, lighting

IMPORTANT: Analyze THIS specific image carefully.
Return different values for different images.
Return ONLY the JSON. No markdown. No backticks.
"""
    
    # Call Grok
    raw_text = _call_grok(image_bytes, prompt, settings.XAI_API_KEY)
    
    if raw_text is None:
        logger.error("VISION: Grok returned None, using defaults")
        return defaults
    
    # Parse the STRING response into a DICT
    parsed = _parse_response(raw_text)
    
    if parsed is None:
        logger.error("VISION: Parse failed, using defaults")
        return defaults
    
    return parsed