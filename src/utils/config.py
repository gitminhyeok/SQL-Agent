import os
from pathlib import Path

# __file__ = src/utils/config.py

ROOT_DIR = Path(__file__).parent.parent.parent  # (SQL_agent)

# Data Path
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "chinook.db"

# MetaData Path 
METADATA_DIR = ROOT_DIR / "metadata"
SCHEMA_PATH = METADATA_DIR / "schema_metadata.yaml"
GOLDEN_SQL_PATH = METADATA_DIR / "golden_sqls.json"

# Vector DB and Model Path
VECTOR_STORE_DIR = ROOT_DIR / "vector_store"
MODEL_DIR = ROOT_DIR / "models"
EMBEDDING_MODEL_NAME = "dragonkue/bge-m3-ko"


def ensure_directories():
    DATA_DIR.mkdir(exist_ok=True)
    METADATA_DIR.mkdir(exist_ok=True)
    VECTOR_STORE_DIR.mkdir(exist_ok=True)
    MODEL_DIR.mkdir(exist_ok=True)

ensure_directories()


# Open AI LLM Models
BASE_LLM_MODEL = "gpt-4.1-mini-2025-04-14"
SQL_LLM_MODEL = "gpt-5-mini-2025-08-07"