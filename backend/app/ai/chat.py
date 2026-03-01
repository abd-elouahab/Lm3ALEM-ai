from openai import OpenAI
from app.config import settings
import json, re, base64 as _b64

SYSTEM_PROMPT_TEMPLATE = """You are a friendly Moroccan home repair diagnostic assistant.
You speak ONLY in Moroccan Darija (Arabic dialect).

{image_context}

Your job:
1. Ask 2-4 short questions in Darija based on what you saw in the photo
2. Questions must be short, simple, conversational
3. After 2-4 exchanges, give the final diagnosis

When you have enough information, respond with EXACTLY this format and NOTHING else before or after:

FINAL_ANALYSIS:
{{
  "message": "فهمت المشكلة ديالك، هاهي النتيجة:",
  "problem_type": "<zlayji|sebbagh|gebbas|plombier|electricien>",
  "description": "وصف قصير بالعربية للمشكلة",
  "severity": <1-5>,
  "surface_area_m2": <float>,
  "complexity": "<simple|moyenne|complexe>",
  "nb_elements_affected": <integer>,
  "confidence": "<high|medium|low>",
  "diagnosis_notes": "سبب هاد التصنيف بالعربية"
}}

Rules:
- ALWAYS base problem_type on the actual photo (electricity=electricien, water leak=plombier, paint damage=sebbagh, plaster/cracks=gebbas, tiles=zlayji)
- Ask only about: duration, exact location in house, severity change
- NEVER ask more than 4 questions total
- NEVER switch to French or Modern Standard Arabic
- Keep each message under 2 sentences
- Output ONLY the FINAL_ANALYSIS block when done, no extra text
"""

FIRST_TURN_SYSTEM = """You are a Moroccan home repair assistant. You speak ONLY in Moroccan Darija.
Look at the uploaded photo carefully and identify the problem type.
Ask ONE short question in Darija about the problem (e.g. location, duration, severity).
Keep it under 2 sentences. Do NOT give a diagnosis yet, just ask a question.
"""


def _normalize_problem_type(value: str) -> str:
    normalized = (value or "").strip().lower()
    aliases = {
        "zellige": "zlayji",
        "zellij": "zlayji",
        "carrelage": "zlayji",
        "tile": "zlayji",
        "tiles": "zlayji",
        "painting": "sebbagh",
        "paint": "sebbagh",
        "plaster": "gebbas",
        "platre": "gebbas",
        "plumbing": "plombier",
        "electricity": "electricien",
        "electric": "electricien",
    }
    return aliases.get(normalized, normalized or "gebbas")


def _detect_mime(b64: str) -> str:
    try:
        hdr = _b64.b64decode(b64[:16] + "==")[:4]
        if hdr[:3] == b'\xff\xd8\xff':
            return "image/jpeg"
        if hdr[:4] == b'\x89PNG':
            return "image/png"
        if hdr[:6] in (b'GIF87a', b'GIF89a'):
            return "image/gif"
    except Exception:
        pass
    return "image/jpeg"


def _get_image_description(client: OpenAI, image_base64: str, mime: str) -> str:
    """Get a concise description of the image for use in subsequent turns."""
    try:
        resp = client.chat.completions.create(
            model="grok-2-vision-1212",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Describe this home repair problem in 1-2 sentences. Include: type of problem (electrical/plumbing/paint/plaster/tiles), location visible, severity. Be specific."
                        }
                    ]
                }
            ],
            max_tokens=100,
            temperature=0.1,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[CHAT] image description failed: {e}")
        return "The client uploaded a photo showing a home repair problem."


def _parse_final_analysis(raw: str) -> dict | None:
    """Extract FINAL_ANALYSIS JSON using multiple strategies."""
    # Strategy 1: Official FINAL_ANALYSIS: prefix
    if "FINAL_ANALYSIS:" in raw:
        after = raw.split("FINAL_ANALYSIS:", 1)[1].strip()
        m = re.search(r'\{.*\}', after, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass

    # Strategy 2: JSON blob with all required keys
    m = re.search(r'\{[^{}]*"problem_type"[^{}]*"severity"[^{}]*\}', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    return None


def chat_with_ai(
    image_base64: str,
    conversation_history: list,
    is_first_message: bool
) -> dict:
    client = OpenAI(
        api_key=settings.XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    mime = _detect_mime(image_base64)

    if is_first_message:
        # Turn 1: Vision model sees the image and asks first question
        # We also get a description to store for subsequent turns
        messages = [
            {"role": "system", "content": FIRST_TURN_SYSTEM},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{image_base64}"
                        }
                    },
                    {"type": "text", "text": "هاهي الصورة ديال المشكلة"}
                ]
            }
        ]

        response = client.chat.completions.create(
            model="grok-2-vision-1212",
            messages=messages,
            max_tokens=200,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        print(f"[CHAT T1] {raw[:100]}")

        # Also get a description for context in later turns
        img_desc = _get_image_description(client, image_base64, mime)
        print(f"[CHAT IMG DESC] {img_desc}")

        # Embed the description into the message so the frontend stores it
        # The frontend will include this in conversation_history for future turns
        return {
            "message": raw,
            "is_final": False,
            "analysis": None,
            "image_description": img_desc  # stored by frontend in history as system context
        }

    else:
        # Turn 2+: text-only model, but system prompt includes what the AI saw in the image
        # Extract image description from history if stored
        img_desc = "The client uploaded a photo showing a home repair problem."
        for msg in conversation_history:
            if msg.get("role") == "system" and msg.get("content", "").startswith("IMAGE:"):
                img_desc = msg["content"][6:].strip()
                break

        image_context = f"From the client's photo you already analyzed, you identified: {img_desc}"
        system = SYSTEM_PROMPT_TEMPLATE.format(image_context=image_context)

        messages = [{"role": "system", "content": system}]
        for msg in conversation_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": str(content)})

        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=messages,
            max_tokens=600,
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        print(f"[CHAT T2+] {raw[:150]}")

        data = _parse_final_analysis(raw)
        if data:
            from app.ai.price_model import predict
            normalized_problem_type = _normalize_problem_type(data.get("problem_type", "gebbas"))
            try:
                price = predict(
                    problem_type=normalized_problem_type,
                    severity=data.get("severity", 3),
                    surface_area_m2=data.get("surface_area_m2", 1.0),
                    complexity=data.get("complexity", "moyenne"),
                    nb_elements_affected=data.get("nb_elements_affected", 1),
                    city="agadir",
                )
            except Exception:
                price = {"price": 400.0, "duration_hours": 3.0}

            price_val = price.get("price", 400.0)
            duration_val = price.get("duration_hours", 3.0)

            return {
                "message": data.get("message", "فهمت المشكلة ديالك، هاهي النتيجة:"),
                "is_final": True,
                "analysis": {
                    "problem_type":     normalized_problem_type,
                    "description":      data.get("description", ""),
                    "diagnosis_notes":  data.get("diagnosis_notes", ""),
                    "severity":         data.get("severity", 3),
                    "surface_area_m2":  data.get("surface_area_m2", 1.0),
                    "complexity":       data.get("complexity", "moyenne"),
                    "nb_elements_affected": data.get("nb_elements_affected", 1),
                    "confidence":       data.get("confidence", "medium"),
                    # These keys match the frontend AiResult interface
                    "price":            round(price_val),
                    "duration_hours":   round(duration_val, 1),
                }
            }

        return {
            "message": raw,
            "is_final": False,
            "analysis": None
        }
