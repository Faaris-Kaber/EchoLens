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

# make sure tables exist in the database
Base.metadata.create_all(bind=engine)

# load environment variables from .env and set up OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("echolens")

# start fastapi app
app = FastAPI()

# add gzip compression and allow frontend to talk to backend
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create a db session and clean it up after

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# incoming request should include a text field
class TextRequest(BaseModel):
    text: str

# --- load the ml models well use ---

logger.info("loading political bias model")
bias_model_name = "premsa/political-bias-prediction-allsides-BERT"
bias_model = AutoModelForSequenceClassification.from_pretrained(bias_model_name)
bias_tokenizer = AutoTokenizer.from_pretrained(bias_model_name)
bias_labels = {i: label for i, label in enumerate(["Left", "Center", "Right"])}
BIAS_MAX_LEN = min(bias_tokenizer.model_max_length, bias_model.config.max_position_embeddings)

logger.info("loading emotion model")
emotion_model_name = "j-hartmann/emotion-english-distilroberta-base"
emotion_model = AutoModelForSequenceClassification.from_pretrained(emotion_model_name)
emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_model_name)
EMOTION_MAX_LEN = min(emotion_tokenizer.model_max_length, emotion_model.config.max_position_embeddings)

# helper function to run a model and get its top prediction

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

# this route handles analysis (bias + emotion)
@app.post("/analyze")
async def analyze_text(req: TextRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    if not text:
        return {"error": "text cannot be empty"}

    try:
        bias_result = run_model(text, bias_tokenizer, bias_model, bias_labels, BIAS_MAX_LEN)
    except Exception as e:
        logger.warning(f"bias model error: {e}")
        bias_result = {"error": str(e)}

    try:
        emotion_result = run_model(text, emotion_tokenizer, emotion_model, emotion_model.config.id2label, EMOTION_MAX_LEN)
    except Exception as e:
        logger.warning(f"emotion model error: {e}")
        emotion_result = {"error": str(e)}

    # log this analysis session to the database
    entry = History(text=text, mode="analyze", results={"bias": bias_result, "emotion": emotion_result})
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {"bias": bias_result, "emotion": emotion_result}

# this route asks gpt to create arguments for both sides of a topic
@app.post("/debate")
async def debate_from_text(req: TextRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    if not text:
        return {"error": "text cannot be empty"}

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "you are a debate assistant. your job is to:\n"
                        "1. read the user's input (article or opinion)\n"
                        "2. extract the core claim\n"
                        "3. write clear points both for and against\n\n"
                        "format:\n"
                        "Claim: <core claim>\n\n"
                        "Arguments For:\n- point 1\n- point 2\n\n"
                        "Arguments Against:\n- point 1\n- point 2\n"
                    )
                },
                {"role": "user", "content": f"text:\n{text}\n\nextract claim and both sides"}
            ],
            temperature=0.7,
            max_tokens=600
        )
        content = response.choices[0].message.content.strip()

        # pull out the claim, for points, and against points
        claim_match = re.search(r"Claim:\s*(.+)", content)
        claim = claim_match.group(1).strip() if claim_match else "no clear claim found"

        for_section = re.findall(r"Arguments For:\s*((?:- .+\n?)+)", content)
        for_points = [line[2:].strip() for line in for_section[0].splitlines()] if for_section else []

        against_section = re.findall(r"Arguments Against:\s*((?:- .+\n?)+)", content)
        against_points = [line[2:].strip() for line in against_section[0].splitlines()] if against_section else []

        # store this debate session in the database
        entry = History(text=text, mode="debate", results={"claim": claim, "for": for_points, "against": against_points})
        db.add(entry)
        db.commit()
        db.refresh(entry)

        return {
            "claim": claim,
            "for": for_points[:3],
            "against": against_points[:3]
        }

    except Exception as e:
        logger.warning(f"debate generation error: {e}")
        return {"error": str(e)}

# this returns the 10 most recent sessions
@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(History).order_by(History.created_at.desc()).limit(10).all()

# run the server if script is called directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
