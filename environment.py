import sys
import os
sys.path.append(os.getcwd())

from models import Observation, Action
from tasks import get_tasks
from grader import grade_step
from rewards import compute_reward
import random


class SupportEnv:

    def __init__(self):
        self.tasks = get_tasks()
        self.current_task = None
        self.stage = None
        self.history = []
        self.step_count = 0
        self.max_steps = 3

    def reset(self):
        self.current_task = random.choice(self.tasks)
        self.stage = "classification"
        self.history = []
        self.step_count = 0

        return Observation(
            query=self.current_task["query"],
            stage=self.stage,
            history=[]
        )

    def step(self, action):
        expected = self.current_task["expected_flow"]

        stage_score = grade_step(self.stage, action, expected)

        self.history.append(str(action))
        self.step_count += 1

        done = False

        if self.stage == "classification":
            self.stage = "action"
        elif self.stage == "action":
            self.stage = "response"
        else:
            done = True

        if self.step_count >= self.max_steps:
            done = True

        reward = compute_reward(stage_score, done)

        return self.state(), reward, done, {}

    def state(self):
        return Observation(
            query=self.current_task["query"],
            stage=self.stage,
            history=self.history
        )