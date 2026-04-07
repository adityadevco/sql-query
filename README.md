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

A real-world reinforcement learning environment simulating customer support decision-making workflows.

---

## 🚀 Overview

This environment models how AI agents handle customer queries by:

1. Understanding user intent  
2. Choosing the correct operational action  
3. Resolving issues effectively  

It reflects real-world systems used in:
- customer support automation  
- helpdesk ticket routing  
- AI assistants  

---

## 🧩 Problem Setting

Each episode consists of:

- A customer query  
- An agent decision  
- A reward signal  

The goal is to maximize correct decision-making.

---

## ⚙️ API (OpenEnv Spec)

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/reset` | Start new task |
| POST | `/step` | Take action |
| GET | `/state` | Get environment state |
| GET | `/` | Health check |

---

## 🧪 Tasks

We simulate increasing difficulty:

### 🟢 Easy
Customer clearly requests refund  
→ Expected: `refund`

### 🟡 Medium
Customer reports damaged product  
→ Expected: `escalate`

### 🔴 Hard
Customer gives vague complaint  
→ Expected: `resolve`

---

## 🧠 Observation Space

Each observation contains:

- user query  
- task difficulty  
- context  

---

## 🎯 Action Space

Agent must choose one:

- `refund`
- `escalate`
- `resolve`

---

## 🧮 Reward Design

Reward is shaped to reflect decision quality:

| Condition | Reward |
|----------|--------|
| Correct action | +0.7 |
| Completion bonus | +0.3 |
| Wrong action | -0.2 |

Final score ∈ [0, 1]

---

## 🤖 Agent Design

The baseline agent uses LLM reasoning:

- Reads observation  
- Decides optimal action  
- Maps output to structured action  

This simulates real AI decision pipelines.

---

## 🧠 Why This Environment Matters

This is NOT a toy environment.

It captures real-world complexity where:

- inputs are ambiguous  
- decisions have business impact  
- multi-step reasoning is required  

Such environments are critical for training production AI systems.

---

## 🐳 Run Locally

```bash
docker build -t sql-env .
docker run sql-env
