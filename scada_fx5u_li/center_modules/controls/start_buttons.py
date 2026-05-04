import tkinter as tk

class StartButton:

    def __init__(self, canvas, x, y, label):

        self.canvas = canvas
        self.x = x
        self.y = y

        # ===== RECT =====
        self.rect = canvas.create_rectangle(
            x-70, y-30,
            x+70, y+30,
            fill="#888888",
            outline=""
        )

        # ===== TEXT =====
        self.text = canvas.create_text(
            x,
            y,
            text=label,
            font=("Arial", 12, "bold"),
            fill="white"
        )

        # ===== HOVER EFFECT =====
        canvas.tag_bind(self.rect, "<Enter>", self.on_enter)
        canvas.tag_bind(self.rect, "<Leave>", self.on_leave)

    # ================= UPDATE MÀU =================
    def update(self, state):
        color = "#22c55e" if state else "#888888"

        self.canvas.itemconfig(self.rect, fill=color)

    # ================= MOVE =================
    def move(self, x, y):

        self.x = x
        self.y = y

        self.canvas.coords(self.rect, x-70, y-30, x+70, y+30)
        self.canvas.coords(self.text, x, y)

    # ================= HOVER =================
    def on_enter(self, event):
        self.canvas.itemconfig(self.rect, outline="#00BFFF", width=2)

    def on_leave(self, event):
        self.canvas.itemconfig(self.rect, outline="", width=1)