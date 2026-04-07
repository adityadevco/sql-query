import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from environment import SQLQueryEnv, SQLAction, TASKS

app = FastAPI()

_env = SQLQueryEnv()


class StepRequest(BaseModel):
    sql_query: str


class ResetRequest(BaseModel):
    task_id: str | None = None


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    result = _env.reset(task_id=req.task_id)
    obs = result.observation
    return {
        "observation": obs.model_dump(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.post("/step")
def step(req: StepRequest):
    action = SQLAction(sql_query=req.sql_query)
    result = _env.step(action)
    obs = result.observation
    return {
        "observation": obs.model_dump(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.get("/state")
def state():
    return _env.state()


@app.get("/tasks")
def tasks():
    return {"tasks": list(TASKS.keys())}


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
