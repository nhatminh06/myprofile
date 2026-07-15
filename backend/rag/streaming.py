"""Streaming helpers for resume evaluation (Perplexity or offline stub)."""

import asyncio
import json
import os
from typing import AsyncIterator, Iterator, Optional

import requests

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


def _has_real_perplexity_key() -> bool:
    key = PERPLEXITY_API_KEY or ""
    return bool(key) and key not in {"your_perplexity_api_key_here", "changeme", "placeholder"}


def build_rate_prompt(company: str, resume: dict, qualifications: str) -> str:
    return (
        f"Rate this resume for a software engineering internship at {company}.\n"
        f"Return a percentage (e.g., 75%) followed by a brief explanation.\n\n"
        f"Qualifications:\n{qualifications}\n\nResume:\n{json.dumps(resume, indent=2)}"
    )


def build_advise_prompt(company: str, resume: dict, qualifications: str, rating: str) -> str:
    return (
        f"Provide actionable resume improvement advice for a software engineering internship at {company}.\n"
        f"Use markdown headings and bullet points.\n\n"
        f"Qualifications:\n{qualifications}\n\n"
        f"Current rating: {rating}\n\nResume:\n{json.dumps(resume, indent=2)}"
    )


def _stub_full_text(step_name: str, company: str) -> str:
    if step_name == "rate":
        return (
            f"75% chance of passing the CV screening round.\n\n"
            f"**Explanation:** [STUB — replace with Perplexity once API key is configured] "
            f"Your resume shows relevant skills for {company}, but could highlight more internship-ready projects."
        )
    return (
        "### 1. **Highlight cloud and DevOps experience**\n"
        "**Why:** The job posting emphasizes Kubernetes and CI/CD.\n"
        "**How to Improve:** Add one bullet quantifying deployment or automation work.\n\n"
        "### 2. **Strengthen AI/ML keywords**\n"
        "**Why:** The posting mentions LangChain and Python.\n"
        "**How to Improve:** Mention any ML coursework or side projects explicitly.\n\n"
        "[STUB — replace with Perplexity streaming once API key is configured]"
    )


def stream_perplexity(prompt: str) -> Iterator[str]:
    """Stream text chunks from Perplexity's SSE chat completions API."""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    data = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "search_mode": "academic",
        "web_search_options": {"search_context_size": "low"},
    }

    with requests.post(PERPLEXITY_API_URL, json=data, headers=headers, stream=True, timeout=120) as response:
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            payload = line.removeprefix("data: ").strip()
            if payload == "[DONE]":
                break
            try:
                parsed = json.loads(payload)
                delta = parsed["choices"][0]["delta"].get("content")
                if delta:
                    yield delta
            except (json.JSONDecodeError, KeyError, IndexError):
                continue


async def stream_stub_text(text: str, *, chunk_size: int = 12, delay_seconds: float = 0.04) -> AsyncIterator[str]:
    """Yield text in small chunks with artificial delay for offline SSE testing."""
    for start in range(0, len(text), chunk_size):
        yield text[start : start + chunk_size]
        await asyncio.sleep(delay_seconds)


async def stream_resume_step(
    step_name: str,
    *,
    company: str,
    resume: dict,
    qualifications: str = "",
    rating: str = "",
) -> AsyncIterator[str]:
    """Stream one resume evaluation step using Perplexity or the offline stub."""
    if step_name == "rate":
        prompt = build_rate_prompt(company, resume, qualifications)
        fallback = _stub_full_text("rate", company)
    else:
        prompt = build_advise_prompt(company, resume, qualifications, rating)
        fallback = _stub_full_text("advise", company)

    if _has_real_perplexity_key():
        try:
            for chunk in stream_perplexity(prompt):
                yield chunk
            return
        except Exception as exc:
            print(f"Perplexity streaming failed for {step_name}, falling back to stub:", exc)

    async for chunk in stream_stub_text(fallback):
        yield chunk
