from eonverse.causal_memory import record_evidence, choose_control
from eonverse.world import World
from eonverse.persistence import save_world, load_world


def test_multiple_trials_accumulate_and_confidence_is_bounded():
    state={}
    hypothesis={"target":"health","control":"sanitation","baseline":50,"control_trend":2}
    first=record_evidence(state,hypothesis,60,40)
    assert first["trials"]==1
    assert hypothesis["estimated_effect"]==8
    record_evidence(state,hypothesis,62,80)
    assert state["causal_models"]["sanitation:health"]["trials"]==2
    assert 0<=state["causal_models"]["sanitation:health"]["confidence"]<=.95


def test_untried_control_remains_available():
    ledger={"sanitation:health":{"trials":5,"mean_effect":4,"uncertainty":1}}
    assert choose_control("health",ledger,("sanitation","research"),1)=="research"


def test_world_learning_persists_after_restart(tmp_path):
    world=World(42)
    for _ in range(120):world.step()
    path=tmp_path/"causal.json"
    save_world(world,path)
    loaded=load_world(path)
    assert loaded.snapshot()==world.snapshot()
    for _ in range(80):
        loaded.step()
        world.step()
    assert loaded.snapshot()==world.snapshot()
