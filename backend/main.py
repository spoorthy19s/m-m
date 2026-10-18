"""FastAPI application entry point for Margins & Mugs."""

from contextlib import asynccontextmanager
import sqlite3
from typing import AsyncIterator, Iterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from catalog import books_grouped_by_genre, menu_grouped_by_category
from customers import normalize_login, upsert_customer
from database import get_connection, initialize_database
from orders import CustomerNotFound, InvalidOrder, MenuItemNotFound, create_order
from ratings import InvalidRating, RatingCustomerNotFound, save_rating


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create the SQLite tables once when the application starts."""
    initialize_database()
    yield


app = FastAPI(
    title="Margins & Mugs API",
    description="API for the Margins & Mugs cafe and book catalogue.",
    version="1.0.0",
    lifespan=lifespan,
)

DEVELOPMENT_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=DEVELOPMENT_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
