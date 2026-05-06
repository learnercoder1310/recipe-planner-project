"""
SQLAlchemy ORM Models
"""

import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id               = Column(Integer, primary_key=True, index=True)
    url              = Column(String(2048), unique=True, nullable=False, index=True)
    title            = Column(String(512), nullable=False)
    cuisine          = Column(String(128))
    prep_time        = Column(String(64))
    cook_time        = Column(String(64))
    total_time       = Column(String(64))
    servings         = Column(Integer)
    difficulty       = Column(String(32))   # easy / medium / hard

    # Complex fields stored as JSON
    ingredients      = Column(JSON)  # [{quantity, unit, item}, ...]
    instructions     = Column(JSON)  # [step1, step2, ...]
    nutrition        = Column(JSON)  # {calories, protein, carbs, fat}
    substitutions    = Column(JSON)  # ["Replace X with Y", ...]
    shopping_list    = Column(JSON)  # {category: [items], ...}
    related_recipes  = Column(JSON)  # ["Recipe A", ...]

    created_at       = Column(DateTime, default=datetime.utcnow)

    # ── Serializers ────────────────────────────────────────────────────────────

    def to_dict(self):
        """Full recipe as dict (for API response)."""
        return {
            "id":             self.id,
            "url":            self.url,
            "title":          self.title,
            "cuisine":        self.cuisine,
            "prep_time":      self.prep_time,
            "cook_time":      self.cook_time,
            "total_time":     self.total_time,
            "servings":       self.servings,
            "difficulty":     self.difficulty,
            "ingredients":    self.ingredients or [],
            "instructions":   self.instructions or [],
            "nutrition_estimate": self.nutrition or {},
            "substitutions":  self.substitutions or [],
            "shopping_list":  self.shopping_list or {},
            "related_recipes":self.related_recipes or [],
            "created_at":     self.created_at.isoformat() if self.created_at else None,
        }

    def to_dict_summary(self):
        """Lightweight version for history table."""
        return {
            "id":         self.id,
            "url":        self.url,
            "title":      self.title,
            "cuisine":    self.cuisine,
            "difficulty": self.difficulty,
            "servings":   self.servings,
            "total_time": self.total_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
