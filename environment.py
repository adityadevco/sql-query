from tasks import TASKS


class Observation:
    def __init__(self, query, difficulty, step):
        self.query = query
        self.difficulty = difficulty
        self.step = step

    def model_dump(self):
        return {
            "query": self.query,
            "difficulty": self.difficulty,
            "step": self.step,
        }


class SupportEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_step = 0
        self.done = False

    def reset(self):
        # rotate tasks for realism
        if self.current_task is None:
            self.current_task = self.tasks[0]
        else:
            idx = self.tasks.index(self.current_task)
            self.current_task = self.tasks[(idx + 1) % len(self.tasks)]

        self.current_step = 0
        self.done = False

        return Observation(
            query=self.current_task["query"],
            difficulty=self.current_task["difficulty"],
            step=self.current_step,
        )

    def step(self, action):
        if self.done:
            return self.reset(), 0.0, True, {}

        self.current_step += 1

        expected = self.current_task["expected"]

        reward = 0.0

        # ---- reward shaping ----
        if action == expected:
            reward += 0.6  # correct decision
            if self.current_step <= 2:
                reward += 0.2  # fast decision bonus
            reward += 0.2  # completion bonus
            self.done = True
        else:
            reward -= 0.2  # penalty for wrong action
            self.done = True

        obs = Observation(
            query=self.current_task["query"],
            difficulty=self.current_task["difficulty"],
            step=self.current_step,
        )

        return obs, reward, self.done, {}

    def state(self):
        return {
            "current_task": self.current_task,
            "step": self.current_step,
            "done": self.done,
        }
