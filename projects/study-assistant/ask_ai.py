"""Week 3 Day 1: call the configured Responses endpoint."""
import sys
import re
from pathlib import Path

import httpx
from dotenv import dotenv_values


def main():
    settings = dotenv_values(Path(__file__).with_name(".env"))
    missing = [k for k in ("AI_BASE_URL", "AI_API_KEY", "AI_MODEL") if not settings.get(k)]
    if missing:
        print("Missing .env settings: " + ", ".join(missing))
        return 1

    question = " ".join(sys.argv[1:]) or "Say hello in one short sentence."
    try:
        # Use a direct HTTPS connection; keep TLS certificate verification enabled.
        with httpx.Client(trust_env=False, timeout=45.0) as client:
            response = client.post(
                settings["AI_BASE_URL"].rstrip("/") + "/responses",
                headers={"Authorization": "Bearer " + settings["AI_API_KEY"]},
                json={"model": settings["AI_MODEL"], "input": question, "max_output_tokens": 256},
            )
        if not response.is_success:
            message = response.text.replace(settings["AI_API_KEY"], "[REDACTED]")
            message = re.sub(r"(?i)Bearer\s+\S+|sk-[A-Za-z0-9_-]+", "[REDACTED]", message)
            print("API HTTP status:", response.status_code)
            print("Provider message:", message[:1200])
            return 1

        data = response.json()
        answer = "\n".join(
            part["text"]
            for item in data.get("output", [])
            if item.get("type") == "message"
            for part in item.get("content", [])
            if part.get("type") == "output_text" and isinstance(part.get("text"), str)
        )
        if not answer:
            print("No text returned. Response status:", data.get("status"))
            return 1
        print(answer)
        return 0
    except httpx.RequestError:
        print("API connection failed or timed out. Check network and base URL.")
        return 1
    except (ValueError, TypeError, KeyError, AttributeError):
        print("Provider returned an unexpected response format.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
