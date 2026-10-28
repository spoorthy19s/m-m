# Margins & Mugs

A small full-stack café and book catalogue application. Customers can log in with a name and phone number, browse the menu and books, build a cart, place orders, and leave a rating with an optional comment.

The project began as a Tkinter application and now includes a FastAPI web backend with a static HTML, CSS, and JavaScript frontend.

## Features

- Customer login using a name and phone number
- Menu and book catalogues
- Cart, bill calculation, and order placement
- A receipt retained on the bill page after checkout
- A star rating with an optional comment (up to 500 characters)
- One rating per customer per UTC calendar day

AI, forecasting, sentiment analysis, admin pages, notebooks, generated data, and automated tests are not currently implemented; the related placeholder files or directories are not presented as completed features.

## Tech stack

- Python 3.14
- FastAPI and Uvicorn
- SQLite
- HTML, CSS, and JavaScript
- pandas, scikit-learn, and joblib for the machine-learning work in progress
- Groq SDK for planned LLM integration

## Project structure

```text
m-m-main/
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application and API routes
│   ├── ai.py                      # Reserved for AI integration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py            # SQLite connection and request dependency
│   │   ├── schema.sql             # Database table definitions
│   │   └── seed.py                # Initial catalogue data
│   ├── services/
│   │   ├── auth.py
│   │   ├── catalog.py
│   │   ├── customers.py
│   │   ├── orders.py
│   │   └── ratings.py
│   └── ml/
│       ├── forecast.py
│       ├── recommender.py
│       └── sentiment.py
├── frontend/
│   ├── index.html                 # Customer login page
│   ├── html/
│   │   ├── about.html
│   │   ├── bill.html
│   │   ├── books.html
│   │   └── menu.html
│   ├── css/style.css
│   └── js/app.js
├── legacy_tkinter/                # Original desktop project
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

Use Python 3.14 and install the pinned dependencies:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`, set a stable `SESSION_SECRET`, then start the application from the project root:

```bash
uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000> in a browser. For deployment, set the same `SESSION_SECRET` in the hosting provider's environment settings. Generate a value with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Keep `.env` private; it is ignored by Git.
