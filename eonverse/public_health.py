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
        # No automatic hospital construction, research or prescribed health program.
        # Residents alter the environment through their own recorded experiments.
        state["sanitation"] = max(0, state["sanitation"] - 1)
        for patient in city_people:
            patient.hygiene = max(0, patient.hygiene - 2)
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
                if state.get("contact_reduction_until", 0) > world.tick:
                    risk = max(0, risk - 4)
                if (world.tick // 20 + source.id * 13 + target.id * 7) % 18 < risk:
                    target.infection = {"strain": source.infection["strain"], "severity": source.infection["severity"], "duration": 0}
                    state["outbreaks"] += 1
        state["medical_records"] = state["medical_records"][-30:]
