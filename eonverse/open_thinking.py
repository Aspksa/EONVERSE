"""Bounded, deterministic, resident-originated hypothesis generation.

Composes observed dimensions and generic controllable world variables rather
than prescribing an institutional or medical solution. Not an unrestricted LLM.
"""
from .civilization import territorial_owner

OBSERVABLES=("health","hygiene","food","energy")
CONTROLS=("sanitation","contact_reduction","supplies","research")
COST={"sanitation":3,"contact_reduction":1,"supplies":2,"research":4}
MAX_HYPOTHESES=24

def observe(world, state):
    people=[p for p in world.residents if territorial_owner(world,p.x,p.z)==state["id"]]
    if not people:return {}
    return {dimension:round(sum(getattr(p,dimension) for p in people)/len(people),3)
            for dimension in OBSERVABLES}

def generate_hypothesis(person, observations, archive):
    """A question about a measurable variable and an intervention."""
    if not observations:return None
    # Select a locally unsatisfactory observation; preference differs by person.
    priority=sorted(observations,key=lambda k:(observations[k],OBSERVABLES.index(k)))
    target=priority[0]
    # Compose variable pairs; experience guides selection but never supplies an answer.
    attempts={(v.get("target"),v.get("control")) for v in archive}
    candidates=[(target,control) for control in CONTROLS]
    candidates.sort(key=lambda pair:(pair in attempts,
         (CONTROLS.index(pair[1])+person.id)%len(CONTROLS)))
    target,control=candidates[0]
    return {"target":target,"control":control,"question":
            "Does changing %s improve %s?"%(control,target),
            "proposer_id":person.id,"status":"proposed"}

def apply_probe(world,state,people,control):
    cost=COST[control]
    if state.get("treasury",0)<cost:return False
    state["treasury"]=round(state["treasury"]-cost,2)
    if control=="sanitation":
        state["sanitation"]=min(100,state.get("sanitation",50)+5)
        for p in people:p.hygiene=min(100,p.hygiene+3)
    elif control=="contact_reduction":
        state["contact_reduction_until"]=world.tick+80
    elif control=="supplies":
        if not state.get("medicinal_inventory",0):
            state["treasury"]=round(state["treasury"]+cost,2)
            return False
        state["medicinal_inventory"]-=1
        patient=min(people,key=lambda p:(p.health,p.id))
        patient.health=min(100,patient.health+5)
    else:
        state["research_observations"]=state.get("research_observations",0)+1
    return True

def update_open_thinking(world):
    if world.tick%40:return
    for state in sorted((s for s in world.states if not s.get("dissolved")),key=lambda s:s["id"]):
        people=sorted((p for p in world.residents if territorial_owner(world,p.x,p.z)==state["id"]),key=lambda p:p.id)
        adults=[p for p in people if p.age>=16]
        if not adults:continue
        data=observe(world,state)
        history=state.setdefault("hypotheses",[])
        pending=state.pop("pending_hypothesis",None)
        if pending:
            end=data.get(pending["target"],0)
            gain=round(end-pending["baseline"],3)
            pending.update({"result":gain,"status":"tested","tested_at":world.tick})
            history.append(pending)
            del history[:-MAX_HYPOTHESES]
            for p in people:
                if p.id==pending["proposer_id"]:
                    p.memory["last_hypothesis_result"]=gain
                    p.knowledge["research"]=round(min(10,p.knowledge.get("research",0)+.1),3)
                    break
        # Each agent retains an independent question; most curiosity wins a test budget.
        ideas=[]
        for p in adults:
            question=generate_hypothesis(p,data,history)
            if question:
                p.memory["current_question"]=question["question"]
                ideas.append((p.personality.get("curiosity",.5),-p.id,question))
        if not ideas:continue
        idea=max(ideas)[2]
        if apply_probe(world,state,people,idea["control"]):
            idea.update({"baseline":data[idea["target"]],"created_at":world.tick,"status":"testing"})
            state["pending_hypothesis"]=idea
            world.history.append(f"Day {world.tick}: resident #{idea['proposer_id']} began testing a question")
