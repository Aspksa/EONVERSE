"""Bounded transferable learning from resident planning successes and failures."""
def update_strategy_memory(state, resident, target, control, observed_change, blocked=False):
    memory=resident.memory.setdefault("strategy_experience",{})
    key=control+":"+target
    row=memory.setdefault(key,{"attempts":0,"failures":0,"mean_gain":0.0})
    count=row["attempts"]
    row["attempts"]=count+1
    row["failures"]+=int(blocked or observed_change < -2)
    row["mean_gain"]=round((row["mean_gain"]*count+observed_change)/(count+1),3)
    # Transfer the control's failure tendency across different needs, but not
    # as certainty: a new objective must still be explored on its own.
    overall=resident.memory.setdefault("control_experience",{})
    stat=overall.setdefault(control,{"attempts":0,"failures":0})
    stat["attempts"]+=1
    stat["failures"]+=int(blocked or observed_change < -2)
    return row

def penalty(resident,target,control):
    personal=resident.memory.get("strategy_experience",{}).get(control+":"+target,{})
    general=resident.memory.get("control_experience",{}).get(control,{})
    local_rate=personal.get("failures",0)/max(1,personal.get("attempts",0))
    general_rate=general.get("failures",0)/max(1,general.get("attempts",0))
    return local_rate*5 + general_rate*2

def alternative_controls(resident,target,ranked_controls):
    """Prefer evidence-informed alternatives without banning exploration."""
    return sorted(ranked_controls,key=lambda c:(penalty(resident,target,c),ranked_controls.index(c)))
