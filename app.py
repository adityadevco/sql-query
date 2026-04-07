from fastapi import FastAPI
from environment import SupportEnv
from models import Action

app = FastAPI()

env = SupportEnv()


@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()


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


@app.get("/")
def root():
    return {"status": "running", "message": "OpenEnv SQL Environment is live"}