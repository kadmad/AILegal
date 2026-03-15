"""
Summary Generation Service — OpenAI client.

Wraps the OpenAI Chat Completions API to produce concise summaries of
AI Document Analysis and medical documents extracted by the OCR service.

The system prompt instructs the model to act as a domain-aware summariser,
which improves output quality for the specialised document types handled by
this platform.
"""

import os
from openai import OpenAI

# Module-level OpenAI client — instantiated once and reused across calls.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_text(text: str) -> str:
    """
    Send ``text`` to OpenAI and return a concise summary.

    Uses the ``gpt-3.5-turbo`` chat model with a domain-specific system
    prompt that primes the model for AI Document Analysis and medical document summarisation.

    Args:
        text: The raw OCR-extracted text to summarise.

    Returns:
        str: The model's summary with leading/trailing whitespace stripped.
    """
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            # System prompt: establish the model's role as an AI Document Analysis/medical summariser
            {"role": "system", "content": "You are a helpful assistant that summarizes AI Document Analysis and medical documents."},
            {"role": "user", "content": f"Summarize the following content:\n{text}"}
        ]
    )
    return chat_response.choices[0].message.content.strip()