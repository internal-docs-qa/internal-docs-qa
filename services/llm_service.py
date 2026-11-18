"""Generate answers from an LLM, grounded in retrieved context."""

import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from core.prompt_templates import SYSTEM_PROMPT, USER_TEMPLATE

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash-lite"
TIMEOUT_SECONDS = 30
FAILURE_MESSAGE = "The answer service is temporarily unavailable. Please try again shortly."


class LLMService:
    """Wraps a Gemini client and turns prompts into answers."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment")

        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, context: str, question: str) -> str:
        """Ask the model to answer the question using only the context."""
        user_message = USER_TEMPLATE.format(context=context, question=question)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.0,
                    http_options=types.HttpOptions(timeout=TIMEOUT_SECONDS * 1000),
                ),
            )
        except Exception:
            logger.exception("LLM call failed")
            return FAILURE_MESSAGE

        text = response.text
        if not text:
            logger.warning("LLM returned an empty response")
            return FAILURE_MESSAGE

        return text.strip()
