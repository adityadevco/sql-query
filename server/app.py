import sys
import os

# 🔥 Fix imports (important after moving to server/)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from environment import SupportEnv
from models import Action

app = FastAPI()

env = SupportEnv()


# ROOT (health check)
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "OpenEnv SQL Environment is live"
    }


# RESET
@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()


# STEP
@app.post("/step")
def step(action: dict):
    action_obj = Action(**action)
    obs, reward, done, info = env.step(action_obj)

    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info,
    }


# STATE (required for OpenEnv validation)
@app.get("/state")
def state():
    return env.state()