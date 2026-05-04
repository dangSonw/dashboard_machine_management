import tkinter as tk

class BarChart(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, height=260, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.defects = [
            ("Thiếu LK", "#e53935"),
            ("Sai vị trí", "#fb8c00"),
            ("Lỗi hàn", "#fdd835"),
            ("Thiếu chân", "#43a047"),
            ("Sai cực", "#1e88e5"),
            ("Mất tem", "#8e24aa")
        ]

    def update_data(self, data):
        self.draw(data)

    def draw(self, data):

        self.canvas.delete("all")

        width = 500
        height = 240

        self.canvas.config(width=width, height=height)

        # ===== TRỤC =====
        x0 = 50   # lề trái
        y0 = 200  # đáy

        # trục Y
        self.canvas.create_line(x0, 30, x0, y0, width=2)

        # trục X
        self.canvas.create_line(x0, y0, width-20, y0, width=2)

        # ===== GIÁ TRỊ MAX =====
        max_val = max(data) if max(data) > 0 else 1

        # ===== VẠCH CHIA TRỤC Y =====
        steps = 5
        for i in range(steps + 1):
            y = y0 - i * (150 / steps)
            val = int(max_val * i / steps)

            # line grid
            self.canvas.create_line(x0-5, y, width-20, y, fill="#eeeeee")

            # label
            self.canvas.create_text(x0-20, y, text=str(val), font=("Arial", 10))

        # ===== VẼ BAR =====
        bar_w = 30
        gap = 25

        for i, (name, color) in enumerate(self.defects):

            value = data[i]

            bar_h = (value / max_val) * 150

            x = x0 + 20 + i * (bar_w + gap)

            # cột
            self.canvas.create_rectangle(
                x,
                y0 - bar_h,
                x + bar_w,
                y0,
                fill=color
            )

            # số trên cột
            self.canvas.create_text(
                x + bar_w / 2,
                y0 - bar_h - 10,
                text=str(value),
                font=("Arial", 10, "bold")
            )

            # label X
            self.canvas.create_text(
                x + bar_w / 2,
                y0 + 15,
                text=name,
                font=("Arial", 9)
            )