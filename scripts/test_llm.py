"""Check the LLM service generates grounded answers and fails gracefully."""

import logging
import os

from core.prompt_templates import format_context
from services.llm_service import FAILURE_MESSAGE, LLMService


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpx2", "httpcore", "google_genai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    chunks = [
        {
            "text": "Tokens are issued by the identity service and expire after 60 minutes.",
            "metadata": {"filename": "auth-api.md", "chunk_index": 0},
        },
        {
            "text": "Roll back immediately if error rates exceed 2% after a deploy.",
            "metadata": {"filename": "deploy-runbook.md", "chunk_index": 0},
        },
    ]
    context = format_context(chunks)

    service = LLMService()

    print("=== 1. answerable question ===")
    print(service.generate_response(context, "How long do auth tokens last?"))

    print("\n=== 2. not in the context ===")
    print(service.generate_response(context, "What is our holiday policy?"))

    print("\n=== 3. empty context ===")
    print(service.generate_response(format_context([]), "How do I deploy?"))

    print("\n=== 4. simulated API failure ===")
    os.environ["GEMINI_API_KEY"] = "invalid-key-for-testing"
    broken = LLMService()
    answer = broken.generate_response(context, "How long do auth tokens last?")
    print(answer)
    print(f"matched failure message: {answer == FAILURE_MESSAGE}")


if __name__ == "__main__":
    main()
