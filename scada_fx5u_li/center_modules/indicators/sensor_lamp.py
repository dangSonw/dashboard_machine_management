class SensorLamp:

    def __init__(self, canvas, x, y, label):

        self.canvas = canvas

        font_size = 12
        r = 20

        # ===== LAMP =====
        self.lamp = canvas.create_oval(
            x-r, y-r,
            x+r, y+r,
            fill="#222222"   # tắt = xám đậm
        )

        # ===== TEXT =====
        self.text = canvas.create_text(
            x,
            y+40,
            text=label,
            font=("Arial", font_size, "bold")
        )

    # ================= UPDATE =================
    def update(self, state):

        color = "#facc15" if state else "#444444"  # vàng khi ON

        self.canvas.itemconfig(
            self.lamp,
            fill=color
        )