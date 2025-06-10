from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))  # ✅ use sqlalchemy.text()
    print("✅ Connected to the database successfully!")
except Exception as e:
    print("❌ Connection failed:", e)
