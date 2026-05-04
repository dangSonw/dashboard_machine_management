class CameraLamp:

    def __init__(self, canvas, x, y):

        self.canvas = canvas

        # ===== CHỈNH CỠ CHỮ Ở ĐÂY =====
        font_size = 12

        # Body camera
        self.body = canvas.create_rectangle(
            x-70, y-35,
            x+70, y+35,
            fill="#4a4a4a"
        )

        # Lens camera
        self.lens = canvas.create_oval(
            x-20, y-20,
            x+20, y+20,
            fill="black"
        )

        # Text
        self.label = canvas.create_text(
            x,
            y+60,
            text="CAMERA",
            font=("Arial", font_size, "bold")
        )

    def update(self, state):

        color = "#22c55e" if state else "#444444"

        self.canvas.itemconfig(
            self.lens,
            fill=color
        )