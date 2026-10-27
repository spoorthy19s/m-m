"use strict";

const API = "http://127.0.0.1:8000/api"; // later: "/api"

async function api(path, options = {}) {
    const res = await fetch(`${API}${path}`, {
        headers: { "Content-Type": "application/json" }, ...options
    });
    const data = await res.json();
    if (!res.ok) {
        const detail = data.detail;
        const message = Array.isArray(detail)
            ? detail.map(issue => issue.msg).join(" ")
            : detail;
        throw new Error(message || "Request failed");
    }
    return data;
}


const CART_KEY = "margins-and-mugs-cart";
const CUSTOMER_ID_KEY = "margins-and-mugs-customer-id";
const CUSTOMER_NAME_KEY = "margins-and-mugs-customer-name";
const ROOT = document.body.dataset.root || "";
const money = amount => `₹${amount}`;
const slug = value => value.toLowerCase().replace(/[^a-z0-9]+/g, "-");

function getCart() {
    try { return JSON.parse(localStorage.getItem(CART_KEY) || "{}"); }
    catch { return {}; }
}
function saveCart(cart) { localStorage.setItem(CART_KEY, JSON.stringify(cart)); }

function createCard(item, menu = false) {
    const { id, name, title, image, price } = item;
    const label = menu ? name : title;
    const card = document.createElement("article");
    card.className = menu ? "card menu-card" : "card book-card";
    const imageBox = document.createElement("div");
    imageBox.className = "card-image";
    const imageNode = document.createElement("img");
    imageNode.src = `${ROOT}images/${image}`;
    imageNode.alt = label;
    imageNode.loading = "lazy";
    imageNode.onerror = () => { imageBox.textContent = "Image not found"; };
    imageBox.append(imageNode);
    const titleNode = document.createElement("h3");
    titleNode.textContent = label;
    card.append(imageBox, titleNode);

    if (menu) {
        const priceLabel = document.createElement("p");
        priceLabel.className = "price";
        priceLabel.textContent = money(price);
        const controls = document.createElement("div");
        controls.className = "quantity";
        const minus = document.createElement("button");
        minus.type = "button"; minus.textContent = "−";
        minus.setAttribute("aria-label", `Remove one ${label}`);
        const quantity = document.createElement("output");
        quantity.id = `qty-${id}`;
        quantity.textContent = getCart()[id]?.qty || 0;
        const plus = document.createElement("button");
        plus.type = "button"; plus.textContent = "+";
        plus.setAttribute("aria-label", `Add one ${label}`);
        minus.addEventListener("click", () => changeQuantity(id, label, price, -1));
        plus.addEventListener("click", () => changeQuantity(id, label, price, 1));
        controls.append(minus, quantity, plus);
        card.append(priceLabel, controls);
    }
    return card;
}

function renderCatalogue(targetId, groupedItems, menu = false) {
    const target = document.getElementById(targetId);
    if (!target) return;
    target.replaceChildren();
    Object.entries(groupedItems).forEach(([category, items]) => {
        const heading = document.createElement("h2");
        heading.className = "category";
        heading.textContent = category;
        const cards = document.createElement("div");
        cards.className = "cards";
        items.forEach(item => cards.append(createCard(item, menu)));
    });
    target.append(heading, cards);
});
}

function showCatalogueError(targetId, error) {
    const target = document.getElementById(targetId);
    if (!target) return;
    const message = document.createElement("p");
    message.className = "form-message";
    message.textContent = error.message;
    target.replaceChildren(message);
}

function changeQuantity(id, name, price, difference) {
    const cart = getCart();
    const quantity = Math.max(0, (cart[id]?.qty || 0) + difference);
    if (quantity) cart[id] = { name, price, qty: quantity };
    else delete cart[id];
    saveCart(cart);
    const output = document.getElementById(`qty-${id}`);
    if (output) output.textContent = quantity;
    renderBill();
    updateCartCount();
}

function updateCartCount() {
    const count = Object.values(getCart()).reduce((sum, item) => sum + item.qty, 0);
    document.querySelectorAll(".cart-count").forEach(node => { node.textContent = count ? `(${count})` : ""; });
}

function renderBill() {
    const target = document.getElementById("order-content");
    if (!target) return;
    target.replaceChildren();
    const message = document.createElement("p");
    message.className = "form-message";
    message.id = "order-message";
    message.setAttribute("aria-live", "polite");
    target.append(message);
    const cart = getCart();
    const entries = Object.entries(cart);
    if (!entries.length) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "Your cart is empty. Browse the menu to add something!";
        target.append(empty);
        return;
    }
    const bill = document.createElement("div");
    bill.className = "bill";
    let estimatedTotal = 0;
    entries.forEach(([, item]) => {
        const subtotal = item.price * item.qty;
        estimatedTotal += subtotal;
        const row = document.createElement("div");
        row.className = "bill-row";
        const label = document.createElement("span"); label.textContent = item.name;
        const quantity = document.createElement("span"); quantity.textContent = `× ${item.qty}`;
        const amount = document.createElement("strong"); amount.textContent = money(subtotal);
        row.append(label, quantity, amount);
        bill.append(row);
    });
    const totalLabel = document.createElement("p");
    totalLabel.className = "bill-total";
    totalLabel.textContent = `Estimated total: ${money(estimatedTotal)}`;
    const placeOrder = document.createElement("button");
    placeOrder.className = "button button-primary";
    placeOrder.textContent = "Place Order";
    placeOrder.addEventListener("click", () => {
        const customer = localStorage.getItem(CUSTOMER_KEY) || "there";
        window.alert(`Thank you, ${customer}! Your order for ${money(total)} has been placed.`);
        localStorage.removeItem(CART_KEY);
        renderBill();
        updateCartCount();
    });
    target.append(bill, totalLabel, placeOrder);
}

function initializeLogin() {
    const form = document.getElementById("login-form");
    if (!form) return;
    form.addEventListener("submit", event => {
        event.preventDefault();
        const name = document.getElementById("customer-name").value.trim();
        const phone = document.getElementById("customer-phone").value.replace(/[\s()+-]/g, "");
        const message = document.getElementById("login-message");
        if (!name) { message.textContent = "Please enter your name."; return; }
        if (!/^\d{7,15}$/.test(phone)) { message.textContent = "Enter a phone number with 7 to 15 digits."; return; }
        localStorage.setItem(CUSTOMER_KEY, name);
        window.location.href = `${ROOT}html/menu.html`;
    });
}

function initializeRating() {
    const stars = [...document.querySelectorAll(".star")];
    if (!stars.length) return;
    let rating = 0;
    stars.forEach(star => star.addEventListener("click", () => {
        rating = Number(star.dataset.rating);
        stars.forEach(item => { item.textContent = Number(item.dataset.rating) <= rating ? "★" : "☆"; });
    }));
    document.getElementById("submit-rating")?.addEventListener("click", () => {
        const message = document.getElementById("rating-message");
        if (!rating) { message.textContent = "Please select a star rating."; return; }
        message.textContent = `Thank you for rating us ${rating} out of 5 stars!`;
    });
}

function initializeExitLinks() {
    document.querySelectorAll("[data-exit]").forEach(link => link.addEventListener("click", event => {
        event.preventDefault();
        window.location.href = `${ROOT}html/about.html#rating`;
    }));
    if (window.location.hash === "#exit") window.location.href = `${ROOT}html/about.html#rating`;
}

function initializePage() {
    const activePage = { items: "menu.html", books: "books.html", orders: "bill.html", about: "about.html" }[document.body.dataset.page];
    if (activePage) {
        document.querySelectorAll(".navigation .nav-link").forEach(link => {
            link.classList.toggle("active", link.getAttribute("href") === activePage);
        });
    }
    const customer = localStorage.getItem(CUSTOMER_KEY);
    document.querySelectorAll(".sidebar-welcome").forEach(node => {
        node.textContent = customer ? `Welcome, ${customer}` : "Welcome to the cafe";
    });
    renderCatalogue("items-content", MENU_ITEMS,
        ["Hot Beverages", "Desserts & Bakes", "Snacks & Spicy Items"], true);
    renderCatalogue("books-content", BOOKS,
        ["General Fiction", "Classic Romance", "Romance", "Literary Fiction", "Political Satire", "Psychological Fiction", "Thrillers"]);
    renderBill();
    updateCartCount();
    initializeLogin();
    initializeRating();
    initializeExitLinks();
}

document.addEventListener("DOMContentLoaded", initializePage);
