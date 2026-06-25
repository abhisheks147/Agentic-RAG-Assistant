from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()


class Settings(BaseSettings):
    
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/agentic"
    REDIS_URL: str = "redis://localhost:6379/0"

   
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "gemini-1.5-flash"

    
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"



settings = Settings()


print("✅ GEMINI KEY LOADED:", bool(settings.GEMINI_API_KEY))