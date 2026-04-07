def compute_reward(stage_score, done):
    reward = stage_score

    if done:
        reward += 0.3  # completion bonus

    return max(min(reward, 1.0), -1.0)