# EchoLens

EchoLens is an AI tool that helps you cut through political bias in the media. It analyzes any article to reveal emotional tone, detect bias, and assess source credibility. Its Debate Mode generates balanced arguments from both sides of an issue, helping you see the bigger picture instead of just one perspective.

## What It Does

EchoLens helps you understand bias in news coverage by analyzing articles and showing both sides of controversial topics. It uses AI models trained on thousands of news articles to detect political slant and emotional tone.

**Main Features:**
- Detects political bias (Left / Center / Right)
- Identifies emotional language in media
- Automatically extracts article text from URLs
- Rates source bias using AllSides data
- Generates debate arguments for both sides using GPT-4
- Saves analysis sessions for easy comparison

## Screenshots

<img width="1913" height="913" alt="ELSS" src="https://github.com/user-attachments/assets/d0292570-287c-4038-a2ee-3096ab86c11e" />

<img width="1917" height="914" alt="ELSS1" src="https://github.com/user-attachments/assets/e06156c2-f604-497b-950b-59ad982fcb64" />

<img width="1908" height="907" alt="ELSS2" src="https://github.com/user-attachments/assets/d0fe9a63-6529-40ea-9b98-055456f9875b" />

<img width="1917" height="917" alt="ELSS3" src="https://github.com/user-attachments/assets/833b50bf-2bcc-42ba-b1c0-acee79e92a12" />

## Tech Stack

**Frontend:**
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS

**Backend:**
- Python 3.11
- FastAPI
- PyTorch
- HuggingFace Transformers
- OpenAI API (GPT-4)

**AI Models:**
- BERT (political bias detection)
- DistilRoBERTa (emotion analysis)

**Database:**
- PostgreSQL
- SQLAlchemy ORM

**DevOps:**
- Docker & Docker Compose
- Uvicorn ASGI server

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/Faaris-Kaber/EchoLens.git
   cd echolens
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your OpenAI API key.

3. **Start with Docker**
   ```bash
   docker compose up --build
   ```

4. **Open the app**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

> **Note:** The first startup will take a few minutes to download the AI models (~2GB).

## Project Structure

```
echolens/
├── app/                    # Next.js pages & routing
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Main page
├── backend/                # FastAPI backend
│   ├── db.py               # Database connection
│   ├── main.py             # API routes & ML inference
│   └── models.py           # SQLAlchemy models
├── components/             # React components
│   ├── BiasCompass.tsx     # Bias visualization
│   ├── DebateResults.tsx   # Debate arguments display
│   ├── EmotionBadge.tsx    # Emotion indicator
│   ├── Header.tsx          # App header
│   ├── MainContent.tsx     # Main analysis UI
│   └── SideNavbar.tsx      # Session sidebar
├── docker/                 # Docker configuration
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── lib/                    # Shared utilities
│   ├── helpers.ts          # Helper functions
│   └── types.ts            # TypeScript types
├── public/                 # Static assets
│   └── data/               # Bias rating data
├── docker-compose.yml      # Docker orchestration
├── package.json            # Frontend dependencies
└── requirements.txt        # Backend dependencies
```

## How It Works

**Bias Detection Pipeline:**

1. Scrapes article text from the URL using newspaper3k
2. Extracts the domain and checks it against AllSides source ratings
3. Splits long articles into sentence-based chunks (~450 tokens each)
4. Runs each chunk through a BERT model trained on labeled news articles
5. Combines predictions using confidence-weighted logit averaging

**Debate Mode:**

Sends your text to GPT-4 with a prompt to extract the main claim and generate balanced arguments for both sides.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/analyze` | POST | Analyze text for bias & emotion |
| `/debate` | POST | Generate debate arguments |
| `/scrape` | POST | Extract article from URL |
| `/history` | GET | Get analysis history |

## Why I Built This

As someone who keeps up with politics, I couldn't help but see how political polarization is driving us apart. A large reason for this polarization is the echo chambers we unknowingly put ourselves into—social environments where we don't get to hear charitable interpretations of the "other side."

EchoLens was made to help you see through these echo chambers by showing you which way a text leans, the credibility of the source, and the emotions it evokes. Combined with "Explore Both Sides," it reminds you how the media you consume tends to lean and presents counterpoints you might not have heard before.

## About Me

I'm Faaris Kaber, a computer engineering student at the University of Guelph passionate about AI and technology, and interested in how technology influences human discourse.

## License

MIT
