"""
openenv.py — Minimal OpenEnv base classes.
The real openenv-core package provides these; this stub ensures
local development works without the package installed.
"""
from pydantic import BaseModel
from typing import Any, Optional


class StepResult(BaseModel):
    observation: Any
    reward: float
    done: bool
    info: dict = {}


class Environment:
    """Base class for OpenEnv environments."""

    async def reset(self, **kwargs) -> StepResult:
        raise NotImplementedError

    async def step(self, action) -> StepResult:
        raise NotImplementedError

    async def state(self) -> dict:
        raise NotImplementedError
