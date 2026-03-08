from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.agents import (
    detect_conversation_signal,
    detect_intent,
    generate_answer,
    recommend_action,
)
from app.memory import add_message, clear_messages, get_messages
from app.observability import request_logging_middleware, setup_logging
from app.retrieval import retrieve_context
from app.schemas import AgentRequest, AgentResponse
from app.settings import settings
from app.usecases import DEMO_SCENARIOS, USE_CASES

APP_START_TS = time.time()
WEB_ROOT = Path(__file__).resolve().parent / "web"


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging(settings.log_level)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-ready AI agent runtime with domain routing, retrieval context, session memory, "
        "and an interactive UI for realistic workflow demos."
    ),
    contact={"name": "AI Agent Runtime Team"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.middleware("http")(request_logging_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.app_env,
        "available_use_cases": list(USE_CASES.keys()),
        "docs_url": "/docs",
        "ui_url": "/ui",
    }


@app.get("/ui", response_class=FileResponse)
def web_ui() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/web/styles.css", response_class=FileResponse)
def web_styles() -> FileResponse:
    return FileResponse(WEB_ROOT / "styles.css", media_type="text/css")


@app.get("/web/app.js", response_class=FileResponse)
def web_script() -> FileResponse:
    return FileResponse(WEB_ROOT / "app.js", media_type="application/javascript")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - APP_START_TS),
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/use-cases")
def get_use_cases() -> dict:
    return {
        "summary": "Domain templates that can be used to build production AI workflows.",
        "count": len(USE_CASES),
        "use_cases": USE_CASES,
    }


@app.get("/demo-scenarios")
def get_demo_scenarios() -> dict:
    return {"scenarios": DEMO_SCENARIOS}


@app.get("/memory/{session_id}")
def memory(session_id: str) -> dict:
    return {"session_id": session_id, "messages": get_messages(session_id)}


@app.delete("/memory/{session_id}")
def delete_memory(session_id: str) -> dict:
    clear_messages(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest) -> AgentResponse:
    if request.use_case not in USE_CASES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported use_case '{request.use_case}'. Supported values: {', '.join(USE_CASES.keys())}",
        )

    start = time.perf_counter()

    add_message(request.session_id, request.message)
    memory_messages = get_messages(request.session_id)

    intent = detect_intent(request.message, request.use_case)
    conversation_signal = detect_conversation_signal(request.message)
    retrieved_context = retrieve_context(request.message, request.use_case) if request.use_retrieval else []
    recommended_action = recommend_action(intent, conversation_signal, request.use_case)

    answer = generate_answer(
        message=request.message,
        intent=intent,
        signal=conversation_signal,
        context=retrieved_context,
        action=recommended_action,
        use_case=request.use_case,
    )

    use_case_config = USE_CASES[request.use_case]

    trace = {
        "latency_ms": int((time.perf_counter() - start) * 1000),
        "retrieval_enabled": request.use_retrieval,
        "memory_count": len(memory_messages),
        "use_case_description": use_case_config["description"],
        "supported_intents": use_case_config["supported_intents"],
    }

    return AgentResponse(
        use_case=request.use_case,
        use_case_category=use_case_config["category"],
        intent=intent,
        conversation_signal=conversation_signal,
        recommended_action=recommended_action,
        retrieved_context=retrieved_context,
        answer=answer,
        memory=memory_messages,
        tool_candidates=use_case_config["tool_candidates"],
        trace=trace,
    )

