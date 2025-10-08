# EchoLens

EchoLens is an AI tool that helps you cut through political bias in the media. It analyzes any article to reveal emotional tone, detect bias, and assess source credibility. Its Debate Mode generates balanced arguments from both sides of an issue, helping you see the bigger picture instead of just one perspective.

# What it does

EchoLens helps you understand bias in news coverage by analyzing articles and showing both sides of controversial topics. It uses AI models trained on thousands of news articles to detect political slant and emotional tone.

Main features:
- Detects political bias (Left / Center / Right)
- Identifies emotional language in media
- Automatically extracts article text from URLs
- Rates source bias using AllSides data
- Generates debate arguments for both sides using GPT-4
- Saves analysis sessions for easy comparison


# Tech stack

Frontend:
- Next.js 15.5
- React 19
- TypeScript
- Tailwind CSS

Backend:
- Python 3.10
- FastAPI
- PyTorch
- HuggingFace Transformers
- OpenAI API (GPT-4)

AI Models:
- BERT (political bias detection)
- DistilRoBERTa (emotion analysis)

Database:
- PostgreSQL
- SQLAlchemy ORM

DevOps:
- Docker & Docker Compose
- Uvicorn ASGI server

Everything runs in Docker for easy deployment


# How to run it

You need Docker and an OpenAI API key

1. Clone the repo
    https://github.com/Faaris-Kaber/EchoLens.git
   
    cd echolens
3. Create a `.env` file in the backend folder
    OPENAI_API_KEY=your_key_here
    DATABASE_URL=postgresql://postgres:postgres@postgres:5432/echolens
4. Start everything with Docker
    docker-compose up --build

5. Open http://localhost:3000

The app will download the AI models on first startup


# How it works

The bias detection works like this:

1. Scrapes article text from the URL using newspaper3k
2. Extracts the domain and checks it against AllSides source ratings
3. Splits long articles into sentence-based chunks (approx. 450 tokens each, never mid-sentence)
4. Runs each chunk through a BERT model trained on labeled news articles
5. Combines the predictions using confidence-weighted logit averaging
6. For the "explore both sides" it sends your text to GPT-4 with a prompt asking it to extract the main claim and generate arguments for both sides. This helps you understand different perspectives on controversial topics.


# Project structure:

- app/ — Next.js frontend  
- backend/ — FastAPI backend  
- public/ — static assets  
- docker-compose.yml & Dockerfile — deployment setup  
- requirements.txt — backend dependencies  
- package.json — frontend dependencies

# Why I built this:
As someone who keeps up with politics I could not help but see how political polarization is driving us apart. A large reason for this polarization is because of the echo chambers we are unknowingly putting ourselves into. Social enviroments where we do not get to hear charitable interpertations of the "other side" and what results is a divisoin. Echolens was made to help you see through these echo chanmbers by telling you which way this text leans, the credibiltiy of the source and the emotion they evoke. This in combination with the "explore both sides" aims to remind you of how the media you are consuming tends to be leaning and counterpoints you might not have heard before. 

# About me
I am Faaris Kaber, a computer engineering student at the University of Guelph who’s passionate about AI and technology, and interested in how technology is influencing the discourse of humans

# License
MIT
