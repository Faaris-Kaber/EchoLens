FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download ML models during build (saves ~2-3 minutes on startup)
RUN python -c "\
from transformers import AutoModelForSequenceClassification, AutoTokenizer; \
print('Downloading bias model...'); \
AutoModelForSequenceClassification.from_pretrained('premsa/political-bias-prediction-allsides-BERT'); \
AutoTokenizer.from_pretrained('premsa/political-bias-prediction-allsides-BERT'); \
print('Downloading emotion model...'); \
AutoModelForSequenceClassification.from_pretrained('j-hartmann/emotion-english-distilroberta-base'); \
AutoTokenizer.from_pretrained('j-hartmann/emotion-english-distilroberta-base'); \
print('Models downloaded successfully!')"

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
