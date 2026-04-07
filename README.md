---
title: SQL Query Environment
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
tags:
  - openenv
---

# 🧠 SQL Query Environment (OpenEnv)

A real-world reinforcement learning environment for training AI agents to handle structured query resolution tasks such as refunds, complaints, and investigations.

Built using the OpenEnv framework with full API compliance.

---

## 🚀 Overview

This environment simulates a multi-step workflow where an AI agent must:

1. Classify user intent  
2. Decide the correct system action  
3. Generate a response  

This mirrors real-world systems like:
- customer support automation  
- ticket resolution pipelines  
- query handling systems  

---

## ⚙️ OpenEnv API Endpoints

The environment exposes the required OpenEnv endpoints:

| Method | Endpoint | Description |
|------|--------|-------------|
| POST | `/reset` | Initialize environment |
| POST | `/step` | Perform an action |
| GET  | `/state` | Get current state |
| GET  | `/` | Health check |

---

## 🧩 Environment Design

### Observation

Each observation includes:

- `query` → user input  
- `stage` → current phase (`classification`, `action`, `response`)  
- `history` → previous steps  

---

### Action Space

Agent outputs structured actions:

- `intent` → refund / complaint / investigate  
- `action` → process_refund / escalate  
- `response` → final message  

---

## 🧪 Tasks

Three difficulty levels:

| Level | Description |
|------|------------|
| Easy | Clear refund request |
| Medium | Delivery complaint |
| Hard | Ambiguous issue requiring investigation |

---

## 🧮 Reward System

Rewards are assigned per step:

- Intent correctness → **+0.4**  
- Action correctness → **+0.3**  
- Response quality → **+0.7**  

Final score normalized between **0.0 – 1.0**

---

## 🤖 Baseline Agent

Provided in `inference.py`:

- Rule-based logic  
- Deterministic outputs  
- No external API dependency  
- Fully reproducible  

---

## 🐳 Running Locally

```bash
docker build -t sql-env .
docker run sql-env