import datetime as dt
import random
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

DB_PATH = "weightbridge.db"


class WeightBridgeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WeightBridge Pro")
        self.geometry("1280x760")
        self.configure(bg="#111827")

        self.conn = sqlite3.connect(DB_PATH)
        self._init_db()

        self.scale_value = tk.DoubleVar(value=350.0)
        self.mode_value = tk.StringVar(value="Manual")
        self.ticket_no = tk.StringVar(value=self._next_ticket())
        self.vehicle_no = tk.StringVar()
        self.client_name = tk.StringVar()
        self.material = tk.StringVar()
        self.remarks = tk.StringVar()
        self.first_weight = tk.DoubleVar(value=0.0)
        self.second_weight = tk.DoubleVar(value=0.0)

        self._configure_style()
        self._build_layout()
        self._refresh_grid()
        self._update_clock()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background="#111827")
        style.configure("Card.TFrame", background="#172033", relief="flat")
        style.configure("Header.TLabel", background="#172033", foreground="#f8fafc", font=("Segoe UI", 12, "bold"))
        style.configure("Body.TLabel", background="#172033", foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure("Scale.TLabel", background="#101827", foreground="#4ade80", font=("Segoe UI", 52, "bold"))
        style.configure("Value.TLabel", background="#172033", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        style.configure("Small.TLabel", background="#172033", foreground="#94a3b8", font=("Segoe UI", 10))
        style.configure("Card.TLabelframe", background="#172033", borderwidth=1, relief="solid", bordercolor="#2a3447")
        style.configure("Card.TLabelframe.Label", background="#172033", foreground="#f8fafc", font=("Segoe UI", 11, "bold"))

        style.configure("Blue.TButton", background="#2563eb", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Blue.TButton", background=[("active", "#1d4ed8")])
        style.configure("Green.TButton", background="#16a34a", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Green.TButton", background=[("active", "#15803d")])
        style.configure("Danger.TButton", background="#ef4444", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#dc2626")])
        style.configure("Neutral.TButton", background="#334155", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)

        style.configure("Dark.Treeview", background="#0b1220", fieldbackground="#0b1220", foreground="#e2e8f0", rowheight=28, bordercolor="#2a3447", borderwidth=1)
        style.configure("Dark.Treeview.Heading", background="#1e293b", foreground="#f8fafc", font=("Segoe UI", 10, "bold"))
        style.map("Dark.Treeview", background=[("selected", "#1d4ed8")])

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)

        header = ttk.Frame(self, style="Card.TFrame", padding=(16, 12))
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 8))
        ttk.Label(header, text="WeightBridge Pro", style="Header.TLabel").pack(side="left")
        self.clock_label = ttk.Label(header, text="", style="Body.TLabel")
        self.clock_label.pack(side="left", padx=18)
        ttk.Label(header, text="Operator: ADMIN", style="Body.TLabel").pack(side="right")

        left = ttk.Frame(self, style="TFrame")
        left.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        right = ttk.Frame(self, style="TFrame")
        right.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 12))
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self._build_scale_card(left)
        self._build_entry_card(left)
        self._build_transactions_card(right)

    def _build_scale_card(self, parent):
        card = ttk.LabelFrame(parent, text="Live Scale", style="Card.TLabelframe", padding=12)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        card.grid_columnconfigure(0, weight=1)

        mode_line = ttk.Frame(card, style="Card.TFrame")
        mode_line.grid(row=0, column=0, sticky="w")
        ttk.Label(mode_line, text="●", foreground="#60a5fa", background="#172033").pack(side="left")
        ttk.Label(mode_line, textvariable=self.mode_value, style="Body.TLabel").pack(side="left", padx=(8, 0))

        scale_box = tk.Frame(card, bg="#101827", highlightbackground="#2a3447", highlightthickness=1)
        scale_box.grid(row=1, column=0, sticky="ew", pady=12)
        self.scale_label = ttk.Label(scale_box, text=f"{self.scale_value.get():.1f}", style="Scale.TLabel")
        self.scale_label.pack(pady=(16, 4))
        ttk.Label(scale_box, text="kg", style="Body.TLabel").pack()
        self.ton_label = ttk.Label(scale_box, text="0.350 ton", style="Small.TLabel")
        self.ton_label.pack(pady=(2, 14))

        ttk.Label(card, text="Simulate Scale (kg)", style="Small.TLabel").grid(row=2, column=0, sticky="w")
        slider = ttk.Scale(card, from_=0, to=60000, variable=self.scale_value, command=self._on_scale_change)
        slider.grid(row=3, column=0, sticky="ew", pady=(3, 8))

        quick = ttk.Frame(card, style="Card.TFrame")
        quick.grid(row=4, column=0, sticky="w", pady=(0, 8))
        for val in [5000, 10000, 20000, 40000, 60000]:
            ttk.Button(quick, text=f"{int(val/1000)}T", style="Neutral.TButton", command=lambda v=val: self._set_scale(v)).pack(side="left", padx=(0, 6))

        manual_frame = ttk.Frame(card, style="Card.TFrame")
        manual_frame.grid(row=5, column=0, sticky="w")
        self.manual_entry = ttk.Entry(manual_frame, width=12)
        self.manual_entry.insert(0, "350")
        self.manual_entry.pack(side="left", padx=(0, 8))
        ttk.Button(manual_frame, text="Set Manual", style="Blue.TButton", command=self._manual_set).pack(side="left")

    def _build_entry_card(self, parent):
        card = ttk.LabelFrame(parent, text="Weighment Entry", style="Card.TLabelframe", padding=12)
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(3, weight=1)

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        ttk.Button(actions, text="1st Weight", style="Neutral.TButton", command=self._capture_first).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="2nd Weight", style="Danger.TButton", command=self._capture_second).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Save", style="Green.TButton", command=self._save_ticket).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="New", style="Blue.TButton", command=self._new_ticket).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Print", style="Neutral.TButton", command=self._print_ticket).pack(side="left")

        self._add_field(card, "Ticket No", self.ticket_no, 1, 0)
        self._add_field(card, "Vehicle No *", self.vehicle_no, 1, 2)
        self._add_field(card, "Client Name", self.client_name, 2, 0)
        self._add_field(card, "Material *", self.material, 2, 2)
        self._add_field(card, "Remarks", self.remarks, 3, 0, span=3)

        stats = ttk.Frame(card, style="Card.TFrame")
        stats.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(14, 0))
        for i in range(4):
            stats.grid_columnconfigure(i, weight=1)

        self.first_label = self._stat_box(stats, "1st Wt", "0 kg", 0)
        self.second_label = self._stat_box(stats, "2nd Wt", "0 kg", 1)
        self.net_label = self._stat_box(stats, "Net Wt", "0 kg\n0.000 t", 2)
        self.munds_label = self._stat_box(stats, "Munds (@40kg)", "0", 3)

    def _build_transactions_card(self, parent):
        card = ttk.LabelFrame(parent, text="Today's Transactions", style="Card.TLabelframe", padding=12)
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        controls = ttk.Frame(card, style="Card.TFrame")
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.search_var = tk.StringVar()
        search = ttk.Entry(controls, textvariable=self.search_var)
        search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        search.bind("<KeyRelease>", lambda _e: self._refresh_grid())
        ttk.Button(controls, text="All", style="Blue.TButton", command=self._refresh_grid).pack(side="left", padx=(0, 4))

        cols = ("ticket", "vehicle", "material", "tare", "gross", "net", "time")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", style="Dark.Treeview")
        for c, title, w in [
            ("ticket", "Ticket", 100),
            ("vehicle", "Vehicle", 110),
            ("material", "Material", 130),
            ("tare", "Tare kg", 95),
            ("gross", "Gross kg", 95),
            ("net", "Net kg", 95),
            ("time", "Time", 130),
        ]:
            self.tree.heading(c, text=title)
            self.tree.column(c, width=w, anchor="center")

        self.tree.grid(row=1, column=0, sticky="nsew")
        scr = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scr.set)
        scr.grid(row=1, column=1, sticky="ns")

    def _add_field(self, parent, label, var, row, col, span=1):
        ttk.Label(parent, text=label, style="Small.TLabel").grid(row=row, column=col, sticky="w", pady=4)
        state = "readonly" if label == "Ticket No" else "normal"
        ttk.Entry(parent, textvariable=var, state=state).grid(row=row, column=col + 1, columnspan=span, sticky="ew", padx=(8, 14), pady=4)

    def _stat_box(self, parent, title, value, col):
        box = tk.Frame(parent, bg="#0f172a", highlightbackground="#22c55e", highlightthickness=1)
        box.grid(row=0, column=col, sticky="ew", padx=(0, 8))
        tk.Label(box, text=title, bg="#0f172a", fg="#60a5fa", font=("Segoe UI", 9, "bold")).pack(pady=(8, 4))
        label = tk.Label(box, text=value, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 18, "bold"))
        label.pack(pady=(0, 8))
        return label

    def _on_scale_change(self, _value=None):
        value = round(self.scale_value.get(), 1)
        self.scale_label.configure(text=f"{value:.1f}")
        self.ton_label.configure(text=f"{value/1000:.3f} ton")

    def _set_scale(self, value):
        self.scale_value.set(value)
        self._on_scale_change()

    def _manual_set(self):
        try:
            value = float(self.manual_entry.get())
        except ValueError:
            messagebox.showerror("Invalid", "Enter a numeric weight.")
            return
        self._set_scale(value)

    def _capture_first(self):
        self.first_weight.set(self.scale_value.get())
        self.first_label.configure(text=f"{self.first_weight.get():.0f} kg")
        self._refresh_net()

    def _capture_second(self):
        self.second_weight.set(self.scale_value.get())
        self.second_label.configure(text=f"{self.second_weight.get():.0f} kg")
        self._refresh_net()

    def _refresh_net(self):
        net = abs(self.first_weight.get() - self.second_weight.get())
        self.net_label.configure(text=f"{net:.0f} kg\n{net/1000:.3f} t")
        self.munds_label.configure(text=f"{net/40:.1f}")

    def _next_ticket(self):
        row = self.conn.execute("SELECT COUNT(*) FROM tickets").fetchone()
        return f"WB-{row[0] + 1:05d}"

    def _save_ticket(self):
        if not self.vehicle_no.get().strip() or not self.material.get().strip():
            messagebox.showwarning("Required", "Vehicle No and Material are required.")
            return

        first = self.first_weight.get()
        second = self.second_weight.get()
        net = abs(first - second)
        tare = min(first, second)
        gross = max(first, second)
        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.conn.execute(
            """
            INSERT INTO tickets(ticket_no, vehicle_no, client_name, material, remarks, tare_kg, gross_kg, net_kg, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.ticket_no.get(),
                self.vehicle_no.get().strip(),
                self.client_name.get().strip(),
                self.material.get().strip(),
                self.remarks.get().strip(),
                tare,
                gross,
                net,
                now,
            ),
        )
        self.conn.commit()
        self._refresh_grid()
        messagebox.showinfo("Saved", "Ticket saved successfully.")
        self._new_ticket(keep_messages=False)

    def _print_ticket(self):
        messagebox.showinfo("Printing", "Ticket sent to Microsoft Print to PDF")

    def _new_ticket(self, keep_messages=True):
        self.ticket_no.set(self._next_ticket())
        self.vehicle_no.set("")
        self.client_name.set("")
        self.material.set("")
        self.remarks.set("")
        self.first_weight.set(0)
        self.second_weight.set(0)
        self.first_label.configure(text="0 kg")
        self.second_label.configure(text="0 kg")
        self._refresh_net()
        if keep_messages:
            messagebox.showinfo("New", "Ready for next ticket.")

    def _refresh_grid(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        q = self.search_var.get().strip()
        if q:
            rows = self.conn.execute(
                """
                SELECT ticket_no, vehicle_no, material, tare_kg, gross_kg, net_kg, created_at
                FROM tickets
                WHERE ticket_no LIKE ? OR vehicle_no LIKE ? OR material LIKE ?
                ORDER BY id DESC
                """,
                (f"%{q}%", f"%{q}%", f"%{q}%"),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT ticket_no, vehicle_no, material, tare_kg, gross_kg, net_kg, created_at
                FROM tickets ORDER BY id DESC
                """
            ).fetchall()

        for r in rows:
            self.tree.insert("", "end", values=r)

    def _update_clock(self):
        self.clock_label.configure(text=dt.datetime.now().strftime("%Y-%m-%d   %H:%M:%S"))
        self.after(1000, self._update_clock)

    def _init_db(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_no TEXT NOT NULL,
                vehicle_no TEXT NOT NULL,
                client_name TEXT,
                material TEXT NOT NULL,
                remarks TEXT,
                tare_kg REAL,
                gross_kg REAL,
                net_kg REAL,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()
        count = self.conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        if count == 0:
            for i in range(4):
                first = random.randint(12000, 24000)
                second = random.randint(5000, 15000)
                tare = min(first, second)
                gross = max(first, second)
                self.conn.execute(
                    """
                    INSERT INTO tickets(ticket_no, vehicle_no, client_name, material, remarks, tare_kg, gross_kg, net_kg, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"WB-{i+1:05d}",
                        f"LE-{random.randint(100, 999)}",
                        "Demo Client",
                        random.choice(["Cement", "Sand", "Wood", "Steel"]),
                        "seed",
                        tare,
                        gross,
                        abs(first - second),
                        dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
            self.conn.commit()


if __name__ == "__main__":
    app = WeightBridgeApp()
    app.mainloop()
