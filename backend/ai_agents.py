import asyncio
import json
import os
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from pydantic import BaseModel

from rag.db import resume_to_snapshot, save_evaluation_history
from rag.retrieve import retrieve_relevant_chunks
from rag.streaming import stream_resume_step

load_dotenv(dotenv_path="backend/.env")

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

app = FastAPI()


class CompanyRequest(BaseModel):
    company: str


class ResumeRequest(BaseModel):
    company: str
    resume: Any


class ResumeEvalState(BaseModel):
    company: str
    resume: dict
    qualifications: str = ""
    rating: str = ""
    advice: str = ""


class StateSchema(BaseModel):
    company: str
    result: str = ""


def call_perplexity(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "search_mode": "academic",
        "web_search_options": {"search_context_size": "low"},
    }
    response = requests.post(PERPLEXITY_API_URL, json=data, headers=headers)
    if not response.ok:
        print("Perplexity API error:", response.status_code, response.text)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"].get("content", "")
    print("Perplexity content:", content)
    return content or ""


def fetch_company_qualifications(company: str) -> str:
    prompt = (
        f"List the typical job qualification requirements for a software engineer at {company}. "
        "Format the requirements as Markdown. For each section, start the header with an icon (e.g., 📝 **Education**), "
        "and list each requirement under it as a Markdown bullet (using -). Do NOT use plain text or paragraphs for the requirements—use only Markdown bullets for each item. "
        "Do NOT include any reference citations like [1], [2], etc. at the end of sentences or paragraphs."
    )
    return call_perplexity(prompt)


sources_graph = StateGraph(state_schema=StateSchema)


def sources_node(state):
    company = state.company
    prompt = (
        f"Provide the most important and basic factual information about the company: {company}. "
        "Include details such as headquarters location, founding year, founders, industry, number of employees, website, and a brief description. "
        "Format the response as clear, concise bullet points or short paragraphs. Do not include technology or jobs information here. "
        "Do NOT include any reference citations like [1], [2], etc. at the end of sentences or paragraphs."
    )
    return {"result": call_perplexity(prompt)}


sources_graph.add_node("sources", RunnableLambda(sources_node))
sources_graph.set_entry_point("sources")
sources_agent = sources_graph.compile()

info_graph = StateGraph(state_schema=StateSchema)


def info_node(state):
    company = state.company
    prompt = (
        f"Describe the technology stack, digital transformation initiatives, and job opportunities at {company}. "
        "Include information about major software, platforms, cloud services, and any notable tech projects or digital strategies. "
        "Also summarize the types of jobs and roles the company hires for, and any unique aspects of their work culture or hiring process. "
        "Structure the response into the following Markdown sections:\n\n"
        "## 🖥️ Technology Stack\n"
        "- List the main programming languages, frameworks, databases, tools, and platforms the company uses.\n"
        "- Mention any notable cloud service providers (e.g., AWS, Azure, GCP).\n"
        "- Highlight major digital transformation projects or tech innovations (AI, IoT, DevOps, etc.).\n\n"
        "## 💼 Job Opportunities\n"
        "- List the typical roles the company hires for (e.g., software engineer, data scientist, DevOps, etc.).\n"
        "- Mention common job functions or departments.\n"
        "- Note any unique aspects of their hiring process or candidate expectations (e.g., coding assessments, emphasis on culture fit).\n"
        "- Describe the work culture briefly if relevant.\n\n"
        "Use bullet points within each section where appropriate. Do not include unrelated company background—focus only on tech and hiring-related info. "
        "Do not summarize the company, just provide the information. "
        "Do NOT include any reference citations like [1], [2], etc. at the end of sentences or paragraphs."
    )
    return {"result": call_perplexity(prompt)}


info_graph.add_node("info", RunnableLambda(info_node))
info_graph.set_entry_point("info")
info_agent = info_graph.compile()

summary_graph = StateGraph(state_schema=StateSchema)


def summary_node(state):
    company = state.company
    prompt = (
        f"Write a concise summary (3–5 sentences) about {company}. "
        "The summary should:\n"
        "- Highlight what makes the company stand out in its industry (e.g., innovation, market leadership, unique value proposition).\n"
        "- Mention recent achievements, growth milestones, or major strategic shifts.\n"
        "- Include any notable partnerships, product innovations, or global expansions.\n"
        "- Conclude with key takeaways for someone researching the company (e.g., strengths, reputation, or direction).\n"
        "Write in a professional yet readable tone suitable for an investor or job candidate. "
        "Do NOT include any reference citations like [1], [2], etc. at the end of sentences or paragraphs."
    )
    return {"result": call_perplexity(prompt)}


summary_graph.add_node("summary", RunnableLambda(summary_node))
summary_graph.set_entry_point("summary")
summary_agent = summary_graph.compile()

resume_eval_graph = StateGraph(state_schema=ResumeEvalState)


def retrieve_node(state):
    qualifications = retrieve_relevant_chunks(state.company, top_k=3)
    if not qualifications.strip():
        qualifications = (
            f"No local qualification chunks were found for {state.company}. "
            "Ingest job posting files into backend/rag/documents and run backend/rag/ingest.py."
        )
    return {"qualifications": qualifications}


def _stub_resume_llm(step_name: str, state: ResumeEvalState) -> str:
    first_line = state.qualifications.splitlines()[0] if state.qualifications else ""
    print(
        f"STUB {step_name}: company={state.company}, qualifications_chars={len(state.qualifications)}, "
        f"first_line={first_line}"
    )
    if step_name == "rate":
        return "75%"
    return "stub response for testing"


def rate_node(state):
    return {"rating": _stub_resume_llm("rate", state)}


def advise_node(state):
    return {"advice": _stub_resume_llm("advise", state)}


resume_eval_graph.add_node("retrieve", RunnableLambda(retrieve_node))
resume_eval_graph.add_node("rate", RunnableLambda(rate_node))
resume_eval_graph.add_node("advise", RunnableLambda(advise_node))
resume_eval_graph.set_entry_point("retrieve")
resume_eval_graph.add_edge("retrieve", "rate")
resume_eval_graph.add_edge("rate", "advise")
resume_eval_agent = resume_eval_graph.compile()


def _sse_event(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


def _persist_evaluation_history(company: str, rating: str, resume: Any) -> None:
    try:
        save_evaluation_history(
            company=company,
            rating=rating,
            resume_snapshot=resume_to_snapshot(resume),
        )
    except Exception as exc:
        print("WARNING: failed to save resume evaluation history:", exc)


@app.post("/ai-company-sources")
async def ai_company_sources(req: CompanyRequest):
    if not req.company:
        raise HTTPException(status_code=400, detail="Company name is required")
    try:
        result = sources_agent.invoke({"company": req.company})
        print("Returning sources:", result["result"])
        return {"company": req.company, "sources": result["result"] or ""}
    except Exception as e:
        print("ERROR in /ai-company-sources:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai-company-info")
async def ai_company_info(req: CompanyRequest):
    if not req.company:
        raise HTTPException(status_code=400, detail="Company name is required")
    try:
        result = info_agent.invoke({"company": req.company})
        info_text = result["result"] or ""
        print("Returning info:", info_text)
        return {"company": req.company, "info": info_text}
    except Exception as e:
        print("ERROR in /ai-company-info:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai-company-summary")
async def ai_company_summary(req: CompanyRequest):
    if not req.company:
        raise HTTPException(status_code=400, detail="Company name is required")
    try:
        result = summary_agent.invoke({"company": req.company})
        print("Returning summary:", result["result"])
        return {"company": req.company, "summary": result["result"] or ""}
    except Exception as e:
        print("ERROR in /ai-company-summary:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai-resume-evaluate")
async def ai_resume_evaluate(req: ResumeRequest):
    if not req.company or req.resume in (None, "", {}, [], ()):
        raise HTTPException(status_code=400, detail="Company and resume are required")
    try:
        result = resume_eval_agent.invoke({"company": req.company, "resume": req.resume})
        _persist_evaluation_history(req.company, result.get("rating", ""), req.resume)
        return {
            "company": req.company,
            "qualifications": result.get("qualifications", ""),
            "rating": result.get("rating", ""),
            "advice": result.get("advice", ""),
        }
    except Exception as e:
        print("ERROR in /ai-resume-evaluate:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai-resume-evaluate/stream")
async def ai_resume_evaluate_stream(req: ResumeRequest):
    if not req.company or req.resume in (None, "", {}, [], ()):
        raise HTTPException(status_code=400, detail="Company and resume are required")

    async def event_generator():
        try:
            qualifications = retrieve_relevant_chunks(req.company, top_k=3)
            if not qualifications.strip():
                qualifications = (
                    f"No local qualification chunks were found for {req.company}. "
                    "Ingest job posting files into backend/rag/documents and run backend/rag/ingest.py."
                )

            yield _sse_event("qualifications", {"text": qualifications, "company": req.company})
            await asyncio.sleep(0)

            rating_parts: list[str] = []
            async for chunk in stream_resume_step(
                "rate",
                company=req.company,
                resume=req.resume,
                qualifications=qualifications,
            ):
                rating_parts.append(chunk)
                yield _sse_event("rating", {"chunk": chunk})

            rating = "".join(rating_parts)
            advice_parts: list[str] = []
            async for chunk in stream_resume_step(
                "advise",
                company=req.company,
                resume=req.resume,
                qualifications=qualifications,
                rating=rating,
            ):
                advice_parts.append(chunk)
                yield _sse_event("advice", {"chunk": chunk})

            _persist_evaluation_history(req.company, rating, req.resume)
            yield _sse_event(
                "done",
                {
                    "company": req.company,
                    "qualifications": qualifications,
                    "rating": rating,
                    "advice": "".join(advice_parts),
                },
            )
        except Exception as exc:
            print("ERROR in /ai-resume-evaluate/stream:", exc)
            yield _sse_event("error", {"detail": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# To run: uvicorn backend.ai_agents:app --reload --port 8000
