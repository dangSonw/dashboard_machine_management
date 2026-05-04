import tkinter as tk
import random
import plc_comm


class ErrorButtons(tk.Frame):

    def __init__(self, parent):

        BG = "#d9d9d9"
        super().__init__(parent, bg=BG)

        self.errors = [
            "LỖI SERVO",
            "LỖI PLC",
            "LỖI CAMERA",
            "LỖI CẢM BIẾN",
            "LỖI KẾT NỐI HMI",
            "LỖI KẾT NỐI WEBSERVER"
        ]

        self.indicators = {}

        # ===== UI =====
        for i, text in enumerate(self.errors):

            r = i % 2
            c = i // 2

            row = tk.Frame(self, bg=BG)
            row.grid(row=r, column=c, sticky="w", padx=20, pady=8)

            lamp = tk.Canvas(row, width=32, height=32,
                             highlightthickness=0, bg=BG)
            lamp.pack(side="left", padx=6)

            circle = lamp.create_oval(
                4, 4, 28, 28,
                fill="#7a7a7a",
                outline=""
            )

            label = tk.Label(
                row,
                text=text,
                font=("Arial", 13, "bold"),
                anchor="w",
                bg=BG
            )
            label.pack(side="left")

            self.indicators[text] = (lamp, circle)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # 🔥 LOOP UPDATE
        self.after(500, self.update_auto)

    # ==============================
    # 🔥 ĐỌC BIT PLC
    # ==============================
    def get_bit(self, name):

        bits = getattr(plc_comm, "latest_bits", [])

        if not bits:
            return False

        try:
            if name.startswith("M"):
                m_index = int(name[1:])
                offset = m_index - 900

                if 0 <= offset < len(bits):
                    return bits[offset]

        except Exception as e:
            print("GET BIT ERROR:", e)

        return False

    # ==============================
    # 🔥 UPDATE AUTO
    # ==============================
    def update_auto(self):

        try:
            run = self.get_bit("M916")   # RUN (Y16)
            stop = self.get_bit("M917") # STOP (Y17)

            # ===== CASE 1: RUN =====
            if run:
                for lamp, circle in self.indicators.values():
                    lamp.itemconfig(circle, fill="#22c55e")  # xanh

            # ===== CASE 2: STOP =====
            elif stop:

                # random 3 lỗi
                red_errors = random.sample(self.errors, 3)

                for name, (lamp, circle) in self.indicators.items():

                    if name in red_errors:
                        lamp.itemconfig(circle, fill="#e53935")  # đỏ
                    else:
                        lamp.itemconfig(circle, fill="#facc15")  # vàng

            # ===== CASE 3: IDLE =====
            else:
                for lamp, circle in self.indicators.values():
                    lamp.itemconfig(circle, fill="#7a7a7a")  # xám

        except Exception as e:
            print("ERROR UI:", e)

        # 🔥 LOOP
        self.after(500, self.update_auto)