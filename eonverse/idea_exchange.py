"""Local, bounded evidence exchange and collaborative hypothesis review.

Messages carry provenance and uncertainty; disagreement is not silently erased.
No pre-written discoveries, dialogue scripts or compulsory consensus.
"""
from math import hypot
from .civilization import territorial_owner

MAX_MESSAGES = 12
MAX_SHARED = 16

def proposition_key(control, target):
    return control + ":" + target

def offer_evidence(sender, recipient, key, model, tick):
    """Share observed claims when residents are close and trust each other."""
    if sender.id == recipient.id or sender.relationships.get(str(recipient.id), 0) < 55:
        return False
    if hypot(sender.x - recipient.x, sender.z - recipient.z) > 4:
        return False
    if not model.get("trials"):
        return False
    mailbox = recipient.memory.setdefault("heard_ideas", {})
    current = mailbox.get(key)
    incoming = {"source_id": sender.id, "effect": model["mean_effect"],
                "confidence": model.get("confidence", 0), "trials": model["trials"],
                "heard_at": tick}
    if current and current["heard_at"] == tick and current["source_id"] == sender.id:
        return False
    mailbox[key] = incoming
    if len(mailbox) > MAX_SHARED:
        oldest = min(mailbox, key=lambda k:(mailbox[k]["heard_at"], k))
        del mailbox[oldest]
    return True

def update_idea_exchange(world):
    if world.tick % 40:
        return
    people = sorted(world.residents, key=lambda p:p.id)
    state_by_id = {s["id"]:s for s in world.states if not s.get("dissolved")}
    for state in state_by_id.values():
        state.setdefault("knowledge_discussions", [])
        state.setdefault("collaborative_questions", [])
    # Exchange source-tagged evidence; avoid silently merging personal beliefs.
    for i, a in enumerate(people):
        for b in people[i+1:]:
            if hypot(a.x-b.x, a.z-b.z) > 4:
                continue
            for sender, recipient in ((a,b),(b,a)):
                state = state_by_id.get(territorial_owner(world,sender.x,sender.z))
                if state is None or territorial_owner(world,recipient.x,recipient.z) != state["id"]:
                    continue
                claims = state.get("causal_models", {})
                if not claims:
                    continue
                key = sorted(claims, key=lambda k:(-claims[k].get("confidence",0),k))[0]
                if not offer_evidence(sender,recipient,key,claims[key],world.tick):
                    continue
                recipient.memory["recent_exchange"] = {"from": sender.id, "claim":key}
                discussed=state["knowledge_discussions"]
                discussed.append({"tick":world.tick,"speaker_id":sender.id,
                                  "listener_id":recipient.id,"claim":key})
                del discussed[:-MAX_MESSAGES]
                personal = recipient.memory.get("last_causal_estimate")
                heard = recipient.memory["heard_ideas"][key]
                if personal is not None and personal * heard["effect"] < 0:
                    # Incompatible signs prompt a new question, not forced agreement.
                    question={"tick":world.tick,"raised_by":recipient.id,
                              "with":sender.id,"claim":key,"status":"unresolved"}
                    discussions=state["collaborative_questions"]
                    if question not in discussions:
                        discussions.append(question)
                        del discussions[:-MAX_MESSAGES]
