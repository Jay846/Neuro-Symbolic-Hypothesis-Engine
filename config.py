import os

# API Keys & URLs loaded from environment variables
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "rc_33ac9a53b845eeb21d5542378f2cd956c473b30169977600fccfa3a980c2b6bd")
FEATHERLESS_API_URL = os.getenv("FEATHERLESS_API_URL", "https://api.featherless.ai/v1")

WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID", "7RR3LRAYLR")
WOLFRAM_API_URL = "http://api.wolframalpha.com/v1/result" # or Cloud API URL

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "fc-edd3db0c3f3849d099eca9ddc77248e8")

# Default LLM Model on Featherless
# They offer models like Qwen 2.5 Coder, DeepSeek R1/V3, Llama 3
DEFAULT_MODEL = os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct")
