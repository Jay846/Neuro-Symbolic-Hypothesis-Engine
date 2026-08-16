import os

# API Keys & URLs loaded from environment variables (Never hardcode credentials here)
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "")
FEATHERLESS_API_URL = os.getenv("FEATHERLESS_API_URL", "https://api.featherless.ai/v1")

WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID", "")
WOLFRAM_API_URL = "http://api.wolframalpha.com/v1/result" # or Cloud API URL

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

# Default LLM Model on Featherless
DEFAULT_MODEL = os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct")
