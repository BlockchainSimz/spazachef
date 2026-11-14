import random
from app import engine
B = dict(ingredients="rice, tinned tomatoes, one onion, chicken", serves=4, notes="no oven", diet="")
def test_respects_oven():
    for _ in range(30):
        r = engine.generate(B, "zanele", {}); assert r["archetype"] != "bake" and r["steps"]
def test_vegetarian_drops_meat():
    r = engine.generate({**B, "diet": "vegetarian"}, "farah", {}); assert not any("chicken" in i["item"] for i in r["ingredients"])
def test_learning_shifts_choice():
    w = {}
    for _ in range(40): engine.learn(w, "jabu", "pan", rating=5, cooked=True); engine.learn(w, "jabu", "grill", rating=1)
    picks = [engine.generate(B, "jabu", w, random.Random(i))["archetype"] for i in range(40)]
    assert picks.count("pan") > 25


def test_vegetarian_drops_fish_and_meat():
    brief = {**B, "ingredients": "rice, spinach, pilchards, onion", "diet": "vegetarian"}
    r = engine.generate(brief, "zanele", {})
    assert not any(x["item"] == "pilchards" for x in r["ingredients"])


def test_vegan_drops_meat_eggs_and_dairy():
    brief = {**B, "ingredients": "rice, spinach, chicken, eggs, cheese, onion", "diet": "vegan"}
    r = engine.generate(brief, "zanele", {})
    names = {x["item"] for x in r["ingredients"]}
    assert not names.intersection({"chicken", "eggs", "cheese"})


def test_vegetarian_excludes_all_common_seafood():
    brief = {
        **B,
        "ingredients": "rice, spinach, prawns, shrimp, salmon, hake, sardines, onion",
        "diet": "vegetarian",
    }
    r = engine.generate(brief, "zanele", {})
    names = {x["item"] for x in r["ingredients"]}
    assert not names.intersection({"prawns", "shrimp", "salmon", "hake", "sardines"})


def test_pescatarian_excludes_meat_but_keeps_fish():
    brief = {
        **B,
        "ingredients": "rice, spinach, chicken, salmon, onion",
        "diet": "pescatarian",
    }
    r = engine.generate(brief, "zanele", {})
    names = {x["item"] for x in r["ingredients"]}
    assert "chicken" not in names
    assert "salmon" in names


def test_vegan_excludes_honey_and_animal_ingredients_but_keeps_oat_milk():
    brief = {
        **B,
        "ingredients": "rice, spinach, chicken, eggs, cheese, honey, oat milk, onion",
        "diet": "vegan",
    }
    r = engine.generate(brief, "zanele", {})
    names = {x["item"] for x in r["ingredients"]}
    assert not names.intersection({"chicken", "eggs", "cheese", "honey"})
    assert "oat milk" in names


def test_unsupported_diet_is_rejected():
    import pytest
    with pytest.raises(ValueError, match="Unsupported dietary preference"):
        engine.generate({**B, "diet": "gluten-free"}, "zanele", {})
