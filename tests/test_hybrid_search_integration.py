import json

import pytest

from app.vectordb import PlantVectorDB


@pytest.fixture(scope="module")
def db() -> PlantVectorDB:
    db = PlantVectorDB()

    # Keep tests deterministic by recreating the plants collection.
    try:
        db.client.delete_collection("plants")
    except Exception:
        pass

    db.collection = db.client.get_or_create_collection(name="plants")
    db.load_plants_from_json("./data/plants.json")
    return db


@pytest.mark.integration
def test_8_hours_maps_to_full_sun(db: PlantVectorDB) -> None:
    filters = db._extract_filters_from_query("What grows well with 8 hours of sun?")
    assert filters.get("sun_requirement") == "full sun"


@pytest.mark.integration
def test_full_sun_low_water_prefers_basil(db: PlantVectorDB) -> None:
    results = db.query_plants("I want full sun plants that need little water", n_results=3)
    ids = results.get("ids", [[]])[0]
    assert "basil" in ids


@pytest.mark.integration
def test_cool_season_returns_non_empty(db: PlantVectorDB) -> None:
    results = db.query_plants("Show me cool season crops", n_results=3)
    ids = results.get("ids", [[]])[0]
    assert len(ids) > 0
