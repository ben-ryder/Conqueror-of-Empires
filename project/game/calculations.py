# Ben-Ryder 2019
# Currently a direct subtraction of attack from health


def apply_attack(attacker, defender):
    defender.health -= attacker.attack

    if (abs(attacker.position[0] - defender.position[0]) <= defender.reach and
            abs(attacker.position[1] - defender.position[1]) <= defender.reach):  # defender is in reach to retaliate.
        attacker.health -= defender.defence

    return [unit for unit in [attacker, defender] if unit.health <= 0]
