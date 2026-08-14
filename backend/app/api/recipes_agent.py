"""Recipe agent API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.agents.chef_agent import (
    RecipeGenerationRequest, 
    RecipeResponse,
    generate_recipe,
    handle_followup_question
)

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])

class FollowUpRequest(BaseModel):
    question: str
    chef_id: str
    chef_name: str

@router.post("/generate", response_model=RecipeResponse)
async def generate_recipe_endpoint(request: RecipeGenerationRequest):
    """Generate a recipe based on ingredients and chef"""
    try:
        response = await generate_recipe(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/followup")
async def followup_question_endpoint(request: FollowUpRequest):
    """Handle follow-up questions about a recipe"""
    try:
        response = await handle_followup_question(
            question=request.question,
            chef_id=request.chef_id,
            chef_name=request.chef_name
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "recipe-agent"}
