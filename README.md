
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
margins-mugs/
├── backend/
│   ├── main.py          # FastAPI app and routes
│   ├── database.py      # SQLite connection
│   ├── seed.py          # Loads menu and books into the DB
│   ├── ai.py            # LLM helper functions
│   ├── requirements.txt
│   └── .env             # API key (not committed)
├── frontend/
│   ├── index.html       # Login
│   ├── html/            # about.html, bill.html, books.html, menu.html
│   ├── css/style.css
│   ├── js/              # menu.js, books.js, bill.js, chat.js, common.js
│   └── images/
└── README.md
```

