# backend/main.py

from backend.banking_knowledge import BANKING_KNOWLEDGE
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

# ================= CONFIG =================
OLLAMA_SERVER = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3"

# ================= LOGGING =================
logging.basicConfig(
    filename="backend_audit.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# ================= FASTAPI =================
app = FastAPI(title="Banking Chatbot Backend (Ollama)")

# ================= REQUEST MODEL =================
class ChatRequest(BaseModel):
    message: str

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
You are a BANKING DOMAIN EXPERT.

Rules:
- Answer ONLY banking-related questions
- Give long, detailed, student-friendly answers
- Explain with:
  • definition
  • purpose
  • features
  • examples
  • advantages
- Do NOT ask for PIN, OTP, or account numbers
- Do NOT perform transactions

If the question is NOT related to banking, reply exactly:
"I can answer only banking-related questions."
"""

# ================= BANKING FILTER =================
def is_banking_question(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in BANKING_KNOWLEDGE)

# ================= CHAT API =================
@app.post("/api/chat")
async def chat(req: ChatRequest):
    question = req.message.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Empty message")

    logging.info("USER QUESTION: %s", question)

    # ❌ BLOCK NON-BANKING QUESTIONS
    if not is_banking_question(question):
        return {"reply": "I can answer only banking-related questions."}

    # 🤖 OLLAMA GENERATES ANSWER (NO HARDCODED ANSWERS)
    prompt = f"""
{SYSTEM_PROMPT}

User Question:
{question}

Answer in detail:
"""

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{OLLAMA_SERVER}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 200
                    }
                }
            )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ollama error")

        data = response.json()
        reply = data.get("response", "").strip()

        return {"reply": reply}

    except Exception as e:
        logging.error(str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
