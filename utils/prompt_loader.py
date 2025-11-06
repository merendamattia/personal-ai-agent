import logging
import os

logger = logging.getLogger(__name__)


def load_prompt(filename):
    """Load prompt file content from the prompts/ folder"""
    # Get the project root directory (parent of utils)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(project_root, "prompts", filename)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    logger.info(f"Loaded prompt: {filename}")
    return content
