"""
inference.py — SQLQueryEnv Baseline Inference Script
Follows OpenEnv structured logging format exactly: [START], [STEP], [END].

Environment variables required:
  API_BASE_URL  — LLM API endpoint
  MODEL_NAME    — model identifier
  HF_TOKEN      — Hugging Face / API key (used as api_key)

Optional:
  LOCAL_IMAGE_NAME — Docker image name (if using from_docker_image())
"""

import asyncio
import json
import os
import sys
import time
from typing import List

import httpx
from openai import OpenAI

# ─────────────────────────────────────────────
# Config from environment variables
# ─────────────────────────────────────────────

API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1/")
MODEL_NAME: str = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN: str = os.getenv("HF_TOKEN", "")
LOCAL_IMAGE_NAME: str = os.getenv("LOCAL_IMAGE_NAME", "")

# Space URL — update after deploying to HF Spaces
SPACE_URL = os.getenv("SPACE_URL", "http://localhost:7860")

BENCHMARK = "sql-query-env"
MAX_STEPS = 7
SUCCESS_SCORE_THRESHOLD = 0.8
MAX_TOTAL_REWARD = 1.0  # We use average, so max per task = 1.0


# ─────────────────────────────────────────────
# Structured Logging (required format)
# ─────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(json.dumps({
        "type": "START",
        "task": task,
        "env": env,
        "model": model,
        "timestamp": time.time(),
    }), flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error=None) -> None:
    print(json.dumps({
        "type": "STEP",
        "step": step,
        "action": action,
        "reward": reward,
        "done": done,
        "error": error,
        "timestamp": time.time(),
    }), flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    print(json.dumps({
        "type": "END",
        "success": success,
        "steps": steps,
        "score": score,
        "rewards": rewards,
        "timestamp": time.time(),
    }), flush=True)


# ─────────────────────────────────────────────
# LLM Agent
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert SQL analyst. You will be given:
1. A database schema (CREATE TABLE statements)
2. A business question to answer with SQL

Your job: Write a single, correct SQL query that answers the question.

Rules:
- Use SQLite syntax
- Always end your query with a semicolon
- Return ONLY the SQL query — no explanation, no markdown, no backticks
- Use explicit column aliases that match the expected output columns
- Always use WHERE status = 'completed' when filtering order status unless told otherwise
- For date math, use julianday() in SQLite

If you made an error before, fix it based on the feedback provided.
"""


def get_model_sql(
    client: OpenAI,
    observation: dict,
    history: List[str],
) -> str:
    schema = observation.get("schema_ddl", "")
    question = observation.get("business_question", "")
    hint = observation.get("hint", "")
    prev_error = observation.get("previous_error", "")
    prev_sql = observation.get("previous_sql", "")
    difficulty = observation.get("difficulty", "")
    step = observation.get("step_number", 0)

    user_content = f"""Database Schema:
{schema}

Business Question:
{question}

Difficulty: {difficulty}
"""
    if hint:
        user_content += f"\nHint: {hint}"
    if prev_sql:
        user_content += f"\n\nYour previous SQL attempt:\n{prev_sql}"
    if prev_error:
        user_content += f"\n\nError/Feedback: {prev_error}\nPlease fix the query."
    if history:
        user_content += f"\n\nHistory of attempts:\n" + "\n".join(history[-3:])

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            max_tokens=512,
            temperature=0.1,
        )
        sql = response.choices[0].message.content.strip()
        # Clean any accidental markdown
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return sql
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "SELECT 1;"


# ─────────────────────────────────────────────
# Environment Client (HTTP)
# ─────────────────────────────────────────────

class EnvClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def reset(self, task_id: str = None) -> dict:
        payload = {"task_id": task_id} if task_id else {}
        r = httpx.post(f"{self.base_url}/reset", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def step(self, sql_query: str) -> dict:
        r = httpx.post(f"{self.base_url}/step", json={"sql_query": sql_query}, timeout=30)
        r.raise_for_status()
        return r.json()

    def tasks(self) -> list:
        r = httpx.get(f"{self.base_url}/tasks", timeout=30)
        r.raise_for_status()
        return r.json()["tasks"]


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def run_task(client: OpenAI, env: EnvClient, task_id: str, task_name: str) -> float:
    """Run a single task and return final score."""
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = env.reset(task_id=task_id)
        observation = result["observation"]

        for step in range(1, MAX_STEPS + 1):
            if result.get("done", False):
                break

            sql = get_model_sql(client, observation, history)
            result = env.step(sql)

            observation = result["observation"]
            reward = float(result.get("reward", 0.0))
            done = result.get("done", False)
            info = result.get("info", {})
            error = info.get("feedback") if reward < 0.5 else None

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=sql, reward=reward, done=done, error=error)
            history.append(f"Step {step}: reward={reward:.3f} | feedback={info.get('feedback','')}")

            if done:
                break

        score = max(rewards) if rewards else 0.0  # Best attempt score
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] Task error: {e}", flush=True)
        error = str(e)
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy")
    env = EnvClient(SPACE_URL)

    print(f"[DEBUG] Connecting to env at {SPACE_URL}", flush=True)
    print(f"[DEBUG] Using model: {MODEL_NAME}", flush=True)

    try:
        tasks = env.tasks()
    except Exception as e:
        print(f"[DEBUG] Failed to connect to env: {e}", flush=True)
        sys.exit(1)

    all_scores = []
    for task in tasks:
        print(f"\n[DEBUG] Running task: {task['task_id']} ({task['difficulty']})", flush=True)
        score = run_task(client, env, task["task_id"], task["name"])
        all_scores.append(score)
        print(f"[DEBUG] Task score: {score:.3f}", flush=True)

    overall = sum(all_scores) / len(all_scores) if all_scores else 0.0
    print(f"\n[DEBUG] Overall score across {len(all_scores)} tasks: {overall:.3f}", flush=True)


if __name__ == "__main__":
    main()
