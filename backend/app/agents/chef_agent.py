"""AI Chef Agent for recipe generation"""

import json
from typing import List
from pydantic import BaseModel

class RecipeGenerationRequest(BaseModel):
    ingredients: List[str]
    chef_id: str
    chef_name: str

class RecipeResponse(BaseModel):
    recipe_description: str
    ingredients: List[str]
    instructions: List[str]

CHEF_PROMPTS = {
    "gogo-precious": """You are Gogo Precious, a warm South African grandmother. 
    You speak with Zulu/Sotho dialect using words like "eish", "hey my child", "hai", "ayoba". 
    You are motherly and caring. Keep responses warm and conversational.
    Always add a caring, grandmotherly touch to your recipe descriptions.""",
    
    "mandla": """You are Chef Mandla from Johannesburg, a confident young chef.
    You speak with kasi dialect using words like "bra", "isit", "eish", "yebo", "ay nah".
    You are street-smart and modern. Make cooking sound exciting and achievable.
    Speak like a friend with humor and confidence.""",
    
    "tandie": """You are Tandie the Baker from Cape Town, creative and playful.
    You use Cape Town vernacular: "hey-hey", "nogal", "lekker", "goed", "sharp".
    You are fun and creative. Make recipes sound like adventures.
    Keep it light and entertaining.""",
    
    "baba-thabo": """You are Baba Thabo, a wise traditional South African.
    You speak with traditional dialect using "ayoba", "respect". Teach through wisdom.
    Every recipe comes with life lessons. Speak like an elder with deep knowledge.
    Be patient and philosophical.""",
    
    "chef-zama": """You are Chef Zama, energetic and funny modern kasi chef.
    You use contemporary South African dialect: "haibo", "no ways", "for real?", "that's mad".
    You have lots of humor and enthusiasm. Make everything sound fun and achievable.
    Be the hype person of cooking.""",
}

async def generate_recipe(request: RecipeGenerationRequest) -> RecipeResponse:
    """Generate a recipe based on ingredients and chef personality"""
    
    chef_prompt = CHEF_PROMPTS.get(request.chef_id, CHEF_PROMPTS["chef-zama"])
    
    system_prompt = f"""{chef_prompt}

Your task is to generate an authentic South African recipe using ONLY the ingredients provided.
Be creative but realistic. Think like a kasi chef - use what you have.

Respond with a warm, engaging recipe description that includes the recipe name, ingredients, steps, and tips."""
    
    user_message = f"""Please create a South African kasi recipe using these ingredients: {', '.join(request.ingredients)}
    
Remember to stay in character as {request.chef_name} with the authentic South African dialect and personality."""

    try:
        # Mock response for demonstration
        mock_response = {
            "recipe_name": f"Lekker {request.chef_name}'s Special",
            "introduction": f"Ayoba! With these ingredients, we're gonna make something special, hey!",
            "ingredients_used": request.ingredients,
            "instructions": [
                "Heat your pot or pan",
                "Add your aromatics first",
                "Build your flavors layer by layer",
                "Let it simmer until lekker",
                "Taste and adjust",
                "Serve hot with respect"
            ],
            "tips": "This is how we do it in the kasi - with love and what we have!",
            "cooking_time": "30-45 minutes"
        }
        
        return RecipeResponse(
            recipe_description=f"""**{mock_response['recipe_name']}**

{mock_response['introduction']}

**What we're using:**
{', '.join(mock_response['ingredients_used'])}

**How to make it:**
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(mock_response['instructions']))}

**Chef's tip:** {mock_response['tips']}

**Time:** {mock_response['cooking_time']}

Now ask me questions about this recipe, hey! I got answers!""",
            ingredients=mock_response['ingredients_used'],
            instructions=mock_response['instructions']
        )
        
    except Exception as e:
        raise Exception(f"Error generating recipe: {str(e)}")

async def handle_followup_question(
    question: str, 
    chef_id: str, 
    chef_name: str
) -> dict:
    """Handle follow-up questions about a recipe"""
    
    chef_prompt = CHEF_PROMPTS.get(chef_id, CHEF_PROMPTS["chef-zama"])
    
    system_prompt = f"""{chef_prompt}

The user is asking a follow-up question about a recipe we just created.
Answer their question directly but stay in character.
Keep it short, practical, and helpful."""
    
    try:
        # Mock response for demonstration
        return {
            "response": f"{chef_name}: Ay, that's a good question! You can adjust the recipe like this. Just remember - cooking is about tasting and adjusting. Trust your senses, hey!"
        }
        
    except Exception as e:
        raise Exception(f"Error handling follow-up: {str(e)}")
