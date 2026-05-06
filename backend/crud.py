"""
CRUD helpers - keep database logic here, away from routes.
"""

from sqlalchemy.orm import Session
import models


def get_recipe_by_url(db: Session, url: str):
    return db.query(models.Recipe).filter(models.Recipe.url == url).first()


def get_recipe_by_id(db: Session, recipe_id: int):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()


def get_all_recipes(db: Session):
    return db.query(models.Recipe).order_by(models.Recipe.created_at.desc()).all()


def create_recipe(db: Session, url: str, data: dict) -> models.Recipe:
    """
    Create a new Recipe row from LLM-extracted data dict.
    """
    recipe = models.Recipe(
        url             = url,
        title           = data.get("title", "Untitled Recipe"),
        cuisine         = data.get("cuisine", "Unknown"),
        prep_time       = data.get("prep_time", "N/A"),
        cook_time       = data.get("cook_time", "N/A"),
        total_time      = data.get("total_time", "N/A"),
        servings        = data.get("servings", 1),
        difficulty      = data.get("difficulty", "medium"),
        ingredients     = data.get("ingredients", []),
        instructions    = data.get("instructions", []),
        nutrition       = data.get("nutrition_estimate", {}),
        substitutions   = data.get("substitutions", []),
        shopping_list   = data.get("shopping_list", {}),
        related_recipes = data.get("related_recipes", []),
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def delete_recipe(db: Session, recipe_id: int) -> bool:
    recipe = get_recipe_by_id(db, recipe_id)
    if not recipe:
        return False
    db.delete(recipe)
    db.commit()
    return True
