import os
from glob import glob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROMPT_CACHE = {}
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), 'prompts')

# Load all .prompty files at startup
for prompt_path in glob(os.path.join(PROMPTS_DIR, "*.prompty")):
    prompt_name = os.path.splitext(os.path.basename(prompt_path))[0]
    with open(prompt_path, "r", encoding="utf-8") as f:
        PROMPT_CACHE[prompt_name] = f.read()
        logger.info(f"Loaded prompt into cache for: {prompt_name} ")


def load_prompt(prompt_name: str) -> str:
    """Fetch prompt from in-memory cache."""
    if prompt_name not in PROMPT_CACHE:
        raise KeyError(f"Prompt '{prompt_name}' not found in cache.")
    return PROMPT_CACHE[prompt_name]
