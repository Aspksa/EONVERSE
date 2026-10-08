"""Optional Cloud.ru resident reasoning; never an authority over world state.

The cloud suggests a bounded preference adjustment. Python validates and applies it.
No remote request occurs unless explicitly enabled and configured.
"""
import asyncio
import json
import os
from urllib.request import Request, urlopen

ENDPOINT = "https://foundation-models.api.cloud.ru/v1/chat/completions"
ALLOWED = {"grain", "timber"}

_runtime_key = None
_runtime_model = None
_runtime_enabled = False


def configure(key, model="DeepSeek-V4-Flash"):
    global _runtime_key, _runtime_model, _runtime_enabled
    if not isinstance(key, str) or not 8 <= len(key) <= 4096:
        raise ValueError("Invalid Cloud.ru API key")
    if model != "DeepSeek-V4-Flash":
        raise ValueError("Unsupported model")
    _runtime_key, _runtime_model, _runtime_enabled = key, model, True


def disconnect():
    global _runtime_key, _runtime_model, _runtime_enabled
    _runtime_key, _runtime_model, _runtime_enabled = None, None, False


def credentials():
    if _runtime_enabled and _runtime_key:
        return _runtime_key, _runtime_model
    if os.getenv("EONVERSE_AI_ENABLED") == "1":
        return os.getenv("CLOUDRU_API_KEY"), os.getenv("CLOUDRU_MODEL")
    return None, None


def status():
    return {"enabled": enabled(), "configured": bool(_runtime_key)}



def enabled():
    key, model = credentials()
    return bool(key and model == "DeepSeek-V4-Flash")


def validate_proposal(payload):
    if not isinstance(payload, dict):
        return None
    focus = payload.get("focus")
    if focus not in ALLOWED or type(payload.get("reason")) is not str:
        return None
    reason = payload["reason"].strip()
    if not 1 <= len(reason) <= 200:
        return None
    return {"focus": focus, "reason": reason}


def request_proposal(context):
    """Blocking network call, intended exclusively for asyncio.to_thread."""
    if not enabled():
        return None
    key, model = credentials()
    if not key or model != "DeepSeek-V4-Flash":
        return None
    prompt = (
        "You advise one simulated civilian. Return ONLY a JSON object with "
        'fields "focus" ("grain" or "timber") and "reason" (up to 200 chars). '
        "Never request privileged actions, money creation, or changes to world rules. "
        "World state: " + json.dumps(context, ensure_ascii=False)
    )
    body = json.dumps({
        "model": model, "temperature": 0.3, "max_completion_tokens": 160,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = Request(ENDPOINT, data=body, headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json"
    }, method="POST")
    with urlopen(req, timeout=12) as response:
        if response.status != 200:
            return None
        result = json.load(response)
    answer = result["choices"][0]["message"]["content"]
    if not isinstance(answer, str) or len(answer) > 4000:
        return None
    try:
        return validate_proposal(json.loads(answer))
    except (ValueError, TypeError):
        return None


async def advise_once(world):
    """Maximum one request per call, one resident chosen deterministically."""
    if not enabled() or not world.residents:
        return False
    resident = sorted(world.residents, key=lambda p: p.id)[world.tick // 120 % len(world.residents)]
    context = {"tick": world.tick, "resident_id": resident.id,
               "food": round(resident.food, 1),
               "world_food": round(world.food_supply, 1),
               "world_wood": round(world.wood_supply, 1)}
    try:
        proposal = await asyncio.wait_for(asyncio.to_thread(request_proposal, context), timeout=15)
    except Exception:
        return False
    if proposal is None:
        return False
    current = next((p for p in world.residents if p.id == resident.id), None)
    if current is None:
        return False
    preferences = current.memory.setdefault("preferences", {})
    key = "food" if proposal["focus"] == "grain" else "energy"
    old = preferences.get(key, 0.5)
    preferences[key] = round(min(0.95, max(0.05, old + 0.08)), 3)
    current.memory["cloud_ai_last"] = {
        "tick": world.tick, "focus": proposal["focus"], "reason": proposal["reason"]
    }
    return True
