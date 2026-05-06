"""
LLM integration using Google Gemini API (NEW SDK FIXED VERSION)
"""

import os
import json
import re
from google import genai

# ── Setup ────────────────────────────────────────────────
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Prompt Templates ─────────────────────────────────────

RECIPE_EXTRACTION_PROMPT = """You are a professional recipe data extractor. 
Analyze the scraped webpage text and return ONLY valid JSON.

URL: {url}

PAGE CONTENT:
{page_text}

Return ONLY JSON with:
- title
- ingredients
- instructions
- cuisine
- prep_time
- cook_time
- servings
- difficulty
- nutrition_estimate
- substitutions
- shopping_list
- related_recipes
"""

MEAL_PLAN_PROMPT = """You are a professional nutritionist.

Recipes:
{recipes_summary}

Return ONLY JSON containing:
- meal_plan (day-wise schedule)
- combined_shopping_list
- total_nutrition_estimate
- meal_prep_tips
"""


# ── LLM CALL ─────────────────────────────────────────────

def call_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text


# ── JSON PARSER ──────────────────────────────────────────

def parse_json_response(raw: str) -> dict:
    raw = raw.strip()

    # remove markdown formatting
    raw = re.sub(r"^```json", "", raw)
    raw = re.sub(r"```$", "", raw)

    try:
        return json.loads(raw)
    except:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Invalid JSON from LLM")


# ── PUBLIC FUNCTIONS ─────────────────────────────────────

def extract_recipe_with_llm(url: str, page_text: str) -> dict:
    prompt = RECIPE_EXTRACTION_PROMPT.format(
        url=url,
        page_text=page_text
    )
    raw = call_gemini(prompt)
    return parse_json_response(raw)


def generate_meal_plan_with_llm(recipes: list) -> dict:
    summaries = []

    for i, r in enumerate(recipes, 1):
        ingredients = ", ".join(
            f"{ing.get('quantity','')} {ing.get('item','')}"
            for ing in r.get("ingredients", [])[:10]
        )
        summaries.append(f"{i}. {r['title']} - {ingredients}")

    prompt = MEAL_PLAN_PROMPT.format(
        recipes_summary="\n".join(summaries)
    )

    raw = call_gemini(prompt)
    return parse_json_response(raw)