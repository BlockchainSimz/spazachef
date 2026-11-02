"""Self-contained recipe engine. No LLM or external API: knowledge base + constraint
composer + Thompson-sampling meta-learner that improves from user feedback."""
import random, re, uuid

ROLES = [
 ("protein", "chicken beef mince lamb pork fish pilchards pilchard tuna egg eggs boerewors sausage tofu".split()),
 ("legume", "beans lentils chickpeas samp".split()),
 ("starch", "rice pap maize potato potatoes pasta noodles bread couscous".split()),
 ("spice", "curry masala turmeric cumin coriander paprika cinnamon".split()),
 ("dairy", "milk cheese butter yoghurt yogurt cream amasi".split()),
 ("aromatic", "garlic ginger chilli chili onion onions".split()),
 ("veg", "tomato tomatoes tinned carrot cabbage spinach morogo pepper peppers butternut pumpkin squash beetroot cauliflower broccoli peas mushrooms".split()),
]
MEAT = set("chicken beef mince lamb pork fish pilchards pilchard tuna boerewors sausage".split())

PERSONAS = {
 "zanele": dict(name="Auntie Zanele", tag="Comfort food, big flavour", heat=1, spice="a pinch of curry powder",
   likes={"pot": .4, "rice": .2}, intro="Sit down, my dear. We are going to stretch this pantry properly."),
 "jabu": dict(name="Braai Boss Jabu", tag="Fire, smoke, and confidence", heat=2, spice="braai spice",
   likes={"grill": .5, "pan": .3}, intro="Right, fire first. Everything tastes better with a little char."),
 "farah": dict(name="Chef Farah", tag="Spice with a story", heat=2, spice="turmeric, cumin and a stick of cinnamon",
   likes={"pot": .3, "rice": .4}, intro="Bloom the spices slowly. That is where the story starts."),
 "raj": dict(name="Raj from next door", tag="Clever swaps, no fuss", heat=1, spice="whatever spice you have",
   likes={"pan": .4, "soup": .2}, intro="No fuss. Missing something? Swap it and carry on."),
}

ARCH = {
 "pot": dict(title="Slow pot of {main}", oven=False, mins=45, fire=False, steps=[
   "Heat oil in a heavy pot and soften {a} for 5 minutes.", "Stir in {sp} for 1 minute until fragrant.",
   "Add {p}, {l} and {v} with 400 ml water.", "Cover and simmer gently for 30 minutes, topping up water if it catches.",
   "Season, rest 5 minutes, and serve with {s}."]),
 "pan": dict(title="Hot-pan {main}", oven=False, mins=20, fire=False, steps=[
   "Cook {s} as the packet says and keep warm.", "Heat oil in a wide pan until shimmering, then brown {p} for 5 minutes.",
   "Add {a}, {v} and {sp}; toss on high heat for 6 minutes.", "Splash in water, scrape the pan, season and serve over {s}."]),
 "rice": dict(title="One-pan {main} rice", oven=False, mins=35, fire=False, steps=[
   "Fry {a} and {sp} in oil for 3 minutes.", "Add {p} and {v}, stir 4 minutes.",
   "Stir in {s} and twice its volume of water.", "Cover on low heat for 18 minutes, rest 5 minutes, fluff and serve."]),
 "soup": dict(title="Cosy {main} soup", oven=False, mins=30, fire=False, steps=[
   "Soften {a} in oil for 4 minutes.", "Add {v}, {l}, {p} and {sp} with 800 ml water.",
   "Simmer 20 minutes, blend half if you like it thick.", "Season well and serve with {s}."]),
 "grill": dict(title="Char-grilled {main}", oven=False, mins=30, fire=True, steps=[
   "Rub {p} and {v} with oil, {sp} and salt.", "Grill over hot coals or a griddle pan, turning often, until charred.",
   "Warm {s} on the edge of the fire.", "Rest 5 minutes and serve with {a}."]),
 "bake": dict(title="Tray-baked {main}", oven=True, mins=50, fire=False, steps=[
   "Heat the oven to 200 C.", "Toss {p}, {v}, {a} and {sp} with oil on a tray.",
   "Roast 35 to 40 minutes, turning once.", "Serve with {s}."]),
}

def parse(text):
    return [t.strip().lower() for t in re.split(r"[,\n;]+", text or "") if t.strip()][:40]

def role(item):
    words = set(re.findall(r"[a-z\-]+", item))
    for r, ws in ROLES:
        if words & set(ws): return r
    return "other"

def feasible(a, roles, notes):
    if ARCH[a]["oven"] and "no oven" in notes: return False
    if ARCH[a]["fire"] and ("no fire" in notes or "no braai" in notes): return False
    has = lambda *r: any(x in roles for x in r)
    return {"pot": has("aromatic", "veg") and has("protein", "legume", "veg"), "pan": has("protein", "veg"),
            "rice": has("starch"), "soup": has("veg", "legume"), "grill": has("protein", "veg"),
            "bake": has("protein", "veg", "starch")}[a]

def join(xs, fb):
    if not xs: return fb
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]

def generate(brief, persona_id, weights, rng=random):
    p = PERSONAS.get(persona_id) or PERSONAS["zanele"]
    items = parse(brief.get("ingredients")); notes = (brief.get("notes") or "").lower()
    diet = (brief.get("diet") or "").lower(); serves = max(1, min(int(brief.get("serves") or 4), 20))
    by = {}
    for i in items: by.setdefault(role(i), []).append(i)
    removed = []
    if "veg" in diet:
        removed = [i for i in by.get("protein", []) if any(m in i for m in MEAT)]
        by["protein"] = [i for i in by.get("protein", []) if i not in removed]
    roles = {r for r, v in by.items() if v}
    cands = [a for a in ARCH if feasible(a, roles, notes)]
    if not cands: raise ValueError("Add at least one ingredient we can cook with, like a vegetable, grain or protein.")
    def draw(k):
        a, b = weights.get(k, (1.0, 1.0)); return rng.betavariate(a, b)
    score = {a: draw(f"{persona_id}|{a}") + .5 * draw(f"*|{a}") + p["likes"].get(a, 0) for a in cands}
    arch = max(score, key=score.get); A = ARCH[arch]
    heat = 0 if "mild" in notes else p["heat"]
    sp = join(by.get("spice", []), p["spice"] if heat else "a little salt and pepper")
    fill = dict(p=join(by.get("protein", []), "your main ingredients"), l=join(by.get("legume", []), "a little extra water"),
                v=join(by.get("veg", []), "any vegetables you have"), a=join(by.get("aromatic", []), "your seasoning"),
                s=join(by.get("starch", []), "bread or pap"), sp=sp)
    main = (by.get("protein") or by.get("legume") or by.get("veg") or items)[0]
    qty = {"protein": 150, "legume": 80, "starch": 80, "veg": 100}
    ing = [{"item": i, "amount": f"{qty[r] * serves} g" if r in qty else "to taste"}
           for r in ("protein", "legume", "starch", "veg", "aromatic", "spice", "dairy", "other") for i in by.get(r, [])]
    ing += [{"item": "oil", "amount": "2 tbsp"}, {"item": "salt and water", "amount": "as needed"}]
    return dict(id=uuid.uuid4().hex[:12], title=A["title"].format(main=main.title()), persona=persona_id, persona_name=p["name"],
                intro=p["intro"], archetype=arch, serves=serves, minutes=A["mins"], ingredients=ing,
                steps=[s.format(**fill) for s in A["steps"]],
                notes=[f"Left out {', '.join(removed)} to keep it {diet}."] if removed else [])

def learn(weights, persona, arch, rating=None, cooked=False, regenerated=False):
    """Bayesian bandit update: ratings and cooking shift Beta(alpha, beta) per persona and globally."""
    d = 0.0 if rating is None else (rating - 3) / 2
    up = max(d, 0) + (1.5 if cooked else 0); down = max(-d, 0) + (.5 if regenerated else 0)
    for k in (f"{persona}|{arch}", f"*|{arch}"):
        a, b = weights.get(k, (1.0, 1.0)); weights[k] = (min(a + up, 500.0), min(b + down, 500.0))
    return weights
