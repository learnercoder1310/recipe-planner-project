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
