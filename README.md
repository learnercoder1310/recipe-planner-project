# 🍳 Recipe Extractor & Meal Planner

A full-stack web application that extracts structured recipe data from any recipe blog URL using web scraping + LLM (Claude AI), stores results in PostgreSQL, and generates meal plans with combined shopping lists.

---

## 📁 Project Structure

```
recipe-planner/
├── backend/
│   ├── main.py          # FastAPI app + all routes
│   ├── database.py      # SQLAlchemy + PostgreSQL setup
│   ├── models.py        # ORM models (Recipe table)
│   ├── crud.py          # Database operations
│   ├── scraper.py       # BeautifulSoup web scraper
│   ├── llm.py           # Claude API + prompt templates
│   ├── requirements.txt
│   └── .env.example     # Environment variables template
├── frontend/
│   └── index.html       # Single-file React app (no build needed)
├── sample_data/
│   ├── sample_urls.md
│   └── grilled_cheese_output.json
├── prompts/
│   └── prompt_templates.md
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Anthropic API Key (free tier available at https://console.anthropic.com/)

---

### Step 1: Database Setup

```bash
# Start PostgreSQL and create database
psql -U postgres
CREATE DATABASE recipe_db;
\q
```

---

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and fill in:
#   ANTHROPIC_API_KEY=your_key_here
#   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/recipe_db

# Run the server
uvicorn main:app --reload --port 8000
```

The backend will be running at: **http://localhost:8000**  
API docs at: **http://localhost:8000/docs**

---

### Step 3: Frontend Setup

No build required! Just open the file:

```bash
# Option 1: Open directly in browser
open frontend/index.html

# Option 2: Serve with Python (recommended to avoid CORS issues)
cd frontend
python -m http.server 3000
# Then open http://localhost:3000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/extract-recipe` | Extract recipe from URL (scrape + LLM) |
| `GET`  | `/api/recipes` | Get all saved recipes (history) |
| `GET`  | `/api/recipes/{id}` | Get single recipe details |
| `POST` | `/api/meal-plan` | Generate meal plan for 3-5 recipes |
| `DELETE` | `/api/recipes/{id}` | Delete a recipe |

### POST /api/extract-recipe

**Request:**
```json
{ "url": "https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/" }
```

**Response:** Full recipe JSON (see sample_data/grilled_cheese_output.json)

### POST /api/meal-plan

**Request:**
```json
{ "recipe_ids": [1, 2, 3] }
```

**Response:**
```json
{
  "meal_plan": [...],
  "combined_shopping_list": {...},
  "total_nutrition_estimate": {...},
  "meal_prep_tips": [...]
}
```

---

## 🧪 Testing Steps

### Test 1: Basic Recipe Extraction
```bash
curl -X POST http://localhost:8000/api/extract-recipe \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/"}'
```

### Test 2: View History
```bash
curl http://localhost:8000/api/recipes
```

### Test 3: Get Recipe Details
```bash
curl http://localhost:8000/api/recipes/1
```

### Test 4: Generate Meal Plan
```bash
# First extract 3+ recipes, then:
curl -X POST http://localhost:8000/api/meal-plan \
  -H "Content-Type: application/json" \
  -d '{"recipe_ids": [1, 2, 3]}'
```

### Test 5: Error Handling
```bash
# Invalid URL
curl -X POST http://localhost:8000/api/extract-recipe \
  -H "Content-Type: application/json" \
  -d '{"url": "https://notarecipesite.xyz/nothing"}'

# Non-recipe page
curl -X POST http://localhost:8000/api/extract-recipe \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

---

## 🌐 Sample Recipe URLs to Test

```
https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/
https://www.allrecipes.com/recipe/24074/alysias-basic-meatballs/
https://www.bbcgoodfood.com/recipes/classic-pancakes
https://www.allrecipes.com/recipe/8652/garlic-chicken/
```

---

## 🛠 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend   | FastAPI (Python) |
| Database  | PostgreSQL + SQLAlchemy |
| Scraping  | BeautifulSoup4 + Requests |
| LLM       | Anthropic Claude (claude-3-haiku) |
| Frontend  | React (via CDN, no build needed) |

---

## ❗ Error Handling

The backend handles:
- **Invalid URL format** → 400 error with message
- **Unreachable URL** → 400 with connection error details  
- **Non-recipe page** → 422 with "content too short" message
- **LLM parse failure** → 500 with details
- **Database errors** → 500 with details
- **Duplicate URL** → Returns cached result (no re-processing)

---

## 🔧 Configuration

Edit `backend/.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...       # From console.anthropic.com
DATABASE_URL=postgresql://postgres:password@localhost:5432/recipe_db
```

---

## 📝 Notes

- The scraper extracts up to 8000 characters of page text to stay within LLM context limits
- Duplicate URLs return the cached database result without calling the LLM again
- The frontend works without any build step - just open index.html
- CORS is enabled for all origins in development (restrict in production)
