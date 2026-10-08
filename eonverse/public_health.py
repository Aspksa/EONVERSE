"""Abstract fictional epidemics, sanitation, hospitals, physicians and herb breeding.

Variants are gameplay counters, NOT biological sequences or clinical models.
"""
from math import hypot
from .civilization import territorial_owner

def update_public_health(world):
    if world.tick % 20:
        return
    active = {s["id"]: s for s in world.states if not s.get("dissolved")}
    people = sorted(world.residents, key=lambda p: p.id)
    for state in active.values():
        state.setdefault("sanitation", 50)
        state.setdefault("hospital", False)
        state.setdefault("outbreaks", 0)
        state.setdefault("medical_research", 0)
        state.setdefault("herb_cultivation", 0)
        state.setdefault("medical_records", [])
        city_people = [p for p in people if territorial_owner(world, p.x, p.z) == state["id"]]
        if not city_people:
            continue
        # Policy, investment and maintenance determine sanitation.
        upkeep = 3
        if state.get("treasury", 0) >= upkeep:
            state["treasury"] = round(state["treasury"] - upkeep, 2)
            improvement = 5 if state.get("law") in ("conservation", "mutual_aid") else 3
            state["sanitation"] = min(100, state["sanitation"] + improvement)
        else:
            state["sanitation"] = max(0, state["sanitation"] - 5)
        if not state["hospital"] and "school" in state.get("institutions", []) and state.get("treasury", 0) >= 35:
            state["treasury"] = round(state["treasury"] - 35, 2)
            state["hospital"] = True
            world.history.append(f"Day {world.tick}: hospital founded in {state['name']}")
        if state["hospital"] and "laboratory" in state.get("institutions", []) and state.get("treasury", 0) >= 4:
            state["treasury"] = round(state["treasury"] - 4, 2)
            state["medical_research"] = min(10, state["medical_research"] + .2)
        if "laboratory" in state.get("institutions", []) and state.get("medicinal_inventory", 0) >= 2 and state.get("treasury", 0) >= 3:
            state["medicinal_inventory"] -= 2
            state["treasury"] = round(state["treasury"] - 3, 2)
            state["herb_cultivation"] = min(5, state["herb_cultivation"] + .1)
        for patient in city_people:
            patient.hygiene = max(0, patient.hygiene - 2)
            if state["sanitation"] >= 60 and state.get("treasury", 0) >= 1:
                patient.hygiene = min(100, patient.hygiene + 5)
            # Low hygiene can seed a fictional illness by a deterministic event.
            if not patient.infection and patient.hygiene < 35 and (world.tick // 20 + patient.id) % 9 == 0:
                patient.infection = {"strain": 0, "severity": 1, "duration": 0}
                state["outbreaks"] += 1
            if patient.infection:
                patient.infection["duration"] += 1
                patient.health = max(0, patient.health - patient.infection["severity"] * 2)
                # Mutation is an abstract severity change, not genetics.
                if patient.infection["duration"] % 5 == 0:
                    patient.infection["strain"] = min(8, patient.infection["strain"] + 1)
                    patient.infection["severity"] = min(3, patient.infection["severity"] + 1)
                doctors = [p for p in city_people if p.knowledge.get("medicine", 0) >= .5]
                if state["hospital"] and doctors and state.get("medicinal_inventory", 0) >= 1:
                    state["medicinal_inventory"] -= 1
                    doctor = max(doctors, key=lambda p: (p.knowledge["medicine"], -p.id))
                    doctor.knowledge["medicine"] = round(min(10, doctor.knowledge["medicine"] + .1), 3)
                    patient.health = min(100, patient.health + 10 + state["medical_research"])
                    patient.infection = None
                    state["medical_records"].append({"tick": world.tick, "patient_id": patient.id, "result": "treated"})
                elif patient.infection["duration"] >= 8:
                    patient.infection = None
                    state["medical_records"].append({"tick": world.tick, "patient_id": patient.id, "result": "recovered"})
        # Proximity-only transmission, with sanitation and hygiene modifying risk.
        contagious = [p for p in city_people if p.infection]
        for source in contagious:
            for target in city_people:
                if target.id == source.id or target.infection or hypot(target.x-source.x, target.z-source.z) > 2:
                    continue
                risk = max(1, (100 - state["sanitation"]) // 15 + (100 - target.hygiene) // 20)
                if (world.tick // 20 + source.id * 13 + target.id * 7) % 18 < risk:
                    target.infection = {"strain": source.infection["strain"], "severity": source.infection["severity"], "duration": 0}
                    state["outbreaks"] += 1
        state["medical_records"] = state["medical_records"][-30:]
