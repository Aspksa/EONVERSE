from eonverse.resource_catalog import MATERIAL_CATALOG, RAW_RESOURCES, PROCESSED_MATERIALS
from eonverse.world import World


def test_expanded_catalog_has_distinct_raw_and_processed_materials():
    assert len(MATERIAL_CATALOG) >= 250
    assert len(RAW_RESOURCES) >= 190
    assert len(PROCESSED_MATERIALS) >= 75
    assert not (set(RAW_RESOURCES) & set(PROCESSED_MATERIALS))
    assert set(RAW_RESOURCES) | set(PROCESSED_MATERIALS) == set(MATERIAL_CATALOG)
    assert all(item["value"] > 0 and item["unit"] == "abstract_unit"
               for item in MATERIAL_CATALOG.values())


def test_generated_deposits_are_real_raw_catalog_members():
    world = World(seed=99)
    assert len(world.deposits) >= 50
    assert len({d["kind"] for d in world.deposits}) > 50
    assert all(d["kind"] in RAW_RESOURCES for d in world.deposits)
    assert all(0 <= d["remaining"] <= d["capacity"] for d in world.deposits)
