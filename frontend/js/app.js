"use strict";

// Cafe menu and book catalogue. Put matching image files in ./assets/.
const MENU_ITEMS = [
    ["Hot Beverages", "ESPRESSO", 90, "esp.jpg"], ["Hot Beverages", "MASALA TEA", 40, "tea.jpg"],
    ["Hot Beverages", "AMERICANO", 120, "americano.jpg"], ["Hot Beverages", "CAPPUCCINO", 150, "cappuccino.jpg"],
    ["Hot Beverages", "MOCHA", 170, "mocha.jpg"], ["Hot Beverages", "ICED LATTE", 180, "latte.jpg"],
    ["Hot Beverages", "HOT CHOCOLATE", 160, "hot.jpeg"], ["Desserts & Bakes", "BUTTER CROISSANT", 70, "91.jpg"],
    ["Desserts & Bakes", "CHOCOLATE MUFFIN", 80, "92.jpg"], ["Desserts & Bakes", "WAFFLE WITH SAUCE", 140, "93.jpg"],
    ["Desserts & Bakes", "BLUEBERRY CHEESECAKE", 160, "96.jpg"], ["Desserts & Bakes", "CHOCOLATE SWISS ROLL", 120, "95.jpg"],
    ["Desserts & Bakes", "ICE CREAM SUNDAE", 130, "94.jpg"], ["Desserts & Bakes", "FRUIT CAKE (SLICE)", 100, "97.jpg"],
    ["Snacks & Spicy Items", "GRILLED VEG SANDWICH", 90, "81.jpg"], ["Snacks & Spicy Items", "VEG PUFF", 50, "82.jpg"],
    ["Snacks & Spicy Items", "SPICY HAKKA NOODLES", 120, "83.jpg"], ["Snacks & Spicy Items", "MASALA FRIES", 100, "84.jpg"],
    ["Snacks & Spicy Items", "CHEESE CORN TOAST", 90, "85.jpg"], ["Snacks & Spicy Items", "PASTA", 140, "86.jpg"],
    ["Snacks & Spicy Items", "VEG MOMOS", 110, "87.jpg"]
];

const BOOKS = [
    ["General Fiction", "A SHIMLA AFFAIR", "11.jpg"], ["General Fiction", "MARROW", "16.jpg"],
    ["General Fiction", "BUTCHER & BLACKBIRD", "17.jpeg"], ["General Fiction", "KING OF ENVY", "13.jpg"],
    ["General Fiction", "GOD OF WAR", "15.jpg"], ["General Fiction", "DAYS AT THE TORUNKA CAFE", "12.jpg"],
    ["General Fiction", "SHATTER ME", "14.jpg"], ["Non-Fiction", "THE METAMORPHOSIS", "31.jpg"],
    ["Non-Fiction", "PRIDE AND PREJUDICE", "36.jpg"], ["Non-Fiction", "ANIMAL FARM", "32.jpg"],
    ["Non-Fiction", "WHITE NIGHTS", "37.jpg"], ["Non-Fiction", "NORWEGIAN WOOD", "33.jpg"],
    ["Non-Fiction", "CRIME AND PUNISHMENT", "35.jpg"], ["Non-Fiction", "THE BELL JAR", "34.jpg"],
    ["Thrillers", "HOW TO KILL MEN AND GET AWAY WITH IT", "21.jpeg"], ["Thrillers", "SHARP OBJECTS", "22.jpg"],
    ["Thrillers", "NONE OF THIS IS TRUE", "23.jpg"], ["Thrillers", "THE FAVOURITE GIRL", "27.jpg"],
    ["Thrillers", "THE FAMILY UPSTAIRS", "25.jpg"], ["Thrillers", "ROCK PAPER SCISSORS", "26.jpg"],
    ["Thrillers", "NEVER LIE", "24.jpg"]
];

const CART_KEY = "margins-and-mugs-cart";
const CUSTOMER_KEY = "margins-and-mugs-customer";
const money = amount => `₹${amount}`;
const slug = value => value.toLowerCase().replace(/[^a-z0-9]+/g, "-");

function readCart() {
    try { return JSON.parse(localStorage.getItem(CART_KEY) || "{}"); }
    catch { return {}; }
}

function saveCart(cart) { localStorage.setItem(CART_KEY, JSON.stringify(cart)); }

function makeCard(name, filename, price = null) {
    const card = document.createElement("article");
    card.className = "card";
    const imageBox = document.createElement("div");
    imageBox.className = "card-image";
    const image = document.createElement("img");
    image.src = `assets/${filename}`;
    image.alt = name;
    image.loading = "lazy";
    image.onerror = () => { imageBox.textContent = "Image not found"; };
    imageBox.append(image);
    const title = document.createElement("h3");
    title.textContent = name;
    card.append(imageBox, title);

    if (price !== null) {
        const priceLabel = document.createElement("p");
        priceLabel.className = "price";
        priceLabel.textContent = money(price);
        const controls = document.createElement("div");
        controls.className = "quantity";
        const remove = document.createElement("button");
        remove.type = "button";
        remove.textContent = "−";
        remove.setAttribute("aria-label", `Remove one ${name}`);
        const count = document.createElement("output");
        count.id = `qty-${slug(name)}`;
        count.textContent = readCart()[name]?.qty || 0;
        const add = document.createElement("button");
        add.type = "button";
        add.textContent = "+";
        add.setAttribute("aria-label", `Add one ${name}`);
        remove.addEventListener("click", () => changeQuantity(name, price, -1));
        add.addEventListener("click", () => changeQuantity(name, price, 1));
        controls.append(remove, count, add);
        card.append(priceLabel, controls);
    }
    return card;
}

function renderCatalogue(containerId, data, categories, isMenu) {
    const root = document.getElementById(containerId);
    if (!root) return;
    categories.forEach(category => {
        const heading = document.createElement("h2");
        heading.className = "category";
        heading.textContent = category;
        const cards = document.createElement("div");
        cards.className = "cards";
        data.filter(item => item[0] === category).forEach(item => {
            cards.append(makeCard(item[1], isMenu ? item[3] : item[2], isMenu ? item[2] : null));
        });
        root.append(heading, cards);
    });
}

function changeQuantity(name, price, change) {
    const cart = readCart();
    const quantity = Math.max(0, (cart[name]?.qty || 0) + change);
    if (quantity) cart[name] = { price, qty: quantity };
    else delete cart[name];
    saveCart(cart);
    const count = document.getElementById(`qty-${slug(name)}`);
    if (count) count.textContent = quantity;
    renderOrder();
    updateCartCount();
}
function updateCartCount() {
    const cart = readCart();
    const count = Object.values(cart).reduce((sum, item) => sum + item.qty, 0);
    document.querySelectorAll(".cart-count").forEach(element => {
        element.textContent = count ? `(${count})` : "";
    });
}

function renderOrder() {
    const target = document.getElementById("order-content");
    if (!target) return;
    target.replaceChildren();
    const cart = readCart();
    const names = Object.keys(cart);
    if (!names.length) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "Your cart is empty. Browse the menu to add something!";
        target.append(empty);
        return;
    }
    const bill = document.createElement("div");
    bill.className = "bill";
    let total = 0;
    names.forEach(name => {
        const item = cart[name];
        const amount = item.price * item.qty;
        total += amount;
        const row = document.createElement("div");
        row.className = "bill-row";
        const title = document.createElement("span"); title.textContent = name;
        const quantity = document.createElement("span"); quantity.textContent = `× ${item.qty}`;
        const subtotal = document.createElement("strong"); subtotal.textContent = money(amount);
        row.append(title, quantity, subtotal);
        bill.append(row);
    });
    const totalLabel = document.createElement("p");
    totalLabel.className = "bill-total";
    totalLabel.textContent = `Total: ${money(total)}`;
    const placeOrder = document.createElement("button");
    placeOrder.className = "button button-primary";
    placeOrder.textContent = "Place Order";
    placeOrder.addEventListener("click", () => {
        const customer = localStorage.getItem(CUSTOMER_KEY) || "there";
        window.alert(`Thank you, ${customer}! Your order for ${money(total)} has been placed.`);
        localStorage.removeItem(CART_KEY);
        renderOrder();
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
        window.location.href = "items.html";
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
        window.location.href = "about.html#rating";
    }));
    if (window.location.hash === "#exit") window.location.href = "about.html#rating";
}

function initializePage() {
    const customer = localStorage.getItem(CUSTOMER_KEY);
    document.querySelectorAll(".sidebar-welcome").forEach(element => {
        element.textContent = customer ? `Welcome, ${customer}` : "Welcome to the cafe";
    });
    renderCatalogue("items-content", MENU_ITEMS,
        ["Hot Beverages", "Desserts & Bakes", "Snacks & Spicy Items"], true);
    renderCatalogue("books-content", BOOKS,
        ["General Fiction", "Non-Fiction", "Thrillers"], false);
    renderOrder();
    updateCartCount();
    initializeLogin();
    initializeRating();
    initializeExitLinks();
}

document.addEventListener("DOMContentLoaded", initializePage);
