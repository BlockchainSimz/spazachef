"""Recipe agent API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.chef_agent import FollowUpResponse, RecipeGenerationRequest, RecipeResponse, generate_recipe, handle_followup_question

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])

class FollowUpRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    chef_id: str = Field(min_length=1, max_length=64)
    chef_name: str = Field(min_length=1, max_length=100)
    recipe_context: str = Field(default="", max_length=10000)

@router.post("/generate", response_model=RecipeResponse)
async def generate_recipe_endpoint(request: RecipeGenerationRequest) -> RecipeResponse:
    try:
        return await generate_recipe(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Recipe generation failed") from exc

@router.post("/followup", response_model=FollowUpResponse)
async def followup_question_endpoint(request: FollowUpRequest) -> FollowUpResponse:
    try:
        return await handle_followup_question(request.question, request.chef_id, request.chef_name, request.recipe_context)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Follow-up request failed") from exc

@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "recipe-agent"}
