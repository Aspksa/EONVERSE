"""Constructed, maintained and depreciating transport assets."""
from .transport import route_status

def update_infrastructure(world):
    if world.tick % 50:
        return
    active = sorted((s for s in world.states if not s.get("dissolved")), key=lambda s:s["id"])
    for i,a in enumerate(active):
        for b in active[i+1:]:
            key=(a["id"],b["id"])
            route=route_status(world,a,b)
            if route is None:
                continue
            asset=world.infrastructure.get(key)
            if asset is None:
                # Construction requires both states to contribute funds.
                kind=route["mode"]
                price={"road":16,"pass":34,"bridge":42,"sea":50}[kind]
                if a.get("treasury",0)<price/2 or b.get("treasury",0)<price/2:
                    continue
                a["treasury"]=round(a["treasury"]-price/2,2)
                b["treasury"]=round(b["treasury"]-price/2,2)
                world.infrastructure[key]={"kind":kind,"condition":100,"spent":price,
                                             "bridges":1 if kind=="bridge" else 0,
                                             "ports":2 if kind=="sea" else 0}
                world.history.append(f"Day {world.tick}: {kind} link constructed between {a['name']} and {b['name']}")
                continue
            asset["condition"]=max(0,asset["condition"]-3)
            if asset["condition"]<=65 and not route["blocked"]:
                repair=round((100-asset["condition"])*0.2,2)
                if a.get("treasury",0)>=repair/2 and b.get("treasury",0)>=repair/2:
                    a["treasury"]=round(a["treasury"]-repair/2,2)
                    b["treasury"]=round(b["treasury"]-repair/2,2)
                    asset["spent"]=round(asset["spent"]+repair,2)
                    asset["condition"]=min(100,asset["condition"]+30)
                    world.history.append(f"Day {world.tick}: maintained {asset['kind']} link")
