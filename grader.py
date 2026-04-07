def grade_step(stage, action, expected):
    score = 0.0

    if stage == "classification":
        if action.intent == expected["intent"]:
            score += 0.4

    elif stage == "action":
        if action.action == expected["action"]:
            score += 0.3

    elif stage == "response":
        if action.response:
            response = action.response.lower()
            if any(k in response for k in expected["keywords"]):
                score += 0.4

    return score