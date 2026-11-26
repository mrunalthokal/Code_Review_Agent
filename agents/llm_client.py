"""Optional Gemini augmentation. Static rules always run; the LLM adds extra findings."""
import json
import re

from config import GEMINI_API_KEY, GEMINI_MODEL
from models import Finding, Severity


def llm_available() -> bool:
    return bool(GEMINI_API_KEY)


def _ask_json(system, user):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY)
    res = client.models.generate_content(
        model=GEMINI_MODEL, contents=user,
        config=types.GenerateContentConfig(system_instruction=system,
                                           response_mime_type="application/json", temperature=0.1))
    text = re.sub(r"^```(?:json)?|```$", "", res.text.strip(), flags=re.M).strip()
    return json.loads(text)


def llm_review(agent_name, focus, sub, existing):
    """Returns (findings, note). Never raises - failures become a note."""
    if not llm_available():
        return [], "Gemini skipped: no API key"
    lines = sub.code.splitlines()
    numbered = "\n".join(f"{i}: {l}" for i, l in enumerate(lines[:400], 1))
    known = "\n".join(f"line {f.line}: {f.title}" for f in existing) or "none"
    system = (f"You are a senior {focus} reviewer. Reply ONLY with a JSON array (max 8 items). "
              'Each item: {"title","category","severity" (Critical|High|Medium|Low|Info),'
              '"line" (int),"description","recommendation","owasp","cwe"}. '
              "Report only real issues not already listed. Return [] if none.")
    user = f"Language: {sub.language}\nAlready detected (do NOT repeat):\n{known}\n\nCode:\n{numbered}"
    try:
        data = _ask_json(system, user)
        out = []
        for it in data[:8]:
            line = int(it.get("line") or 0)
            if not 1 <= line <= len(lines):
                continue
            out.append(Finding(
                agent=agent_name, rule_id="LLM", title=str(it.get("title", "AI finding"))[:80],
                category=str(it.get("category", focus)), severity=Severity.parse(it.get("severity")),
                line=line, description=str(it.get("description", "")),
                recommendation=str(it.get("recommendation", "")), snippet=lines[line - 1].strip()[:160],
                owasp=str(it.get("owasp", "")), cwe=str(it.get("cwe", "")), source="llm"))
        return out, f"Gemini ({GEMINI_MODEL}) added {len(out)} finding(s)"
    except Exception as e:
        return [], f"Gemini failed: {str(e)[:120]}"
