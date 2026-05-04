import math


class CarouselRenderer:

    def __init__(self, canvas):
        self.canvas = canvas

    def draw_bolt(self, x, y, size=4):
        c = self.canvas
        c.create_oval(x-size, y-size, x+size, y+size,
                      fill="#9ca3af", outline="#475569", tags="carousel")
        c.create_oval(x-size*0.4, y-size*0.4,
                      x+size*0.4, y+size*0.4,
                      fill="#1e293b", outline="", tags="carousel")

    def draw(self, cx, cy, radius, core):

        canvas = self.canvas
        canvas.delete("carousel")

        rotation = core.get_rotation()

        # =============================
        # MÂM XOAY (KIM LOẠI)
        # =============================
        canvas.create_oval(
            cx-radius, cy-radius,
            cx+radius, cy+radius,
            fill="#d1d5db", outline="#6b7280",
            width=2, tags="carousel"
        )

        # vòng trong
        canvas.create_oval(
            cx-radius+10, cy-radius+10,
            cx+radius-10, cy+radius-10,
            outline="#9ca3af",
            width=2, tags="carousel"
        )

        # =============================
        # BU LÔNG TRUNG TÂM
        # =============================
        for i in range(6):
            angle = math.radians(i * 60 +  - 90)
            bx = cx + 40 * math.cos(angle)
            by = cy + 40 * math.sin(angle)
            self.draw_bolt(bx, by)

        self.draw_bolt(cx, cy, 5)

        # =============================
        # 6 TẤM STATION (GIỐNG MÁY THẬT)
        # =============================
        for i, sensor in enumerate(core.sensors):

            angle = (i * 60) + rotation- 90 
            rad = math.radians(angle)

            x = cx + radius * 0.75 * math.cos(rad)
            y = cy + radius * 0.75 * math.sin(rad)

            w, h = 100, 70
            x1, y1 = x-w/2, y-h/2
            x2, y2 = x+w/2, y+h/2

            # tấm nhôm
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#e5e7eb",
                outline="#6b7280",
                width=2,
                tags="carousel"
            )

            # 4 con ốc
            self.draw_bolt(x1+8, y1+8)
            self.draw_bolt(x2-8, y1+8)
            self.draw_bolt(x1+8, y2-8)
            self.draw_bolt(x2-8, y2-8)

            # TEXT
            canvas.create_text(
                x, y-10,
                text=sensor["label"],
                fill="#111827",
                font=("Arial", 9, "bold"),
                tags="carousel"
            )

            canvas.create_text(
                x, y+10,
                text=f"ID:{sensor['id']}",
                fill="#374151",
                font=("Arial", 8),
                tags="carousel"
            )

            # =============================
            # LED (GIỮ NGUYÊN LOGIC)
            # =============================
            r, yel, g = core.get_station_state(i)

            color = "#334155"
            if r:
                color = "#ef4444"
            elif yel:
                color = "#facc15"
            elif g:
                color = "#22c55e"

            canvas.create_oval(
                x-10, y+25,
                x+10, y+45,
                fill=color,
                outline="#111",
                tags="carousel"
            )