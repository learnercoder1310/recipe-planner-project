# Prompt Templates

## 1. Recipe Extraction Prompt (used in llm.py → RECIPE_EXTRACTION_PROMPT)

```
You are a professional recipe data extractor. 
Your job is to analyze raw text scraped from a recipe webpage and return ONLY a valid JSON object.

Analyze this recipe page content carefully and extract all recipe information.

RECIPE PAGE URL: {url}

RAW PAGE CONTENT:
{page_text}

Return ONLY a JSON object (no markdown, no backticks, no explanation) with EXACTLY this structure:

{
  "title": "Recipe title as found on page",
  "cuisine": "Cuisine type (e.g., American, Italian, Indian, Mexican, etc.)",
  "prep_time": "Preparation time (e.g., 10 mins)",
  "cook_time": "Cook time (e.g., 20 mins)",
  "total_time": "Total time (e.g., 30 mins)",
  "servings": 4,
  "difficulty": "easy | medium | hard",
  "ingredients": [
    {"quantity": "2", "unit": "cups", "item": "all-purpose flour"},
    {"quantity": "1", "unit": "tsp", "item": "salt"},
    {"quantity": "3", "unit": "", "item": "eggs"}
  ],
  "instructions": ["Step 1: ...", "Step 2: ..."],
  "nutrition_estimate": {
    "calories": 350,
    "protein": "12g",
    "carbs": "40g",
    "fat": "15g"
  },
  "substitutions": [
    "Replace butter with olive oil for a dairy-free version.",
    "Use gluten-free flour instead of all-purpose flour.",
    "Swap regular milk with almond milk to reduce calories."
  ],
  "shopping_list": {
    "dairy": ["butter", "milk"],
    "produce": ["onions", "garlic"],
    "pantry": ["olive oil", "flour"],
    "meat": ["chicken breast"],
    "spices": ["cumin", "paprika"]
  },
  "related_recipes": ["Recipe Name 1", "Recipe Name 2", "Recipe Name 3"]
}

RULES:
1. difficulty: judge by number of steps, techniques, and time needed
2. ingredients: ALWAYS separate quantity, unit, and item. If no unit, use ""
3. nutrition_estimate: provide reasonable estimates even if not on page
4. substitutions: provide exactly 3 practical substitutions
5. shopping_list: group ALL ingredients by category
6. related_recipes: suggest 3 complementary or similar dishes
7. If information is missing, use reasonable defaults
8. Return ONLY the JSON object, nothing else
```

---

## 2. Meal Plan Generation Prompt (used in llm.py → MEAL_PLAN_PROMPT)

```
You are a professional nutritionist and meal planner.

The user has selected these {count} recipes for their meal plan:
{recipes_summary}

Generate a practical meal plan with a COMBINED SHOPPING LIST.

Return ONLY a JSON object with this exact structure:

{
  "meal_plan": [
    {
      "day": "Day 1",
      "meal": "Breakfast | Lunch | Dinner",
      "recipe_title": "Recipe name from the list",
      "notes": "Brief serving suggestion or tip"
    }
  ],
  "combined_shopping_list": {
    "dairy": ["2 cups milk", "100g butter"],
    "produce": ["3 tomatoes", "1 head garlic"],
    "pantry": ["2 cups flour", "olive oil"],
    "meat": ["500g chicken"],
    "spices": ["cumin", "paprika"],
    "bakery": ["1 loaf bread"]
  },
  "total_nutrition_estimate": {
    "avg_daily_calories": 1800,
    "avg_protein": "65g",
    "avg_carbs": "220g",
    "avg_fat": "70g"
  },
  "meal_prep_tips": [
    "Tip 1 about batch cooking or storage",
    "Tip 2 about prep efficiency",
    "Tip 3 about ingredient reuse"
  ]
}

RULES:
1. Assign each recipe to breakfast/lunch/dinner based on recipe type
2. Merge duplicate ingredients in the shopping list with combined quantities
3. The meal_plan should cover as many days as there are recipes
4. Return ONLY the JSON object, nothing else
```

---

## Prompt Design Decisions

### Why these prompts work well:
1. **Strict output format**: Instructing the model to return ONLY JSON prevents preamble/postamble that would break parsing.
2. **Explicit rules section**: Rules at the bottom act as a checklist for the model - reduces hallucination.
3. **Few-shot ingredient format**: Showing `{"quantity": "2", "unit": "cups", "item": "..."}` in the schema teaches the model to always split ingredients correctly.
4. **Grounding in scraped text**: The raw page content is passed verbatim - the model extracts from actual content rather than hallucinating.
5. **Nutrition estimation**: Explicitly allowed ("provide estimates even if not on page") since most recipe pages don't include structured nutrition data.
6. **Substitutions diversity**: The examples hint at diversity (dairy-free, gluten-free, flavor variation) without prescribing exact substitutions.
