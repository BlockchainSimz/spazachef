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
