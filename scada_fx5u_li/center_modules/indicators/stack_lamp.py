class StackLamp:

    def __init__(self, canvas, x, y):

        self.canvas = canvas

        # ===== CHỈNH CỠ CHỮ Ở ĐÂY =====
        font_size = 12

        r = 20

        self.red = canvas.create_oval(
            x-r, y-r,
            x+r, y+r,
            fill="#550000"
        )

        self.yellow = canvas.create_oval(
            x-r, y+40-r,
            x+r, y+40+r,
            fill="#555000"
        )

        self.green = canvas.create_oval(
            x-r, y+80-r,
            x+r, y+80+r,
            fill="#003300"
        )

        # Label
        self.label = canvas.create_text(
            x,
            y+120,
            text="STACK LAMP",
            font=("Arial", font_size, "bold")
        )

    def update(self, r, y, g):

        self.canvas.itemconfig(
            self.red,
            fill="#ef4444" if r else "#550000"
        )

        self.canvas.itemconfig(
            self.yellow,
            fill="#facc15" if y else "#555000"
        )

        self.canvas.itemconfig(
            self.green,
            fill="#22c55e" if g else "#003300"
        )