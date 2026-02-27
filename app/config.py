import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/fraud_sharing")
SECRET_PEPPER = os.getenv("SECRET_PEPPER", "")
ESTAFF_API_URL = os.getenv("ESTAFF_API_URL", "")
ESTAFF_API_KEY = os.getenv("ESTAFF_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
