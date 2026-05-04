import tkinter as tk
from PIL import Image, ImageTk
import time


class Header(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#E6EEF7")

        # ======================
        # LEFT SIDE (LOGO + TITLE)
        # ======================

        left_frame = tk.Frame(self, bg="#E6EEF7")
        left_frame.pack(side="left", padx=10)

        # Logo
        self.logo_path = "assets/logo_truong.png"

        try:
            self.original_image = Image.open(self.logo_path)
        except:
            self.original_image = Image.new('RGB', (60, 60), "#E6EEF7")

        self.logo_tk = ImageTk.PhotoImage(
            self.original_image.resize((60, 60), Image.LANCZOS)
        )

        self.lbl_logo = tk.Label(
            left_frame,
            image=self.logo_tk,
            bg="#E6EEF7"
        )

        self.lbl_logo.pack(side="left", padx=10)

        # Title
        self.lbl_title = tk.Label(
            left_frame,
            text="TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI",
            font=("Arial", 18, "bold"),
            bg="#E6EEF7"
        )

        self.lbl_title.pack(side="left")

        # ======================
        # RIGHT SIDE (TIME + LOCATION)
        # ======================

        right_frame = tk.Frame(self, bg="#E6EEF7")
        right_frame.pack(side="right", padx=20)

        # Location
        self.lbl_location = tk.Label(
            right_frame,
            text="Hà Nội, Việt Nam",
            font=("Arial", 10),
            bg="#E6EEF7"
        )

        self.lbl_location.pack(anchor="e")

        # Date
        self.lbl_date = tk.Label(
            right_frame,
            font=("Arial", 11),
            bg="#E6EEF7"
        )

        self.lbl_date.pack(anchor="e")

        # Time
        self.lbl_time = tk.Label(
            right_frame,
            font=("Arial", 14, "bold"),
            bg="#E6EEF7"
        )

        self.lbl_time.pack(anchor="e")

        # Start clock
        self.update_clock()

    # ======================
    # CLOCK UPDATE
    # ======================

    def update_clock(self):

        now = time.localtime()

        current_time = time.strftime("%H:%M:%S", now)
        current_date = time.strftime("%d/%m/%Y", now)

        self.lbl_time.config(text=current_time)
        self.lbl_date.config(text=current_date)

        self.after(1000, self.update_clock)

    # ======================
    # SCALE UI
    # ======================

    def scale_widgets(self, factor):

        new_font_size = max(int(18 * factor), 10)

        self.lbl_title.config(
            font=("Arial", new_font_size, "bold")
        )

        new_logo_size = max(int(60 * factor), 20)

        resized_img = self.original_image.resize(
            (new_logo_size, new_logo_size),
            Image.LANCZOS
        )

        self.logo_tk = ImageTk.PhotoImage(resized_img)

        self.lbl_logo.config(image=self.logo_tk)