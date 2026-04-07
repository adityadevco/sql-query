def get_tasks():
    return [
        {
            "id": "easy_refund",
            "query": "I was charged twice for my order",
            "expected_flow": {
                "intent": "refund",
                "action": "process_refund",
                "keywords": ["refund", "processed"]
            }
        },
        {
            "id": "medium_delivery_issue",
            "query": "My order hasn’t arrived yet and support is not responding",
            "expected_flow": {
                "intent": "complaint",
                "action": "escalate",
                "keywords": ["escalate", "issue", "priority"]
            }
        },
        {
            "id": "hard_payment_confusion",
            "query": "Payment failed but money got deducted and I received a confirmation SMS",
            "expected_flow": {
                "intent": "investigate",
                "action": "escalate",
                "keywords": ["investigate", "resolve", "check"]
            }
        }
    ]