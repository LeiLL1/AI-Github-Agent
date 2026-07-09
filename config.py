"""Runtime configuration for AI GitHub Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
LOG_DIR = BASE_DIR / "logs"

for directory in (DATA_DIR, CACHE_DIR, KNOWLEDGE_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

DB_PATH = DATA_DIR / "knowledge_base.db"

GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com").rstrip("/")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
if GITHUB_TOKEN.startswith("ghp_your_"):
    GITHUB_TOKEN = ""

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
if DEEPSEEK_API_KEY.startswith("sk-your_"):
    DEEPSEEK_API_KEY = ""
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1").rstrip("/")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
if OPENAI_API_KEY.startswith("sk-your_"):
    OPENAI_API_KEY = ""
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
if ANTHROPIC_API_KEY.startswith("sk-ant-your_"):
    ANTHROPIC_API_KEY = ""
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "deepseek").strip().lower()
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", DEEPSEEK_MODEL).strip()

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
SEARCH_PER_PAGE = int(os.getenv("SEARCH_PER_PAGE", "10"))
MAX_STRUCTURE_ITEMS = int(os.getenv("MAX_STRUCTURE_ITEMS", "160"))

LLM_PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek",
        "api_key": DEEPSEEK_API_KEY,
        "base_url": DEEPSEEK_API_BASE,
        "model": DEEPSEEK_MODEL,
        "models": ["deepseek-chat", "deepseek-coder"],
        "compatible": "openai",
    },
    "openai": {
        "label": "OpenAI",
        "api_key": OPENAI_API_KEY,
        "base_url": OPENAI_API_BASE,
        "model": OPENAI_MODEL,
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1-mini"],
        "compatible": "openai",
    },
    "anthropic": {
        "label": "Anthropic",
        "api_key": ANTHROPIC_API_KEY,
        "base_url": "https://api.anthropic.com/v1",
        "model": ANTHROPIC_MODEL,
        "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
        "compatible": "anthropic",
    },
}
