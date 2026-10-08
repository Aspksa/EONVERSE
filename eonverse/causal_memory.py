"""Conservative evidence bookkeeping for residents' intervention hypotheses.

Counterfactual baselines are estimates, not proof of causation.
"""
from math import sqrt

def record_evidence(state, hypothesis, observed, tick):
    target, control = hypothesis["target"], hypothesis["control"]
    key = control + ":" + target
    ledger = state.setdefault("causal_models", {})
    model = ledger.setdefault(key, {"trials":0, "sum_effect":0.0, "sum_squared":0.0,
                                    "mean_effect":0.0, "uncertainty":0.0, "confidence":0.0})
    baseline = hypothesis.get("baseline", 0)
    drift = hypothesis.get("control_trend", 0)
    # Relative to the estimated no-intervention change, not merely before-after.
    effect = round(observed - baseline - drift, 3)
    n = model["trials"] + 1
    model["trials"] = n
    model["sum_effect"] = round(model["sum_effect"] + effect, 5)
    model["sum_squared"] = round(model["sum_squared"] + effect * effect, 5)
    mean = model["sum_effect"] / n
    variance = max(0, model["sum_squared"] / n - mean * mean)
    model["mean_effect"] = round(mean, 4)
    model["uncertainty"] = round(sqrt(variance / n) if n>1 else abs(effect)+1, 4)
    # Low evidence or high dispersion means low confidence.
    model["confidence"] = round(min(.95, n/(n+4) * abs(mean)/(abs(mean)+model["uncertainty"]+1)), 4)
    hypothesis["estimated_effect"] = effect
    hypothesis["uncertainty"] = model["uncertainty"]
    hypothesis["confidence"] = model["confidence"]
    hypothesis["evaluated_at"] = tick
    return model

def choose_control(target, archives, controls, resident_id):
    """Balance exploration of untested pairs and promising but uncertain results."""
    candidates=[]
    for index, control in enumerate(controls):
        model=archives.get(control+":"+target)
        if not model:
            score=1000  # untested alternatives get an opportunity
        else:
            score=model["mean_effect"]+model["uncertainty"]*2+2/(1+model["trials"])
        candidates.append((score, -(index+resident_id)%len(controls), -index, control))
    return max(candidates)[-1]
