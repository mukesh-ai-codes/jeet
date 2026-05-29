"""Tara AI Tutor — core service. RAG + 3 modes + memory + frustration detection.
Model swappable via settings.TARA_MODEL (Gemini now, Claude later)."""
import os
from google import genai
from app.core.config import settings

CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                "..", "..", "..", "ml", "tara", "chroma_db"))

MODES = {
    "saathi": ("You are Tara, a warm encouraging study buddy for an Indian JEE/NEET "
        "student. Speak like a supportive friend (Hinglish okay). Motivating and kind. "
        "Use the NCERT context and its analogy if relevant. Keep it concise."),
    "strategist": ("You are Tara in Strategist mode — an exam-focused JEE/NEET coach. "
        "Direct, practical, score-optimized. Reference the NCERT context. Actionable "
        "steps. English-leaning, concise."),
    "guru": ("You are Tara in Guru mode — explain concepts deeply with rich Indian-life "
        "analogies. Use the NCERT context and its analogy. Build from first principles. "
        "Patient and thorough."),
}

FRUSTRATION_SIGNALS = ["i give up","i can't do this","i cant do this","this is impossible",
    "i'm so stupid","im so stupid","i hate this","i want to quit","i'm dropping",
    "im dropping","useless","i'll fail","ill fail","want to drop out"]

def detect_frustration(message: str, repeat_count: int = 0) -> bool:
    msg = message.lower()
    if any(s in msg for s in FRUSTRATION_SIGNALS): return True
    letters = [c for c in message if c.isalpha()]
    if len(letters) > 10 and sum(c.isupper() for c in letters)/len(letters) > 0.7: return True
    if repeat_count >= 3: return True
    return False

def retrieve_context(query: str, k: int = 2):
    try:
        import chromadb
        col = chromadb.PersistentClient(path=CHROMA_DIR).get_collection("ncert")
        res = col.query(query_texts=[query], n_results=k)
        docs = res.get("documents",[[]])[0]; metas = res.get("metadatas",[[]])[0]
        return [{"text":d,"meta":m} for d,m in zip(docs,metas)]
    except Exception:
        return []

_client = None
def _gemini():
    global _client
    if _client is None: _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client

def ask_tara(message: str, mode: str = "saathi", memory=None):
    import json, re
    mode = mode if mode in MODES else "saathi"
    keyword_frustrated = detect_frustration(message)  # fast-path
    ctx = retrieve_context(message)
    ctx_block = "\n\n".join(f"[NCERT] {d['text']}" for d in ctx) or "(no specific NCERT context)"
    mem_block = "\n".join(f"{m['role']}: {m['text']}" for m in (memory or [])[-6:])
    system = MODES[mode]
    system += (" If the student sounds frustrated/discouraged, lead with empathy and one "
        "small concrete next step; don't lecture.")
    # Ask for the reply AND a distress judgment in one call (no extra cost/latency).
    prompt = (f"{system}\n\nNCERT CONTEXT:\n{ctx_block}\n\n"
        + (f"RECENT:\n{mem_block}\n\n" if mem_block else "")
        + f"STUDENT: {message}\n\n"
        + "Respond as STRICT JSON only, no markdown: "
        + '{\"reply\": \"<your tutor reply>\", \"distressed\": <true/false '
        + "if the student sounds genuinely discouraged, hopeless, or wanting to quit>}")
    reply, llm_distressed = None, False
    try:
        r = _gemini().models.generate_content(model=settings.TARA_MODEL, contents=prompt)
        raw = r.text.strip()
        raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)
        reply = data.get("reply", "").strip()
        llm_distressed = bool(data.get("distressed", False))
    except Exception:
        # fallback: plain call without JSON if parsing fails
        try:
            r = _gemini().models.generate_content(model=settings.TARA_MODEL,
                contents=prompt.split("Respond as STRICT JSON")[0] + "TARA:")
            reply = r.text.strip()
        except Exception:
            reply = "I'm having trouble reaching my brain right now — try again in a moment?"
    if not reply:
        reply = "I'm here with you — tell me a bit more?"
    frustrated = keyword_frustrated or llm_distressed
    return {"reply":reply,"mode":mode,
        "sources":[d["meta"].get("chapter") for d in ctx],
        "frustration_detected":frustrated}
