def apply_damage(current_hp, damage, no_damage=False):
    """피해를 적용하고 체력이 0 미만으로 내려가지 않게 한다."""
    if no_damage:
        return max(0, current_hp)
    return max(0, current_hp - max(0, damage))
