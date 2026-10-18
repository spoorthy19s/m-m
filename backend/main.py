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
    name: str
    phone: str


class LoginResponse(BaseModel):
    customer_id: int
    name: str


class OrderItemRequest(BaseModel):
    menu_item_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=20)

    class Config:
        extra = "forbid"


class OrderRequest(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[OrderItemRequest]

    class Config:
        extra = "forbid"


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
    customer_id: int = Field(gt=0)
    stars: int = Field(strict=True, ge=1, le=5)
    comment: str | None = None

    class Config:
        extra = "forbid"


class RatingResponse(BaseModel):
    message: str


def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency that closes its connection after the request."""
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


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

    return upsert_customer(connection, name, phone)


@app.post("/api/orders", tags=["Orders"], response_model=OrderResponse)
def submit_order(
    payload: OrderRequest,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    """Create an order; prices and totals are always calculated server-side."""
    try:
        return create_order(
            connection,
            payload.customer_id,
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
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, str]:
    """Save a customer rating after checking its customer and comment."""
    try:
        message = save_rating(
            connection,
            payload.customer_id,
            payload.stars,
            payload.comment,
        )
    except RatingCustomerNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except InvalidRating as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"message": message}
