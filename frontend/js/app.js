"use strict";

const API = "/api";

async function api(path, options = {}) {
    const { headers = {}, ...requestOptions } = options;
    const token = localStorage.getItem(SESSION_TOKEN_KEY);
    let res;
    try {
        res = await fetch(`${API}${path}`, {
            ...requestOptions,
            headers: {
                "Content-Type": "application/json",
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
                ...headers
            }
        });
    } catch {
        throw new Error("Cannot reach the server. Please try again.");
    }
    let data = null;
    try { data = await res.json(); } catch { /* body was not JSON */ }

    if (res.status === 401) {
        clearSession();
        window.location.href = `${ROOT}index.html`;
        throw new Error(data?.detail || "Please log in.");
    }
    if (!res.ok) {
        const detail = data?.detail;
        const message = Array.isArray(detail)
            ? detail.map(issue => issue.msg).join(" ")
            : detail;
        const error = new Error(message || `Request failed (${res.status}).`);
        error.status = res.status;
        throw error;
    }
    if (data === null) throw new Error("Unexpected response from the server.");
    return data;
}

function clearSession() {
    localStorage.removeItem(SESSION_TOKEN_KEY);
    localStorage.removeItem(CUSTOMER_NAME_KEY);
    localStorage.removeItem(CART_KEY);
    localStorage.removeItem(RECEIPT_KEY);
}

const CART_KEY = "margins-and-mugs-cart-v2";
const SESSION_TOKEN_KEY = "margins-and-mugs-session-token";
const CUSTOMER_NAME_KEY = "margins-and-mugs-customer-name";
const RECEIPT_KEY = "margins-and-mugs-last-receipt";
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
        const receipt = JSON.parse(localStorage.getItem(RECEIPT_KEY) || "null");
        if (receipt) {
            const receiptNode = document.createElement("section");
            receiptNode.className = "bill receipt";
            const title = document.createElement("h2");
            title.textContent = `Receipt for order #${receipt.order_id}`;
            const date = document.createElement("p");
            date.textContent = `Placed ${new Date(receipt.placed_at).toLocaleString()}`;
            receiptNode.append(title, date);
            receipt.items.forEach(item => {
                const row = document.createElement("div");
                row.className = "bill-row";
                const name = document.createElement("span"); name.textContent = item.name;
                const quantity = document.createElement("span"); quantity.textContent = `× ${item.quantity}`;
                const amount = document.createElement("strong"); amount.textContent = money(item.line_total);
                row.append(name, quantity, amount);
                receiptNode.append(row);
            });
            const total = document.createElement("p");
            total.className = "bill-total";
            total.textContent = `Total paid: ${money(receipt.total)}`;
            receiptNode.append(total);
            target.append(receiptNode);
            return;
        }
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
    placeOrder.addEventListener("click", async () => {
        const sessionToken = localStorage.getItem(SESSION_TOKEN_KEY);
        if (!sessionToken) {
            message.textContent = "Please log in before placing an order.";
            return;
        }
        placeOrder.disabled = true;
        try {
            const order = await api("/orders", {
                method: "POST",
                body: JSON.stringify({
                    items: entries.map(([id, item]) => ({ menu_item_id: Number(id), quantity: item.qty }))
                })
            });
            localStorage.setItem(RECEIPT_KEY, JSON.stringify({
                ...order,
                placed_at: new Date().toISOString()
            }));
            localStorage.removeItem(CART_KEY);
            renderBill();
            document.getElementById("order-message")?.remove();
            updateCartCount();
        } catch (error) {
            const staleItem = error.status === 400 && error.message.match(/Menu item id (\d+) was not found\./);
            if (staleItem && getCart()[staleItem[1]]) {
                const updatedCart = getCart();
                delete updatedCart[staleItem[1]];
                saveCart(updatedCart);
                renderBill();
                const currentMessage = document.getElementById("order-message");
                if (currentMessage) currentMessage.textContent = `An unavailable menu item was removed from your cart. Review the updated order and try again.`;
                updateCartCount();
                return;
            }
            message.textContent = error.message;
            placeOrder.disabled = false;
        }
    });
    target.append(bill, totalLabel, placeOrder);
}

function initializeLogin() {
    const form = document.getElementById("login-form");
    if (!form) return;
    form.addEventListener("submit", async event => {
        event.preventDefault();
        const name = document.getElementById("customer-name").value.trim();
        const phone = document.getElementById("customer-phone").value;
        const message = document.getElementById("login-message");
        message.textContent = "";
        try {
            const customer = await api("/login", {
                method: "POST",
                body: JSON.stringify({ name, phone })
            });
            if (!customer.access_token) throw new Error("Login failed. Please try again.");
            localStorage.setItem(SESSION_TOKEN_KEY, customer.access_token);
            localStorage.setItem(CUSTOMER_NAME_KEY, customer.name);
            window.location.href = `${ROOT}html/menu.html`;
        } catch (error) {
            message.textContent = error.message;
        }
    });
}

function initializeRating() {
    const stars = [...document.querySelectorAll(".star")];
    if (!stars.length) return;
    let rating = 0;
    stars.forEach(star => star.setAttribute("aria-pressed", "false"));
    stars.forEach(star => star.addEventListener("click", () => {
        rating = Number(star.dataset.rating);
        stars.forEach(item => {
            const selected = Number(item.dataset.rating) === rating;
            item.setAttribute("aria-pressed", String(selected));
            item.textContent = Number(item.dataset.rating) <= rating ? "★" : "☆";
        });
    }));
    document.getElementById("submit-rating")?.addEventListener("click", async () => {
        const message = document.getElementById("rating-message");
        message.textContent = "";
        const sessionToken = localStorage.getItem(SESSION_TOKEN_KEY);
        if (!sessionToken) { message.textContent = "Please log in before submitting a rating."; return; }
        if (!rating) { message.textContent = "Please select a star rating."; return; }
        try {
            const result = await api("/ratings", {
                method: "POST",
                body: JSON.stringify({ stars: rating, comment: document.getElementById("rating-comment").value })
            });
            message.textContent = `${result.message} Thank you for visiting!`;
            document.getElementById("submit-rating").disabled = true;
            clearSession();
            setTimeout(() => { window.location.href = `${ROOT}index.html`; }, 2500);
        } catch (error) {
            message.textContent = error.message;
        }
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
    if (activePage && !localStorage.getItem(SESSION_TOKEN_KEY)) {
        window.location.replace(`${ROOT}index.html`);
        return;
    }
    if (activePage) {
        document.querySelectorAll(".navigation .nav-link").forEach(link => {
            link.classList.toggle("active", link.getAttribute("href") === activePage);
        });
    }
    const customerName = localStorage.getItem(CUSTOMER_NAME_KEY);
    document.querySelectorAll(".sidebar-welcome").forEach(node => {
        node.textContent = customerName ? `Welcome, ${customerName}` : "Welcome to the cafe";
    });
    if (document.getElementById("items-content")) {
        api("/menu").then(items => renderCatalogue("items-content", items, true))
            .catch(error => showCatalogueError("items-content", error));
    }
    if (document.getElementById("books-content")) {
        api("/books").then(books => renderCatalogue("books-content", books))
            .catch(error => showCatalogueError("books-content", error));
    }
    renderBill();
    updateCartCount();
    initializeLogin();
    initializeRating();
    initializeExitLinks();
}

document.addEventListener("DOMContentLoaded", initializePage);
