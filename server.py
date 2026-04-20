"""FastAPI server + static frontend for the workshop agent.

You don't need to modify this file. It wraps `agent.py` in an HTTP endpoint so
attendees can interact via the browser instead of the CLI. Your changes to
`agent.py`, `tools/`, and `eval.py` are what make the agent smarter.

Run:
    uv run python server.py
Then open http://localhost:8000
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pydantic_ai.messages import ToolCallPart, ToolReturnPart

from agent import MODEL, agent

load_dotenv()

app = FastAPI(title="navi-workshop")

FRONTEND_DIR = Path(__file__).parent / "frontend"


class ChatRequest(BaseModel):
    prompt: str


class ToolCallRecord(BaseModel):
    name: str
    args: dict[str, Any] | str
    result: Any | None = None


class ChatResponse(BaseModel):
    output: str
    tool_calls: list[ToolCallRecord]
    model: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="empty prompt")

    try:
        result = await agent.run(req.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}") from e

    # Stitch tool calls and their returns from the message trace.
    calls: dict[str, ToolCallRecord] = {}
    for msg in result.all_messages():
        for part in getattr(msg, "parts", []):
            if isinstance(part, ToolCallPart):
                args = part.args
                # pydantic-ai may expose args as a dict or a JSON string
                calls[part.tool_call_id] = ToolCallRecord(
                    name=part.tool_name,
                    args=args if isinstance(args, (dict, str)) else str(args),
                )
            elif isinstance(part, ToolReturnPart):
                rec = calls.get(part.tool_call_id)
                if rec is not None:
                    rec.result = part.content

    return ChatResponse(
        output=result.output,
        tool_calls=list(calls.values()),
        model=MODEL,
    )


@app.get("/api/config")
async def config() -> dict[str, Any]:
    """Small config surface the frontend uses to show model + Logfire link."""
    logfire_token = os.getenv("LOGFIRE_TOKEN", "")
    return {
        "model": MODEL,
        "logfire_enabled": bool(logfire_token),
    }


# Static frontend. Everything under / is served from frontend/.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
