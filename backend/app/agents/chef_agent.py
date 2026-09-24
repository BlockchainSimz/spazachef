"""Provider-backed AI recipe generation with strict validation."""
import json
from typing import List
import httpx
from pydantic import BaseModel, Field
from app.config import settings

class RecipeGenerationRequest(BaseModel):
    ingredients: List[str] = Field(min_length=1, max_length=30)
    chef_id: str = Field(min_length=1, max_length=64)
    chef_name: str = Field(min_length=1, max_length=100)

    def normalized_ingredients(self) -> list[str]:
        values = [x.strip() for x in self.ingredients if x.strip()]
        if not values:
            raise ValueError("At least one ingredient is required")
        return list(dict.fromkeys(values))[:30]

class RecipeResponse(BaseModel):
    recipe_name: str = Field(min_length=1, max_length=200)
    recipe_description: str = Field(min_length=1, max_length=12000)
    ingredients: List[str] = Field(min_length=1, max_length=50)
    instructions: List[str] = Field(min_length=1, max_length=30)
    tips: str = Field(default="", max_length=3000)
    cooking_time: str = Field(default="", max_length=100)

class FollowUpResponse(BaseModel):
    response: str = Field(min_length=1, max_length=4000)

CHEF_PROMPTS = {
    "gogo-precious": "Warm South African grandmother; caring and practical.",
    "mandla": "Confident Johannesburg chef; modern, practical and encouraging.",
    "tandie": "Creative Cape Town baker; playful and encouraging.",
    "baba-thabo": "Wise traditional South African cook; patient and respectful.",
    "chef-zama": "Energetic modern kasi chef; funny and practical.",
}

def _chef_prompt(chef_id: str) -> str:
    return CHEF_PROMPTS.get(chef_id, CHEF_PROMPTS["chef-zama"])

async def _call_ai(system: str, user: str) -> str:
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError("AI provider is not configured")
    payload = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": 1800,
        "temperature": 0.7,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    headers = {
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    async with httpx.AsyncClient(timeout=settings.ANTHROPIC_TIMEOUT_SECONDS) as client:
        response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        response.raise_for_status()
    data = response.json()
    text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text").strip()
    if not text:
        raise RuntimeError("AI provider returned an empty response")
    return text

def _json_object(text: str) -> dict:
    value = text.strip()
    if value.startswith("```"):
        value = value.replace("```json", "", 1).replace("```", "", 1).strip()
    try:
        result = json.loads(value)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI provider returned invalid structured data") from exc
    if not isinstance(result, dict):
        raise RuntimeError("AI provider returned an invalid object")
    return result

async def generate_recipe(request: RecipeGenerationRequest) -> RecipeResponse:
    ingredients = request.normalized_ingredients()
    system = (_chef_prompt(request.chef_id) + "\nCreate a realistic South African recipe using only the supplied ingredients. "
              "Return ONLY JSON with recipe_name, recipe_description, ingredients, instructions, tips and cooking_time.")
    raw = await _call_ai(system, "Create a recipe for " + request.chef_name + ". Ingredients: " + ", ".join(ingredients))
    return RecipeResponse.model_validate(_json_object(raw))

async def handle_followup_question(question: str, chef_id: str, chef_name: str, recipe_context: str = "") -> FollowUpResponse:
    question = question.strip()
    if not question:
        raise ValueError("Question is required")
    system = _chef_prompt(chef_id) + "\nAnswer the cooking question concisely and safely. Return JSON with a response field."
    user = "Recipe:\n" + recipe_context[:10000] + "\nQuestion: " + question + "\nChef: " + chef_name
    raw = await _call_ai(system, user)
    result = _json_object(raw)
    return FollowUpResponse(response=str(result.get("response", raw))[:4000])
