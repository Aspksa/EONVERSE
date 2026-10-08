"""Evidence-guided resident plans across many simulation ticks.

Plans are composed from generic world affordances, not civilization milestones.
"""
from .civilization import territorial_owner
from .open_thinking import observe, CONTROLS, COST, apply_probe
from .causal_memory import choose_control
from .strategy_learning import update_strategy_memory, alternative_controls

MAX_STEPS=3
MAX_PLAN_RECORDS=16

def propose_plan(world, state, person, measurements):
    """Combine available actions into a finite, budgeted and revisable plan."""
    if not measurements:
        return None
    target=min(measurements, key=lambda k:(measurements[k],k))
    models=state.get("causal_models",{})
    ranked=[]
    for control in CONTROLS:
        model=models.get(control+":"+target,{})
        confidence=model.get("confidence",0)
        effect=model.get("mean_effect",0)
        uncertainty=model.get("uncertainty",3)
        value=effect*confidence + uncertainty*(1-confidence)*.15 - COST[control]*.2
        ranked.append((value,-CONTROLS.index(control),control))
    ranked.sort(reverse=True)
    first=choose_control(target,models,CONTROLS,person.id)
    controls=alternative_controls(person,target,[first]+[item[2] for item in ranked if item[2]!=first])
    funds=state.get("treasury",0)
    steps=[]
    for control in controls:
        if len(steps)>=MAX_STEPS:break
        if COST[control]>funds:continue
        steps.append({"control":control,"status":"pending","cost":COST[control]})
        funds-=COST[control]
    if not steps:return None
    return {"owner_id":person.id,"target":target,"baseline":measurements[target],
            "steps":steps,"cursor":0,"created_at":world.tick,
            "status":"active","failures":0,"last_observation":measurements[target],
            "supporters":[]}

def update_planning(world):
    if world.tick%40:return
    for state in sorted((s for s in world.states if not s.get("dissolved")),key=lambda s:s["id"]):
        people=sorted([p for p in world.residents if territorial_owner(world,p.x,p.z)==state["id"]],
                      key=lambda p:p.id)
        adults=[p for p in people if p.age>=16]
        if not adults:continue
        measurements=observe(world,state)
        if not measurements:continue
        plan=state.get("collective_plan")
        owner=next((p for p in adults if plan and p.id==plan.get("owner_id")),None)
        if plan and plan["status"]=="active" and owner is None:
            plan["status"]="abandoned"
        if plan and plan["status"]=="active" and owner:
            pending=plan.pop("awaiting_result",None)
            if pending:
                change=round(measurements[plan["target"]]-pending["before"],3)
                step=plan["steps"][pending["index"]]
                step["observed_change"]=change
                step["status"]="evaluated"
                update_strategy_memory(state,owner,plan["target"],step["control"],change)
                plan["last_observation"]=measurements[plan["target"]]
                if change < -2:
                    plan["failures"]+=1
                if plan["failures"]>=2:
                    plan["status"]="revised"
                    owner.memory["plan_outcome"]="revised"
                elif plan["cursor"]>=len(plan["steps"]):
                    plan["status"]="completed"
                    owner.memory["plan_outcome"]="completed"
            if plan["status"]=="active" and "awaiting_result" not in plan:
                if plan["cursor"]<len(plan["steps"]):
                    step=plan["steps"][plan["cursor"]]
                    if apply_probe(world,state,people,step["control"]):
                        step["status"]="testing"
                        plan["awaiting_result"]={"index":plan["cursor"],
                            "before":measurements[plan["target"]]}
                        plan["cursor"]+=1
                    else:
                        plan["failures"]+=1
                        step["status"]="blocked"
                        update_strategy_memory(state,owner,plan["target"],step["control"],-3,blocked=True)
                        if plan["failures"]>=2:plan["status"]="revised"
                else:
                    plan["status"]="completed"
        if plan and plan["status"]=="active":
            continue
        if plan:
            state.setdefault("plan_history",[]).append(plan)
            state["plan_history"]=state["plan_history"][-MAX_PLAN_RECORDS:]
        planner=max(adults,key=lambda p:(p.personality.get("ambition",0)+p.knowledge.get("research",0)/10,-p.id))
        new_plan=propose_plan(world,state,planner,measurements)
        if new_plan:
            new_plan["supporters"]=[p.id for p in adults if p.id!=planner.id
                and p.relationships.get(str(planner.id),0)>=60][:6]
            state["collective_plan"]=new_plan
            planner.memory["long_term_plan"]=new_plan["target"]
            world.history.append(f"Day {world.tick}: citizen #{planner.id} formed a multi-step plan")
