import os
from openai import OpenAI
from environment import SupportEnv

client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"]
)

model = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

env = SupportEnv()

print("[START] task=sql-task env=sql-query-env model=reasoning-agent")

obs = env.reset()

total_reward = 0
rewards = []

for step in range(1, 4):
    prompt = f"""
You are an intelligent customer support agent.

Current observation:
{obs}

Choose the best next action from:
refund, escalate, resolve

Respond with only one word.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10
    )

    action_text = response.choices[0].message.content.lower().strip()

    if "refund" in action_text:
        action = "refund"
    elif "escalate" in action_text:
        action = "escalate"
    else:
        action = "resolve"

    obs, reward, done, info = env.step(action)

    total_reward += reward
    rewards.append(reward)

    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()}")

    if done:
        break

score = total_reward / len(rewards)

print(f"[END] success={str(done).lower()} steps={step} score={score:.2f} rewards={','.join([f'{r:.2f}' for r in rewards])}")
