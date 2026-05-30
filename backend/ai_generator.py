from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv


def _get_model():
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import Model

    load_dotenv()
    api_key = os.getenv("WATSONX_API_KEY")
    url = os.getenv("WATSONX_URL")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-chat-v2")

    if not api_key or not url or not project_id:
        raise ValueError("Missing WATSONX_API_KEY, WATSONX_URL, or WATSONX_PROJECT_ID")

    credentials = Credentials(url=url, api_key=api_key)
    return Model(model_id=model_id, credentials=credentials, project_id=project_id)


def _extract_text(response) -> str:
    if isinstance(response, dict):
        results = response.get("results")
        if isinstance(results, list) and results:
            return results[0].get("generated_text", "").strip()
        return response.get("generated_text", "").strip()
    if isinstance(response, list) and response:
        return str(response[0])
    return str(response)


def generate_recap(prompt: str) -> str:
    """Generate a race recap using IBM watsonx.ai."""
    try:
        model = _get_model()
        params = {
            "decoding_method": "sample",
            "max_new_tokens": 300,
            "temperature": 0.4,
            "top_p": 0.9,
            "repetition_penalty": 1.05,
        }
        response = model.generate(prompt=prompt, params=params)
        recap = _extract_text(response)
        if not recap:
            return "The model returned an empty response. Try adjusting the prompt."
        return recap
    except Exception as exc:  # noqa: BLE001
        return f"AI generation failed: {exc}"
