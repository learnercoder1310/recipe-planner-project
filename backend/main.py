"""
Recipe Extractor & Meal Planner - FastAPI Backend
Uses BeautifulSoup for scraping + Claude API (via Anthropic) as LLM
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import uvicorn

from database import engine, Base, get_db
from sqlalchemy.orm import Session
from fastapi import Depends
import models
import crud
from scraper import scrape_recipe_page
from llm import extract_recipe_with_llm, generate_meal_plan_with_llm

# ── App Setup ──────────────────────────────────────────────────────────────────
app = FastAPI(title="Recipe Extractor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables on startup
Base.metadata.create_all(bind=engine)

# ── Request/Response Schemas ───────────────────────────────────────────────────
class RecipeURLRequest(BaseModel):
    url: str

class MealPlanRequest(BaseModel):
    recipe_ids: List[int]  # 3-5 saved recipe IDs

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Recipe Extractor API is running!"}


@app.post("/api/extract-recipe")
def extract_recipe(request: RecipeURLRequest, db: Session = Depends(get_db)):
    """
    Main endpoint: scrapes URL → sends to LLM → stores in DB → returns JSON
    """
    url = request.url.strip()

    # 1. Check if already processed
    existing = crud.get_recipe_by_url(db, url)
    if existing:
        return existing.to_dict()

    # 2. Scrape page
    try:
        raw_text = scrape_recipe_page(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")

    if not raw_text or len(raw_text) < 100:
        raise HTTPException(status_code=422, detail="Page content too short or not a recipe page.")

    # 3. Send to LLM for extraction
    try:
        recipe_data = extract_recipe_with_llm(url, raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {str(e)}")

    # 4. Store in database
    try:
        db_recipe = crud.create_recipe(db, url, recipe_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return db_recipe.to_dict()


@app.get("/api/recipes")
def list_recipes(db: Session = Depends(get_db)):
    """Return all previously extracted recipes (history view)."""
    recipes = crud.get_all_recipes(db)
    return [r.to_dict_summary() for r in recipes]


@app.get("/api/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get full details of a single recipe by ID."""
    recipe = crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return recipe.to_dict()


@app.post("/api/meal-plan")
def generate_meal_plan(request: MealPlanRequest, db: Session = Depends(get_db)):
    """
    Given 3-5 recipe IDs, generate a combined meal plan with merged shopping list.
    """
    if not (3 <= len(request.recipe_ids) <= 5):
        raise HTTPException(status_code=400, detail="Please select between 3 and 5 recipes.")

    recipes = []
    for rid in request.recipe_ids:
        r = crud.get_recipe_by_id(db, rid)
        if not r:
            raise HTTPException(status_code=404, detail=f"Recipe ID {rid} not found.")
        recipes.append(r.to_dict())

    try:
        meal_plan = generate_meal_plan_with_llm(recipes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meal plan generation failed: {str(e)}")

    return meal_plan


@app.delete("/api/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Delete a recipe from history."""
    success = crud.delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return {"message": "Recipe deleted successfully."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
