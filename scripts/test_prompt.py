"""Check the prompt template assembles correctly."""

from core.prompt_templates import build_prompt, format_context


def main() -> None:
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
    prompt = build_prompt(context, "How long do auth tokens last?")

    print(prompt)
    print(f"\n--- {len(prompt)} characters ---")

    print("\n--- empty context ---")
    print(build_prompt(format_context([]), "What is the deployment process?"))


if __name__ == "__main__":
    main()