from fastapi import FastAPI, Depends
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
import torch
import torch.nn.functional as F
import logging
from openai import OpenAI
import os
import re
from dotenv import load_dotenv

from backend.db import engine, SessionLocal
from backend.models import Base, History

Base.metadata.create_all(bind=engine)

# Load environment variables and OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("echolens")

# FastAPI setup
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Input model
class TextRequest(BaseModel):
    text: str

# --- Load ML Models ---
logger.info("Loading political bias model...")
bias_model_name = "premsa/political-bias-prediction-allsides-BERT"
bias_model = AutoModelForSequenceClassification.from_pretrained(bias_model_name)
bias_tokenizer = AutoTokenizer.from_pretrained(bias_model_name)
bias_labels = {i: label for i, label in enumerate(["Left", "Center", "Right"])}
BIAS_MAX_LEN = min(bias_tokenizer.model_max_length, bias_model.config.max_position_embeddings)

logger.info("Loading emotion model...")
emotion_model_name = "j-hartmann/emotion-english-distilroberta-base"
emotion_model = AutoModelForSequenceClassification.from_pretrained(emotion_model_name)
emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_model_name)
EMOTION_MAX_LEN = min(emotion_tokenizer.model_max_length, emotion_model.config.max_position_embeddings)

# --- Helpers ---
def run_model(text, tokenizer, model, label_map, max_len):
    inputs = tokenizer(
        text,
        truncation=True,
        max_length=max_len,
        padding="max_length",
        return_tensors="pt"
    )
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=-1)
    avg_probs = torch.mean(probs, dim=0)
    top_idx = torch.argmax(avg_probs).item()
    return {
        "label": label_map[top_idx],
        "confidence": round(avg_probs[top_idx].item(), 3),
        "raw_scores": {
            label_map[i]: round(p.item(), 3) for i, p in enumerate(avg_probs)
        }
    }

# --- Routes ---
@app.post("/analyze")
async def analyze_text(req: TextRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    if not text:
        return {"error": "Text cannot be empty."}

    try:
        bias_result = run_model(text, bias_tokenizer, bias_model, bias_labels, BIAS_MAX_LEN)
    except Exception as e:
        logger.warning(f"Bias model error: {e}")
        bias_result = {"error": str(e)}

    try:
        emotion_result = run_model(text, emotion_tokenizer, emotion_model, emotion_model.config.id2label, EMOTION_MAX_LEN)
    except Exception as e:
        logger.warning(f"Emotion model error: {e}")
        emotion_result = {"error": str(e)}

    # Save to DB
    entry = History(text=text, mode="analyze", results={"bias": bias_result, "emotion": emotion_result})
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {"bias": bias_result, "emotion": emotion_result}

@app.post("/debate")
async def debate_from_text(req: TextRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    if not text:
        return {"error": "Text cannot be empty."}

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a debate assistant. Your job is to:\n\n"
                        "1. Read the user's input (which may include an article, opinion, or paragraph).\n"
                        "2. Extract the core claim.\n"
                        "3. Generate strong arguments both FOR and AGAINST.\n\n"
                        "Format:\n"
                        "Claim: <central claim>\n\n"
                        "Arguments For:\n- ...\n- ...\n\n"
                        "Arguments Against:\n- ...\n- ...\n"
                        "Use hyphens, be punchy, and keep points to 1-2 sentences."
                    )
                },
                {"role": "user", "content": f"Text:\n{text}\n\nExtract a claim and generate both sides."}
            ],
            temperature=0.7,
            max_tokens=600
        )
        content = response.choices[0].message.content.strip()
        claim_match = re.search(r"Claim:\s*(.+)", content)
        claim = claim_match.group(1).strip() if claim_match else "No clear claim found"
        for_section = re.findall(r"Arguments For:\s*((?:- .+\n?)+)", content)
        for_points = [line[2:].strip() for line in for_section[0].splitlines()] if for_section else []
        against_section = re.findall(r"Arguments Against:\s*((?:- .+\n?)+)", content)
        against_points = [line[2:].strip() for line in against_section[0].splitlines()] if against_section else []

        entry = History(text=text, mode="debate", results={"claim": claim, "for": for_points, "against": against_points})
        db.add(entry)
        db.commit()
        db.refresh(entry)

        return {"claim": claim, "for": for_points[:3], "against": against_points[:3]}

    except Exception as e:
        logger.warning(f"Debate generation error: {e}")
        return {"error": str(e)}

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(History).order_by(History.created_at.desc()).limit(10).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
