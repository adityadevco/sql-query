import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
import uvicorn

from environment import SupportEnv

app = FastAPI()

_env = SupportEnv()


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/reset")
def reset(req: dict = {}):
    obs = _env.reset()
    return {
        "observation": obs.model_dump() if hasattr(obs, "model_dump") else obs,
        "reward": 0.0,
        "done": False,
        "info": {},
    }


@app.post("/step")
def step(action: dict):
    act = action.get("action") or action.get("sql_query") or action

    obs, reward, done, info = _env.step(act)

    return {
        "observation": obs.model_dump() if hasattr(obs, "model_dump") else obs,
        "reward": float(reward),
        "done": bool(done),
        "info": info if isinstance(info, dict) else {},
    }


@app.get("/state")
def state():
    return _env.state()


@app.get("/tasks")
def tasks():
    if hasattr(_env, "tasks"):
        return {"tasks": _env.tasks}
    return {"tasks": []}


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
