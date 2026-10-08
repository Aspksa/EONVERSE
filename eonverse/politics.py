"""Simple deterministic political institutions for emerging settlements.

Rule-based politics: ruler selection, succession and periodic policies.
"""
GOVERNMENTS = ("council", "monarchy", "republic")


def update_politics(world):
    residents = {r.id: r for r in world.residents}
    for state in world.states:
        if "government" not in state:
            state["government"] = GOVERNMENTS[(state["id"] - 1) % len(GOVERNMENTS)]
            state["ruler_id"] = None
            state["law"] = "balanced"
            state["elections_at"] = world.tick + 100
        incumbent = residents.get(state.get("ruler_id"))
        candidates = [r for r in world.residents if r.age >= 16]
        if not candidates:
            state["ruler_id"] = None
            continue
        vacancy = incumbent is None
        election = (state["government"] in ("republic", "council")
                    and world.tick >= state["elections_at"])
        if vacancy or election:
            # Prioritize older adults for council, wealth for republic,
            # and family succession for monarchy.
            if state["government"] == "monarchy" and incumbent is None:
                royal_family = state.get("dynasty_id")
                pool = [r for r in candidates if r.family_id == royal_family]
                winner = max(pool or candidates, key=lambda r: (r.age, -r.id))
                state["dynasty_id"] = winner.family_id
            elif state["government"] == "republic":
                winner = max(candidates, key=lambda r: (r.coins, -r.id))
            else:
                winner = max(candidates, key=lambda r: (r.age, -r.id))
            old = state.get("ruler_id")
            state["ruler_id"] = winner.id
            state["elections_at"] = world.tick + 100
            if old != winner.id:
                world.history.append(
                    f"Day {world.tick}: {state['name']} appointed ruler #{winner.id}"
                )
        # Policy selection influences future diplomacy and tax reforms.
        if world.tick % 100 == 0:
            state["law"] = ("conservation" if world.food_supply < 90
                            else "development" if world.wood_supply > 90
                            else "balanced")
