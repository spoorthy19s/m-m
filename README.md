
# ☕📚 Margins & Mugs

A full-stack web café management system that combines the joy of coffee with the love of books. Browse the menu, discover books, place orders, and get AI-powered recommendations.

> Originally built as a Python Tkinter desktop mini project, now rebuilt as a web application with AI features.

---

## ✨ Features

- **Login** with name and phone number validation
- **Menu** with hot beverages, desserts & bakes, and snacks
- **Books available** in the café: general fiction, non-fiction, thrillers
- **Cart and billing** with quantity controls and automatic total calculation
- **Order placement** saved to the database
- **Rating system** (1–5 stars) on exit
- **AI chatbot** that answers questions about the menu and books
- **AI recommendations** that pair a book with your order, plus mood-based picks
- **Admin dashboard** with orders, top sellers, revenue, and an AI summary of ratings

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Database | SQLite |
| AI | LLM API (GROQ) |
| Charts | Chart.js |
| Deployment | Render |

---

## 📁 Project Structure

```
margins-and-mugs/
├── backend/
│   ├── main.py            # Flask app and API routes
│   ├── database.py        # SQLite connection helpers
│   ├── schema.sql         # Database table definitions
│   ├── seed.py            # Loads the menu into the database
│   ├── ai.py              # Connects API endpoints to the ML modules
│   ├── ml/
│   │   ├── forecast.py    # Demand forecasting
│   │   ├── recommender.py # Item recommendations
│   │   └── sentiment.py   # Review sentiment classifier
│   └── models/            # Saved trained models (.joblib)
├── frontend/
│   ├── index.html         # Landing page and best sellers
│   ├── html/              # Menu, cart/bill, admin, books, about pages
│   ├── css/style.css      # Styling
│   └── js/                # Page scripts and API helper
├── data/                  # Dataset generator and generated orders
├── notebooks/             # EDA and model experiments
├── tests/                 # Automated tests
├── docs/                  # Screenshots, architecture diagram, demo GIF
├── legacy_tkinter/        # Original Tkinter version
├── requirements.txt
└── README.md
```

