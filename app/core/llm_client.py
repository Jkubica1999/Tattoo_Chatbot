import os, json
from typing import Optional, List, Dict, Callable
from openai import OpenAI

MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
MAX_OUT = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "120"))
TEMP = float(os.getenv("LLM_TEMPERATURE", "0.3"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

_client: Optional[OpenAI] = None
def client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client

def complete_json(messages: List[Dict], validate: Callable[[dict], object]) -> Optional[dict]:
    """Call the model once; if invalid JSON or schema fails, try one repair prompt. Else return None."""
    def _call(msgs) -> str:
        res = client().chat.completions.create(
            model=MODEL,
            messages=msgs,
            temperature=TEMP,
            max_tokens=MAX_OUT,
            response_format={"type": "json_object"},
        )
        content = res.choices[0].message.content
        if content is None:
            raise ValueError("LLM response had no content")
        return content

    # attempt 1
    try:
        data = json.loads(_call(messages))
        validate(data)  # pydantic validation callable
        return data
    except Exception:
        pass

    # repair attempt
    repair_msgs = [{"role": "system", "content": "Return ONLY valid JSON that matches the requested schema."}] + messages
    try:
        data = json.loads(_call(repair_msgs))
        validate(data)
        return data
    except Exception:
        return None