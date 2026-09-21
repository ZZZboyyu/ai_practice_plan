from pathlib import Path

import httpx
from dotenv import dotenv_values


SETTINGS = dotenv_values(Path(__file__).with_name(".env"))


def ask_ai(question: str) -> str:
    with httpx.Client(trust_env=False, timeout=45.0) as client:
        response = client.post(
            SETTINGS["AI_BASE_URL"].rstrip("/") + "/responses",
            headers={"Authorization": "Bearer " + SETTINGS["AI_API_KEY"]},
            json={
                "model": SETTINGS["AI_MODEL"],
                "input": question,
                "max_output_tokens": 256,
            },
        )
    response.raise_for_status()
    data = response.json()
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                return part["text"]
    raise ValueError("AI 未返回文本")
