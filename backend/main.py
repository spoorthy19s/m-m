"""FastAPI application entry point for Margins & Mugs."""

from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
from typing import AsyncIterator

from dotenv import load_dotenv

load_dotenv()  # must run before importing backend.services.auth
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from backend.services.auth import create_session_token, verify_session_token
from backend.services.catalog import books_grouped_by_genre, menu_grouped_by_category
from backend.services.customers import normalize_login, upsert_customer
from backend.database.database import get_db, initialize_database
from backend.database.seed import seed_database
from backend.services.orders import CustomerNotFound, InvalidOrder, MenuItemNotFound, create_order
from backend.services.ratings import InvalidRating, RatingCustomerNotFound, save_rating


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create the SQLite tables once when the application starts."""
    initialize_database()
    seed_database()
    yield


app = FastAPI(
    title="Margins & Mugs API",
    description="API for the Margins & Mugs cafe and book catalogue.",
    version="1.0.0",
    lifespan=lifespan,
)

DEFAULT_DEV_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


def _allowed_origins() -> list[str]:
    """Read comma-separated origins from CORS_ORIGINS, or use the dev defaults."""
    raw = os.environ.get("CORS_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return origins or DEFAULT_DEV_ORIGINS


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

class MenuItemResponse(BaseModel):
    id: int
    name: str
    price: int
    image: str | None


class BookResponse(BaseModel):
    id: int
    title: str
    genre: str
    image: str | None


class LoginRequest(BaseModel):
    name: str = Field(max_length=100)
    phone: str


class LoginResponse(BaseModel):
    customer_id: int
    name: str
    access_token: str


class OrderItemRequest(BaseModel):
    menu_item_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=20)

    model_config = ConfigDict(extra="forbid")


class OrderRequest(BaseModel):
    items: list[OrderItemRequest] = Field(min_length=1)

    model_config = ConfigDict(extra="forbid")


class OrderItemResponse(BaseModel):
    menu_item_id: int
    name: str
    quantity: int
    unit_price: int
    line_total: int


class OrderResponse(BaseModel):
    order_id: int
    items: list[OrderItemResponse]
    total: int


class RatingRequest(BaseModel):
    stars: int = Field(strict=True, ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(extra="forbid")

class RatingResponse(BaseModel):
    message: str


def current_customer_id(authorization: str | None = Header(default=None)) -> int:
    """Return the customer id from a valid 'Authorization: Bearer <token>' header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return verify_session_token(authorization[len("Bearer "):])
    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


@app.get("/api/health", tags=["Health"])
def health_check(_connection: sqlite3.Connection = Depends(get_db)) -> dict[str, str]:
    """Report that the API is running and the request database opened."""
    return {"status": "ok"}


@app.get("/api/menu", tags=["Menu"], response_model=dict[str, list[MenuItemResponse]])
def read_menu(
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, list[dict[str, object]]]:
    """Return all cafe menu items grouped by category."""
    return menu_grouped_by_category(connection)


@app.get("/api/books", tags=["Books"], response_model=dict[str, list[BookResponse]])
def read_books(
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, list[dict[str, object]]]:
    """Return all books grouped by genre."""
    return books_grouped_by_genre(connection)


@app.post("/api/login", tags=["Customers"], response_model=LoginResponse)
def login(
    payload: LoginRequest,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, int | str]:
    """Validate customer details and return the existing or newly created customer."""
    try:
        name, phone = normalize_login(payload.name, payload.phone)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    customer = upsert_customer(connection, name, phone)
    return {**customer, "access_token": create_session_token(int(customer["customer_id"]))}


@app.post("/api/orders", tags=["Orders"], response_model=OrderResponse)
def submit_order(
    payload: OrderRequest,
    customer_id: int = Depends(current_customer_id),
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    """Create an order; prices and totals are always calculated server-side."""
    try:
        return create_order(
            connection,
            customer_id,
            [(item.menu_item_id, item.quantity) for item in payload.items],
        )
    except CustomerNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except MenuItemNotFound as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except InvalidOrder as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/api/ratings", tags=["Ratings"], response_model=RatingResponse)
def submit_rating(
    payload: RatingRequest,
    customer_id: int = Depends(current_customer_id),
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, str]:
    """Save a customer rating after checking its customer and comment."""
    try:
        message = save_rating(
            connection,
            customer_id,
            payload.stars,
            payload.comment,
        )
    except RatingCustomerNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except InvalidRating as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"message": message}


# Keep this at the very end: a "/" mount would otherwise swallow the /api routes.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
