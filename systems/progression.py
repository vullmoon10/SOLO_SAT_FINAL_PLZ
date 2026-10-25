def add_score(current_score, earned_score):
    """획득 점수를 누적한다."""
    return current_score + max(0, earned_score)
