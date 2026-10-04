"""Margins & Mugs: a small Tkinter cafe and bookshop ordering app.

Put this file beside an ``assets`` folder containing the image files listed
in ``MENU_ITEMS`` and ``BOOKS`` below. Images are optional; the app shows a
text placeholder when an image is missing.

Dependency: Pillow (``python -m pip install Pillow``)
"""

from __future__ import annotations

import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError as exc:
    raise SystemExit(
        "This app needs Pillow. Install it with: python -m pip install Pillow"
    ) from exc


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

BG = "#101814"
PANEL = "#16251b"
CARD = "#203126"
GREEN = "#176b36"
LIGHT_GREEN = "#a9d5ad"
GOLD = "#ffd966"
WHITE = "#f5f5ee"
MUTED = "#bdc8bf"


# Each image filename should be placed in the assets folder. Names are kept
# from the source PDF so existing image collections can be copied over easily.
MENU_ITEMS = [
    ("Hot Beverages", "ESPRESSO", 90, "esp.jpg"),
    ("Hot Beverages", "MASALA TEA", 40, "tea.jpg"),
    ("Hot Beverages", "AMERICANO", 120, "americano.jpg"),
    ("Hot Beverages", "CAPPUCCINO", 150, "cappuccino.jpg"),
    ("Hot Beverages", "MOCHA", 170, "mocha.jpg"),
    ("Hot Beverages", "ICED LATTE", 180, "latte.jpg"),
    ("Hot Beverages", "HOT CHOCOLATE", 160, "hot.jpeg"),
    ("Desserts & Bakes", "BUTTER CROISSANT", 70, "91.jpg"),
    ("Desserts & Bakes", "CHOCOLATE MUFFIN", 80, "92.jpg"),
    ("Desserts & Bakes", "WAFFLE WITH SAUCE", 140, "93.jpg"),
    ("Desserts & Bakes", "BLUEBERRY CHEESECAKE", 160, "96.jpg"),
    ("Desserts & Bakes", "CHOCOLATE SWISS ROLL", 120, "95.jpg"),
    ("Desserts & Bakes", "ICE CREAM SUNDAE", 130, "94.jpg"),
    ("Desserts & Bakes", "FRUIT CAKE (SLICE)", 100, "97.jpg"),
    ("Snacks & Spicy Items", "GRILLED VEG SANDWICH", 90, "81.jpg"),
    ("Snacks & Spicy Items", "VEG PUFF", 50, "82.jpg"),
    ("Snacks & Spicy Items", "SPICY HAKKA NOODLES", 120, "83.jpg"),
    ("Snacks & Spicy Items", "MASALA FRIES", 100, "84.jpg"),
    ("Snacks & Spicy Items", "CHEESE CORN TOAST", 90, "85.jpg"),
    ("Snacks & Spicy Items", "PASTA", 140, "86.jpg"),
    ("Snacks & Spicy Items", "VEG MOMOS", 110, "87.jpg"),
]

BOOKS = [   
    ("General Fiction", "A SHIMLA AFFAIR", "11.jpg"),
    ("General Fiction", "MARROW", "16.jpg"),
    ("General Fiction", "BUTCHER & BLACKBIRD", "17.jpeg"),
    ("General Fiction", "KING OF ENVY", "13.jpg"),
    ("General Fiction", "GOD OF WAR", "15.jpg"),
    ("General Fiction", "DAYS AT THE TORUNKA CAFE", "12.jpg"),
    ("General Fiction", "SHATTER ME", "14.jpg"),
    ("Non-Fiction", "THE METAMORPHOSIS", "31.jpg"),
    ("Non-Fiction", "PRIDE AND PREJUDICE", "36.jpg"),
    ("Non-Fiction", "ANIMAL FARM", "32.jpg"),
    ("Non-Fiction", "WHITE NIGHTS", "37.jpg"),
    ("Non-Fiction", "NORWEGIAN WOOD", "33.jpg"),
    ("Non-Fiction", "CRIME AND PUNISHMENT", "35.jpg"),
    ("Non-Fiction", "THE BELL JAR", "34.jpg"),
    ("Thrillers", "HOW TO KILL MEN AND GET AWAY WITH IT", "21.jpeg"),
    ("Thrillers", "SHARP OBJECTS", "22.jpg"),
    ("Thrillers", "NONE OF THIS IS TRUE", "23.jpg"),
    ("Thrillers", "THE FAVOURITE GIRL", "27.jpg"),
    ("Thrillers", "THE FAMILY UPSTAIRS", "25.jpg"),
    ("Thrillers", "ROCK PAPER SCISSORS", "26.jpg"),
    ("Thrillers", "NEVER LIE", "24.jpg"),
]


class MarginsAndMugsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Margins & Mugs")
        self.root.configure(bg=BG)
        self.root.state("zoomed")
        self.root.minsize(800, 600)
        self.customer_name = ""
        self.cart: dict[str, dict[str, int]] = {}
        self.photo_cache: dict[tuple[str, tuple[int, int]], ImageTk.PhotoImage] = {}
        self._configure_styles()
        self._show_login()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=WHITE, font=("Arial", 11))
        style.configure("Title.TLabel", font=("Arial", 28, "bold"), foreground=GOLD)
        style.configure("Section.TLabel", font=("Arial", 16, "bold"), foreground=LIGHT_GREEN)
        style.configure("TButton", font=("Arial", 11, "bold"), padding=8)
        style.configure("Green.TButton", background=GREEN, foreground=WHITE)
        style.map("Green.TButton", background=[("active", "#218a49")])
        style.configure("TEntry", padding=7)

    def _show_login(self) -> None:
        self._clear_root()
        outer = ttk.Frame(self.root, padding=30)
        outer.pack(expand=True)
        ttk.Label(outer, text="WELCOME TO", style="Section.TLabel").pack(pady=(0, 8))
        ttk.Label(outer, text="MARGINS & MUGS", style="Title.TLabel").pack(pady=(0, 28))
        form = tk.Frame(outer, bg=PANEL, padx=30, pady=26)
        form.pack()
        tk.Label(form, text="Your name", bg=PANEL, fg=WHITE, font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.name_entry = ttk.Entry(form, width=32)
        self.name_entry.grid(row=0, column=1, padx=(18, 0), pady=8)
        tk.Label(form, text="Phone number", bg=PANEL, fg=WHITE, font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.phone_entry = ttk.Entry(form, width=32)
        self.phone_entry.grid(row=1, column=1, padx=(18, 0), pady=8)
        ttk.Button(form, text="Enter", style="Green.TButton", command=self._enter_app).grid(
            row=2, column=0, columnspan=2, pady=(18, 0)
        )
        self.name_entry.focus_set()
        self.root.bind("<Return>", lambda _event: self._enter_app())

    def _enter_app(self) -> None:
        name = self.name_entry.get().strip()
        phone = re.sub(r"[\s()+-]", "", self.phone_entry.get())
        if not name:
            messagebox.showerror("Missing name", "Please enter your name.", parent=self.root)
            return
        if not phone.isdigit() or not 7 <= len(phone) <= 15:
            messagebox.showerror("Invalid phone number", "Enter a phone number containing 7 to 15 digits.", parent=self.root)
            return
        self.customer_name = name
        self.root.unbind("<Return>")
        self._show_main()
        self.show_menu()

    def _show_main(self) -> None:
        self._clear_root()
        self.root.title("Margins & Mugs | Cafe and Books")
        shell = ttk.Frame(self.root)
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg=PANEL, width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="MARGINS\n& MUGS", bg=PANEL, fg=GOLD,
                 font=("Arial", 19, "bold"), justify="center").pack(pady=(24, 20))
        for label, action in [
            ("Menu", self.show_menu),
            ("Books", self.show_books),
            ("Your Order", self.show_bill),
            ("About", self.show_about),
            ("Exit", self.show_rating),
        ]:
            tk.Button(sidebar, text=label, command=action, bg=GREEN, fg=WHITE,
                      activebackground="#218a49", activeforeground=WHITE,
                      font=("Arial", 12, "bold"), relief="flat", padx=12, pady=12).pack(
                          fill="x", padx=14, pady=6
                      )
        tk.Label(sidebar, text=f"Welcome, {self.customer_name}", bg=PANEL,
                 fg=MUTED, wraplength=155, font=("Arial", 10)).pack(side="bottom", pady=18)
        self.content = tk.Frame(shell, bg=BG)
        self.content.pack(side="right", fill="both", expand=True)

    def _clear_content(self) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

    def _clear_root(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

    def _heading(self, title: str, subtitle: str = "") -> None:
        tk.Label(self.content, text=title, bg=BG, fg=GOLD,
                 font=("Arial", 23, "bold")).pack(anchor="w", padx=26, pady=(22, 3))
        if subtitle:
            tk.Label(self.content, text=subtitle, bg=BG, fg=MUTED,
                     font=("Arial", 11)).pack(anchor="w", padx=28, pady=(0, 12))

    def _scroll_area(self) -> tuple[tk.Canvas, tk.Frame]:
        wrapper = tk.Frame(self.content, bg=BG)
        wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        canvas = tk.Canvas(wrapper, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=BG)
        body.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(canvas_window, width=event.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(-1 * (event.delta // 120), "units"))
        return canvas, body

    def show_books(self) -> None:
        self._clear_content()
        self._heading("Books Available", "Browse the books on the cafe shelves.")
        _, body = self._scroll_area()
        for category in ("General Fiction", "Non-Fiction", "Thrillers"):
            tk.Label(body, text=category, bg=BG, fg=LIGHT_GREEN,
                     font=("Arial", 15, "bold")).pack(anchor="w", padx=8, pady=(14, 2))
            row = tk.Frame(body, bg=BG)
            row.pack(anchor="w", fill="x")
            for column in range(4):
                row.grid_columnconfigure(column, weight=1)
            for cat, name, filename in BOOKS:
                if cat == category:
                    self._make_card(row, name, filename)

    def show_bill(self) -> None:
        self._clear_content()
        self._heading("Your Order", "Review your selected items before placing the order.")
        if not self.cart:
            tk.Label(self.content, text="Your cart is empty. Add something from the menu!",
                     bg=BG, fg=WHITE, font=("Arial", 14)).pack(pady=40)
            return
        table = tk.Frame(self.content, bg=PANEL, padx=18, pady=16)
        table.pack(fill="x", padx=30, pady=12)
        total = 0
        for row, (name, data) in enumerate(self.cart.items()):
            amount = data["price"] * data["qty"]
            total += amount
            tk.Label(table, text=name, bg=PANEL, fg=WHITE, anchor="w",
                     font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=8, pady=7)
            tk.Label(table, text=f"× {data['qty']}", bg=PANEL, fg=WHITE,
                     font=("Arial", 12)).grid(row=row, column=1, padx=20, pady=7)
            tk.Label(table, text=f"₹{amount}", bg=PANEL, fg=WHITE, anchor="e",
                     font=("Arial", 12, "bold")).grid(row=row, column=2, sticky="e", padx=8, pady=7)
        tk.Label(self.content, text=f"Total: ₹{total}", bg=BG, fg=GOLD,
                 font=("Arial", 20, "bold")).pack(anchor="e", padx=40, pady=15)
        ttk.Button(self.content, text="Place Order", style="Green.TButton",
                   command=self._place_order).pack(anchor="e", padx=40)

    def _place_order(self) -> None:
        messagebox.showinfo("Order placed", f"Thank you, {self.customer_name}! Your order has been placed.", parent=self.root)
        self.cart.clear()
        self.show_bill()

    def show_about(self) -> None:
        self._clear_content()
        self._heading("About Margins & Mugs")
        box = tk.Frame(self.content, bg=PANEL, padx=28, pady=24)
        box.pack(fill="both", expand=True, padx=30, pady=12)
        description = (
            "Margins & Mugs brings a cafe and a bookshop together. Browse the menu, "
            "look through the books, add food and drinks to your cart, and review a clear bill.\n\n"
            "Features\n"
            "• Interactive menu and book catalogue\n"
            "• Quantity-based ordering\n"
            "• Automatic bill calculation\n"
            "• Customer greeting and experience rating\n\n"
            "Project team\nShaalika · Shambhavi · Shreya · Spoorthy"
        )
        tk.Label(box, text=description, bg=PANEL, fg=WHITE, justify="left",
                 anchor="nw", font=("Arial", 13), wraplength=800).pack(fill="both", expand=True)

    def show_rating(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Rate Margins & Mugs")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Enjoy your margins with your mug!",
                 bg=BG, fg=GOLD, font=("Arial", 15, "bold")).pack(padx=24, pady=(24, 10))
        tk.Label(dialog, text="Rate your experience", bg=BG, fg=WHITE,
                 font=("Arial", 12)).pack()
        rating = tk.IntVar(value=0)
        stars = tk.Frame(dialog, bg=BG)
        stars.pack(pady=10)
        star_buttons: list[tk.Button] = []

        def choose(value: int) -> None:
            rating.set(value)
            for index, button in enumerate(star_buttons, start=1):
                button.configure(text="★" if index <= value else "☆")

        for value in range(1, 6):
            button = tk.Button(stars, text="☆", font=("Arial", 24), bg=BG, fg=GOLD,
                               relief="flat", command=lambda v=value: choose(v))
            button.pack(side="left", padx=3)
            star_buttons.append(button)

        def submit() -> None:
            if rating.get() == 0:
                messagebox.showwarning("Rating required", "Please select a star rating.", parent=dialog)
                return
            dialog.destroy()
            self.root.destroy()

        ttk.Button(dialog, text="Submit and Exit", style="Green.TButton", command=submit).pack(pady=(4, 22))
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)


def main() -> None:
    root = tk.Tk()
    MarginsAndMugsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()