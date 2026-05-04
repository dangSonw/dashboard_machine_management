class StackButtons:

    def __init__(self, canvas, x, y, plc_write_callback=None):
        self.canvas = canvas
        self.write_plc = plc_write_callback

        size = 40

        # 🔥 STATE
        self.yellow_hold = False

        # ===== BUTTON =====
        self.red = canvas.create_rectangle(
            x-size//2, y-size//2,
            x+size//2, y+size//2,
            fill="#550000", outline=""
        )

        self.yellow = canvas.create_rectangle(
            x-size//2, y+40-size//2,
            x+size//2, y+40+size//2,
            fill="#555000", outline=""
        )

        self.green = canvas.create_rectangle(
            x-size//2, y+80-size//2,
            x+size//2, y+80+size//2,
            fill="#003300", outline=""
        )

        # ===== LABEL =====
        self.label = canvas.create_text(
            x, y+130,
            text="STACK CTRL",
            font=("Arial", 12, "bold")
        )

        # ===== CLICK =====
        canvas.tag_bind(self.red, "<Button-1>", lambda e: self.press_red())
        canvas.tag_bind(self.yellow, "<Button-1>", lambda e: self.press_yellow())
        canvas.tag_bind(self.green, "<Button-1>", lambda e: self.press_green())

    # ================= RED =================
    def press_red(self):
        self.flash(self.red, "#ef4444", "#550000")
        self.canvas.after(2000, lambda: self.send("M890"))

    # ================= GREEN =================
    def press_green(self):
        self.flash(self.green, "#22c55e", "#003300")
        self.canvas.after(2000, lambda: self.send("M892"))

    # ================= YELLOW (GIỮ) =================
    def press_yellow(self):
        self.yellow_hold = not self.yellow_hold

        if self.yellow_hold:
            self.canvas.itemconfig(self.yellow, fill="#facc15")
            self.send("M891")
        else:
            self.canvas.itemconfig(self.yellow, fill="#555000")
            self.send("M891")

    # ================= SEND =================
    def send(self, bit):
        if self.write_plc:
            self.write_plc(bit, True)

    # ================= FLASH =================
    def flash(self, obj, on_color, off_color):
        self.canvas.itemconfig(obj, fill=on_color)
        self.canvas.after(150, lambda: self.canvas.itemconfig(obj, fill=off_color))

    # ================= UPDATE (ĐỒNG BỘ PLC) =================
    def update(self, r, y, g):

        # 🔴
        self.canvas.itemconfig(
            self.red,
            fill="#ef4444" if r else "#550000"
        )

        # 🟡
        if self.yellow_hold:
            self.canvas.itemconfig(self.yellow, fill="#facc15")
        else:
            self.canvas.itemconfig(
                self.yellow,
                fill="#facc15" if y else "#555000"
            )

        # 🟢
        self.canvas.itemconfig(
            self.green,
            fill="#22c55e" if g else "#003300"
        )