"""Cloud integration never needs credentials to test offline behavior."""
import asyncio
from eonverse.world import World
from eonverse import cloud_ai


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("EONVERSE_AI_ENABLED", raising=False)
    monkeypatch.setenv("CLOUDRU_API_KEY", "dummy")
    monkeypatch.setenv("CLOUDRU_MODEL", "dummy")
    assert not cloud_ai.enabled()


def test_proposal_is_whitelisted():
    assert cloud_ai.validate_proposal({"focus": "grain", "reason": "Harvest nearby"}) is not None
    assert cloud_ai.validate_proposal({"focus": "delete_all", "reason": "no"}) is None
    assert cloud_ai.validate_proposal({"focus": "timber", "reason": ""}) is None
    assert cloud_ai.validate_proposal({"focus": "timber", "reason": "x" * 201}) is None


def test_advice_only_changes_bounded_memory(monkeypatch):
    world = World(42)
    monkeypatch.setattr(cloud_ai, "enabled", lambda: True)
    monkeypatch.setattr(cloud_ai, "request_proposal", lambda context:
                        {"focus": "grain", "reason": "shortage"})
    previous_food, previous_wood = world.food_supply, world.wood_supply
    old_deposits = [d["remaining"] for d in world.deposits]
    assert asyncio.run(cloud_ai.advise_once(world))
    assert world.food_supply == previous_food
    assert world.wood_supply == previous_wood
    assert [d["remaining"] for d in world.deposits] == old_deposits
    assert world.residents[0].memory["cloud_ai_last"]["focus"] == "grain"


def test_advice_failure_does_not_stop_simulation(monkeypatch):
    world = World(42)
    monkeypatch.setattr(cloud_ai, "enabled", lambda: True)
    def unavailable(context):
        raise OSError("offline")
    monkeypatch.setattr(cloud_ai, "request_proposal", unavailable)
    assert asyncio.run(cloud_ai.advise_once(world)) is False
    world.step()
    assert world.tick == 1
