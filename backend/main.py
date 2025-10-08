from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import torch
import torch.nn.functional as F
import logging
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import numpy as np

from backend.db import engine, get_db, check_db_connection
from backend.models import Base, History

from newspaper import Article
import requests
from bs4 import BeautifulSoup

load_dotenv()

# grab env variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./echolens.db")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# model names
BIAS_MODEL_NAME = "premsa/political-bias-prediction-allsides-BERT"
EMOTION_MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('echolens.log')
    ]
)
logger = logging.getLogger("echolens")

# global model vars loaded on startup
bias_model = None
bias_tokenizer = None
bias_labels = None
bias_max_len = None

emotion_model = None
emotion_tokenizer = None
emotion_max_len = None

# openai client
client = None

# request validation
class TextRequest(BaseModel):
    text: str
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('text cannot be empty')
        if len(v) > 10000:
            raise ValueError('text too long (max 10000 characters)')
        return v

# load models on startup cleanup on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    global bias_model, bias_tokenizer, bias_labels, bias_max_len
    global emotion_model, emotion_tokenizer, emotion_max_len
    global client
    
    logger.info("=== Starting EchoLens API ===")
    
    # create db tables
    logger.info("Initializing database tables")
    Base.metadata.create_all(bind=engine)
    
    # init openai
    logger.info("Initializing OpenAI client")
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=30.0)
    
    # load models
    try:
        logger.info("Loading political bias model...")
        bias_model = AutoModelForSequenceClassification.from_pretrained(BIAS_MODEL_NAME)
        bias_tokenizer = AutoTokenizer.from_pretrained(BIAS_MODEL_NAME)
        bias_model.eval()
        bias_labels = {0: "Left", 1: "Center", 2: "Right"}
        bias_max_len = min(
            bias_tokenizer.model_max_length,
            bias_model.config.max_position_embeddings
        )
        logger.info(f"✓ Bias model loaded (max_len={bias_max_len})")
        
        logger.info("Loading emotion model...")
        emotion_model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL_NAME)
        emotion_tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL_NAME)
        emotion_model.eval()
        emotion_max_len = min(
            emotion_tokenizer.model_max_length,
            emotion_model.config.max_position_embeddings
        )
        logger.info(f"✓ Emotion model loaded (max_len={emotion_max_len})")
        
        logger.info("=== All models loaded successfully ===")
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}", exc_info=True)
        raise
    
    yield
    
    logger.info("=== Shutting down EchoLens API ===")

# init fastapi
app = FastAPI(
    title="EchoLens API",
    description="Political bias and emotion analysis API with debate generation",
    version="1.0.0",
    lifespan=lifespan
)

# add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# save analysis to database
def save_to_history(db: Session, text: str, mode: str, results: dict):
    try:
        entry = History(text=text, mode=mode, results=results)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        logger.info(f"{mode.capitalize()} saved to DB (id={entry.id})")
    except Exception as e:
        logger.error(f"Database error: {e}", exc_info=True)
        db.rollback()

# split text into semantic chunks that fit model context
def intelligent_chunk(text: str, max_tokens: int = 450):
    sentences = text.replace('\n\n', '. ').replace('\n', '. ').split('. ')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_tokens = len(bias_tokenizer.encode(sentence, add_special_tokens=True))
        
        if current_length + sentence_tokens > max_tokens and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_length += sentence_tokens
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

# analyze text in chunks and aggregate results
def analyze_long_text(text: str):
    chunks = intelligent_chunk(text)
    
    logger.info(f"Processing {len(chunks)} chunk(s)")
    
    # if text fits in one chunk process normally
    if len(chunks) == 1:
        return analyze_single_chunk(chunks[0])
    
    # process each chunk
    all_bias_results = []
    all_emotion_results = []
    
    for i, chunk in enumerate(chunks):
        logger.info(f"Analyzing chunk {i+1}/{len(chunks)}")
        result = analyze_single_chunk(chunk)
        all_bias_results.append(result['bias'])
        all_emotion_results.append(result['emotion'])
    
    # aggregate bias using confidence-weighted logit averaging
    if all_bias_results and all_bias_results[0]:
        all_logits = []
        all_confidences = []
        
        for r in all_bias_results:
            if r:
                all_logits.append(r['logits'])
                all_confidences.append(r['confidence'])
        
        all_logits = np.array(all_logits)
        all_confidences = np.array(all_confidences)
        
        # weighted average of logits
        weighted_logits = np.average(all_logits, axis=0, weights=all_confidences)
        
        # apply softmax
        exp_logits = np.exp(weighted_logits - np.max(weighted_logits))
        avg_probs = exp_logits / np.sum(exp_logits)
        
        bias_label_idx = np.argmax(avg_probs)
        bias_label = bias_labels[bias_label_idx]
        
        # check for mixed bias between left and right
        chunk_labels = [r['label'] for r in all_bias_results if r]
        sorted_probs = sorted(avg_probs, reverse=True)
        confidence_margin = sorted_probs[0] - sorted_probs[1]
        
        # if chunks disagree between left and right classify as center
        has_left = 'Left' in chunk_labels
        has_right = 'Right' in chunk_labels
        
        if has_left and has_right and confidence_margin < 0.25:
            bias_label = "Center"
            bias_result = {
                'label': bias_label,
                'confidence': round(1.0 - confidence_margin, 3),
                'raw_scores': {
                    bias_labels[i]: round(float(avg_probs[i]), 3) 
                    for i in range(len(bias_labels))
                },
                'detected_as_mixed': True,
                'original_prediction': bias_labels[bias_label_idx]
            }
            logger.info(f"🎯 Mixed bias detected → Reclassified as Center (margin: {confidence_margin:.3f})")
        else:
            bias_result = {
                'label': bias_label,
                'confidence': round(float(avg_probs[bias_label_idx]), 3),
                'raw_scores': {
                    bias_labels[i]: round(float(avg_probs[i]), 3) 
                    for i in range(len(bias_labels))
                }
            }
        
        logger.info(f"Chunk confidences: {all_confidences.tolist()}")
        logger.info(f"Final result: {bias_label} ({bias_result['confidence']})")
    else:
        bias_result = None
    
    # aggregate emotion by most common
    if all_emotion_results and all_emotion_results[0]:
        emotion_labels = [e['label'] for e in all_emotion_results if e]
        emotion_label = max(set(emotion_labels), key=emotion_labels.count)
        avg_confidence = np.mean([e['confidence'] for e in all_emotion_results if e])
        emotion_result = {
            'label': emotion_label,
            'confidence': round(avg_confidence, 3),
            'raw_scores': all_emotion_results[0]['raw_scores']
        }
    else:
        emotion_result = None
    
    return {
        'bias': bias_result,
        'emotion': emotion_result,
        'chunks_processed': len(chunks)
    }

# analyze a single chunk of text
def analyze_single_chunk(text: str) -> dict:
    results = {"bias": None, "emotion": None}
    
    # run bias analysis
    try:
        results["bias"] = run_model(
            text, bias_tokenizer, bias_model, bias_labels, bias_max_len
        )
        logger.info(f"Bias logits: {results['bias']['logits']}")
        logger.info(f"Label mapping: {bias_labels}")
        logger.info(f"Raw scores: {results['bias']['raw_scores']}")
    except Exception as e:
        logger.error(f"Bias model error on chunk: {e}")
    
    # run emotion analysis
    try:
        results["emotion"] = run_model(
            text, 
            emotion_tokenizer, 
            emotion_model, 
            emotion_model.config.id2label, 
            emotion_max_len
        )
    except Exception as e:
        logger.error(f"Emotion model error on chunk: {e}")
    
    return results

# run inference on text
def run_model(text: str, tokenizer, model, label_map: dict, max_len: int) -> dict:
    try:
        inputs = tokenizer(
            text,
            truncation=True,
            max_length=max_len,
            padding="max_length",
            return_tensors="pt"
        )
        
        with torch.no_grad():
            logits = model(**inputs).logits
        
        # store raw logits for aggregation
        raw_logits = logits[0].cpu().numpy().tolist()
        
        probs = F.softmax(logits, dim=-1)[0]
        top_idx = torch.argmax(probs).item()
        
        result = {
            "label": label_map[top_idx],
            "confidence": round(probs[top_idx].item(), 3),
            "raw_scores": {
                label_map[i]: round(p.item(), 3) for i, p in enumerate(probs)
            },
            "logits": raw_logits
        }
        
        # cleanup memory
        del inputs, logits, probs
        
        return result
        
    except Exception as e:
        logger.error(f"Model inference error: {e}", exc_info=True)
        raise

# root endpoint
@app.get("/", tags=["root"])
def root():
    return {
        "message": "EchoLens API",
        "status": "running",
        "version": "1.0.0"
    }

# health check
@app.get("/health", tags=["health"])
def health_check():
    healthy = bias_model and emotion_model and client
    return {
        "status": "healthy" if healthy else "degraded",
        "models_loaded": bool(healthy)
    }

# scrape article from url
@app.post("/scrape")
async def scrape_url(data: dict):
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    
    # try newspaper3k first
    try:
        article = Article(url)
        article.config.browser_user_agent = 'Mozilla/5.0'
        article.download()
        article.parse()
        
        if article.text and len(article.text) > 100:
            return {"success": True, "text": article.text, "title": article.title, "url": url}
    except:
        pass
    
    # fallback to beautifulsoup
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # remove junk
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # get paragraphs
        paragraphs = soup.find_all('p')
        text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
        
        if len(text) < 100:
            raise HTTPException(status_code=400, detail="Could not extract article content")
        
        title = soup.find('title')
        return {
            "success": True,
            "text": text,
            "title": title.get_text() if title else None,
            "url": url
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape: {str(e)}")

# analyze text for bias and emotion
@app.post("/analyze", tags=["analysis"], status_code=status.HTTP_200_OK)
async def analyze_text(req: TextRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    
    # use chunking for long texts
    results = analyze_long_text(text)
    
    # if both models failed return error
    if not results["bias"] and not results["emotion"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Both analysis models failed. Please try again."
        )
    
    # save to database
    save_to_history(db, text, "analyze", results)
    
    return results

# generate debate arguments
@app.post("/debate", tags=["debate"], status_code=status.HTTP_200_OK)
async def debate_from_text(req: TextRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    
    try:
        logger.info("Generating debate arguments via OpenAI")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a debate assistant. Extract the core claim from the text "
                        "and generate 3 arguments for and 3 arguments against it. "
                        "Return your response as JSON with this exact structure: "
                        '{"claim": "the main claim", "for": ["point 1", "point 2", "point 3"], '
                        '"against": ["point 1", "point 2", "point 3"]}'
                    )
                },
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=600
        )
        
        # parse json directly
        result = json.loads(response.choices[0].message.content)
        
        # save to database
        save_to_history(db, text, "debate", result)
        
        return result
        
    except Exception as e:
        logger.error(f"Debate generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate debate: {str(e)}"
        )

# get recent analysis history
@app.get("/history", tags=["history"])
def get_history(db: Session = Depends(get_db), limit: int = 10):
    if limit > 50:
        limit = 50
    
    try:
        records = db.query(History).order_by(History.created_at.desc()).limit(limit).all()
        return [record.to_dict() for record in records]
    except Exception as e:
        logger.error(f"Error fetching history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch history"
        )

# run server
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
