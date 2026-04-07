import asyncio
import sys
import os

sys.path.append(os.getcwd())

from environment import SupportEnv
from models import Action

BENCHMARK = "sql-query-env"
TASK_NAME = "sql-task"
MAX_STEPS = 3


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done):
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()}",
        flush=True,
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# 🔥 IMPROVED RULE-BASED AGENT
def get_action(observation):
    query = observation.query.lower()
    stage = observation.stage

    # --- classification ---
    if stage == "classification":
        if "charged" in query or "refund" in query:
            return Action(intent="refund")
        elif "not delivered" in query or "delivery" in query:
            return Action(intent="complaint")
        elif "payment" in query:
            return Action(intent="investigate")
        else:
            return Action(intent="investigate")

    # --- action ---
    elif stage == "action":
        if "refund" in query or "charged" in query:
            return Action(action="process_refund")
        else:
            return Action(action="escalate")

    # --- response ---
    elif stage == "response":
        if "refund" in query or "charged" in query:
            return Action(response="Your refund has been processed successfully.")
        elif "not delivered" in query or "delivery" in query:
            return Action(response="We are escalating your issue as high priority.")
        else:
            return Action(response="We are investigating and will resolve your issue soon.")

    # fallback (should never hit)
    return Action(
        intent="investigate",
        action="escalate",
        response="We are resolving your query.",
    )


async def main():
    env = SupportEnv()

    rewards = []
    steps_taken = 0

    log_start(TASK_NAME, BENCHMARK, "rule-based-agent")

    obs = env.reset()

    for step in range(1, MAX_STEPS + 1):
        action = get_action(obs)

        obs, reward, done, _ = env.step(action)

        rewards.append(reward)
        steps_taken = step

        log_step(step, action, reward, done)

        if done:
            break

    score = min(max(sum(rewards) / MAX_STEPS, 0), 1)
    success = score >= 0.5

    log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())