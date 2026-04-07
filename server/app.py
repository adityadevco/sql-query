import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from environment import SQLQueryEnv, SQLAction, TASKS

app = FastAPI(
    title="SQLQueryEnv",
    description="OpenEnv environment for SQL query correctness and optimization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_env = SQLQueryEnv()


class StepRequest(BaseModel):
    sql_query: str


class ResetRequest(BaseModel):
    task_id: str | None = None


@app.get("/")
async def root():
    return {
        "name": "SQLQueryEnv",
        "version": "1.0.0",
        "status": "running",
    }


@app.post("/reset")
async def reset(req: ResetRequest = ResetRequest()):
    result = await _env.reset(task_id=req.task_id)
    obs = result.observation
    return {
        "observation": obs.model_dump(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.post("/step")
async def step(req: StepRequest):
    action = SQLAction(sql_query=req.sql_query)
    result = await _env.step(action)
    obs = result.observation
    return {
        "observation": obs.model_dump(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.get("/state")
async def state():
    return await _env.state()


@app.get("/tasks")
async def list_tasks():
    return {
        "tasks": [
            {
                "task_id": tid,
                "name": t["name"],
                "difficulty": t["difficulty"],
                "max_steps": t["max_steps"],
            }
            for tid, t in TASKS.items()
        ]
    }


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
