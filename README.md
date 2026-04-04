---
title: Sql Query Env
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# 🧠 SQLQueryEnv — OpenEnv Round 1 Submission

> **Real-world SQL environment where AI agents must write correct, efficient queries to answer business questions.**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-green)](https://openenv.dev)
[![HF Space](https://img.shields.io/badge/🤗-HuggingFace%20Space-blue)](https://huggingface.co/spaces)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://python.org)

---

## 🎯 What Is This?

SQLQueryEnv is a reinforcement learning environment where an AI agent receives:
- A **database schema** (SQLite DDL)
- Seeded **sample data**
- A **business question** in plain English

The agent must write a **correct, efficient SQL query** to answer the question. It receives graded rewards based on correctness, efficiency, and code style — with partial credit for partially correct answers.

This simulates a real task that data analysts, backend engineers, and business intelligence teams do every day.

---

## 🗂️ Environment Architecture

```
┌─────────────────────────────────────────┐
│              AI Agent                   │
│  (writes SQL based on schema + question)│
└────────────────┬────────────────────────┘
                 │ SQLAction(sql_query=...)
                 ▼
┌─────────────────────────────────────────┐
│           SQLQueryEnv                   │
│  ┌─────────────────────────────────┐    │
│  │ In-memory SQLite DB             │    │
│  │  - Execute query                │    │
│  │  - Compare vs expected output   │    │
│  │  - Grade: correctness+efficiency│    │
│  └─────────────────────────────────┘    │
│  Returns: SQLObservation + reward       │
└─────────────────────────────────────────┘
```

---

## 📋 Tasks

### Task 1 — Easy: Sales Summary Report
**Difficulty:** Easy | **Max Steps:** 5

The agent must aggregate revenue by product category for completed orders.

```
Expected output:
category     | total_revenue
-------------|-------------
Electronics  | 7075.0
Furniture    | 1650.0
```

**Skills tested:** `SELECT`, `JOIN`, `WHERE`, `GROUP BY`, `ORDER BY`, `SUM()`

---

### Task 2 — Medium: Customer Cohort Analysis
**Difficulty:** Medium | **Max Steps:** 7

Find customers who ordered in 2+ distinct months. Return their name, region, tier, order count, distinct months active, and total spend.

**Skills tested:** `GROUP BY`, `HAVING`, `strftime()` for date extraction, multi-table `JOIN`, `COUNT(DISTINCT ...)`

---

### Task 3 — Hard: Churn Risk Classification
**Difficulty:** Hard | **Max Steps:** 10

For each customer, compute total orders, total spend, average order value, months since last order, and classify churn risk as `High / Medium / Low` using business rules.

**Skills tested:** `CASE WHEN`, `julianday()` date arithmetic, `CAST()`, complex aggregation, custom `ORDER BY` with CASE expressions

---

## 🎮 Action & Observation Spaces

### Action Space
```json
{
  "sql_query": "SELECT category, SUM(quantity * unit_price) AS total_revenue FROM orders ..."
}
```

### Observation Space
```json
{
  "task_id": "easy_sales_summary",
  "task_name": "Sales Summary Report",
  "difficulty": "easy",
  "schema_ddl": "CREATE TABLE orders (...); ...",
  "sample_data": "-- Sample rows in orders: ...",
  "business_question": "What is total revenue per category?",
  "hint": "Revenue = quantity * unit_price. Filter by status = 'completed'.",
  "previous_error": null,
  "previous_sql": null,
  "step_number": 0,
  "max_steps": 5
}
```

---

## 🏆 Reward Function

Rewards are continuous (0.0 – 1.0) with partial credit:

| Component | Weight | Description |
|-----------|--------|-------------|
| Correctness | 70% | Column names + row values match expected output |
| Efficiency | 20% | Appropriate SQL constructs for difficulty (GROUP BY on medium/hard, CASE on hard) |
| Style | 10% | Avoids `SELECT *`, uses semicolons |

**Partial rewards are meaningful:**
- Wrong number of rows but some correct → partial credit
- Right rows, wrong sort order → 0.85 correctness
- SQL error → 0.05 (not zero, to avoid reward cliffs)

Episode ends when `score >= 0.95` (success) or max steps reached.

---

## 🚀 Setup & Usage

### Run Locally

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/sql-query-env
cd sql-query-env
pip install -r requirements.txt
python app.py
# Server starts at http://localhost:7860
```

### Docker

```bash
docker build -t sql-query-env .
docker run -p 7860:7860 sql-query-env
```

### API Endpoints

```bash
# Reset to a task
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy_sales_summary"}'

# Submit a SQL query
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"sql_query": "SELECT category, SUM(quantity * unit_price) AS total_revenue FROM orders JOIN products USING(product_id) WHERE status = '\''completed'\'' GROUP BY category ORDER BY total_revenue DESC;"}'

# List all tasks
curl http://localhost:7860/tasks
```

### Run Inference

```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1/"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="hf_your_token_here"
export SPACE_URL="https://your-space.hf.space"

python inference.py
```

---

## 📊 Baseline Scores

Evaluated using `meta-llama/Llama-3.1-8B-Instruct` via HF Inference API:

| Task | Difficulty | Score |
|------|-----------|-------|
| Sales Summary Report | Easy | 0.95 |
| Customer Cohort Analysis | Medium | 0.78 |
| Churn Risk Classification | Hard | 0.61 |
| **Overall Average** | | **0.78** |

---

## 📁 Project Structure

```
sql-query-env/
├── app.py          # FastAPI server (OpenEnv HTTP interface)
├── env.py          # SQLQueryEnv core logic, graders, tasks
├── inference.py    # Baseline agent script (required)
├── openenv.py      # OpenEnv base classes stub
├── openenv.yaml    # Environment metadata
├── Dockerfile      # Container definition
├── requirements.txt
└── README.md
```

---

## 💡 Why SQL?

SQL query writing is one of the most common real-world tasks for knowledge workers. Bad SQL causes:
- Slow dashboards
- Incorrect business reports
- Costly cloud compute bills

An agent that reliably writes correct, efficient SQL has **immediate production value**. This environment gives a grounded, deterministic, reproducible benchmark for measuring that capability.

---

## 🛡️ Disqualification Checklist

- ✅ HF Space deploys and responds to `/reset`
- ✅ `openenv.yaml` present and valid
- ✅ `Dockerfile` builds and runs
- ✅ `inference.py` in root, uses OpenAI client, structured logs
- ✅ 3+ tasks with graders returning 0.0–1.0
- ✅ Graders are deterministic (SQLite in-memory, fixed seed data)
- ✅ No plagiarism — original environment and tasks

---

*Built for OpenEnv Hackathon Round 1 — Scaler × Hugging Face*
