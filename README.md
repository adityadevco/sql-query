# 🧠 SQL Query Environment (OpenEnv)

A real-world reinforcement learning environment for training AI agents to understand and respond to structured query tasks, inspired by customer support and data query workflows.

Built using the OpenEnv framework for standardized agent evaluation.

---

## 🚀 Overview

This environment simulates a multi-step decision-making process where an AI agent must:

1. Classify the user query (intent detection)
2. Decide the correct action
3. Generate an appropriate response

The goal is to model how intelligent systems handle real-world query resolution tasks such as refunds, complaints, and investigations.

---

## 🎯 Why This Matters

Modern AI systems are increasingly used in:

- Customer support automation  
- Query resolution systems  
- Data-driven decision workflows  

This environment provides a **controlled benchmark** to evaluate how well agents can reason through structured, multi-step tasks.

---

## 🧩 Environment Design

### Observation Space

Each observation includes:

- `query` — user input text  
- `stage` — current stage of task (`classification`, `action`, `response`)  
- `history` — previous steps  

---

### Action Space

Agent outputs structured actions:

- `intent` → classification (refund / complaint / investigate)  
- `action` → system action (process_refund / escalate)  
- `response` → final user-facing message  

---

## 🧪 Tasks

The environment includes multiple tasks with increasing difficulty:

| Difficulty | Description |
|----------|------------|
| Easy | Clear refund request |
| Medium | Delivery complaint |
| Hard | Ambiguous investigation case |

Each task requires correct reasoning across all 3 stages.

---

## 🧮 Reward System

Reward is assigned at each step:

- **Intent correctness** → +0.4  
- **Action correctness** → +0.3  
- **Response quality** → +0.7  

Final score is normalized between **0.0 – 1.0**

Partial rewards ensure learning signal throughout the episode.

---

## ⚙️ OpenEnv Compliance

This environment fully implements:

- `reset()` → initializes environment  
- `step(action)` → returns `(observation, reward, done, info)`  
- `state()` → returns current state  

Includes:

- Typed models (Pydantic)  
- `openenv.yaml` configuration  
- Deterministic graders  

---

## 🤖 Baseline Agent

A rule-based agent is included in `inference.py`.

Features:

- Deterministic outputs  
- No external API dependency  
- Reproducible scoring  

---

## 🐳 Running Locally

```bash
docker build -t sql-env .
docker run sql-env