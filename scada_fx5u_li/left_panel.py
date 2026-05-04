import tkinter as tk
import cv2
from PIL import Image, ImageTk

from plc_comm.reader import read_all_bits


# ===== MÀU GIAO DIỆN SCADA XÁM =====
PANEL_BG = "#d9d9d9"
STATS_BG = "#efefef"
VIDEO_BG = "#555555"
DATA_BG = "#4a4a4a"
DATA_FG = "#4ade80"


class LeftPanel(tk.LabelFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            text="THỐNG KÊ",
            font=("Arial", 11, "bold"),
            bg=PANEL_BG,
            fg="black"
        )

        self.labels = {}
        self.data_labels = {}

        # ====== THỐNG KÊ ======
        items = [
            ("Thời gian chu kỳ", "cycle"),
            ("Tổng đầu vào", "in"),
            ("Tổng SP đạt", "ok"),
            ("Tổng SP lỗi", "ng"),
            ("Tổng đầu ra", "out"),
            ("Lỗi đã gom", "rate")
        ]

        for name, key in items:
            frame = tk.Frame(self, bg=STATS_BG)
            frame.pack(fill="x", pady=5, padx=10)

            label = tk.Label(frame, text=name, anchor="w", bg=STATS_BG)
            label.pack(side="top", fill="x")
            self.labels[key] = label

            value = tk.Label(
                frame,
                text="0",
                bg=DATA_BG,
                fg=DATA_FG,
                font=("Courier", 16, "bold"),
                relief="sunken"
            )
            value.pack(side="top", fill="x", ipady=5)
            self.data_labels[key] = value

        # ====== SEPARATOR ======
        separator = tk.Frame(self, height=2, bd=1, relief="sunken", bg=PANEL_BG)
        separator.pack(fill="x", padx=5, pady=10)

        # ====== VIDEO + BUTTON ======
        self.video_container = tk.Frame(self, bg=PANEL_BG)
        self.video_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.video_frame = tk.Frame(self.video_container, bg=VIDEO_BG)
        self.video_frame.pack(side="left", fill="both", expand=True)
        self.video_frame.pack_propagate(False)

        self.video_label = tk.Label(self.video_frame, bg=VIDEO_BG)
        self.video_label.pack(fill="both", expand=True)

        self.button_frame = tk.Frame(self.video_container, bg=PANEL_BG)
        self.button_frame.pack(side="right", padx=5)

        self.btn_run = tk.Button(
            self.button_frame, text="RUN",
            bg="gray", font=("Arial", 10, "bold"),
            width=8, height=2
        )
        self.btn_run.pack(pady=5)

        self.btn_off = tk.Button(
            self.button_frame, text="OFF",
            bg="gray", font=("Arial", 10, "bold"),
            width=8, height=2
        )
        self.btn_off.pack(pady=5)

        # ====== VIDEO ======
        self.video_path = r"D:\SCADA_FX5U_li\assets\video_mohinh.mp4"
        self.cap = cv2.VideoCapture(self.video_path)
        self.running_video = True

        self.play_video()

    # ====== NHẬN TRẠNG THÁI PLC ======
    def update_status(self, bits):
        if not bits or len(bits) < 20:
            return

        try:
            # 🔥 mapping từ M900
            M916 = bits[16]   # RUN (Y16)
            M917 = bits[17]   # STOP (Y17)

            if M916 == 1:
                self.btn_run.config(bg="#22c55e")
                self.btn_off.config(bg="gray")

            elif M917 == 1:
                self.btn_run.config(bg="gray")
                self.btn_off.config(bg="#ef4444")

            else:
                self.btn_run.config(bg="gray")
                self.btn_off.config(bg="gray")

        except Exception as e:
            print("UPDATE STATUS ERROR:", e)

    # ====== VIDEO LOOP ======
    def play_video(self):
        if not self.running_video:
            return

        ret, frame = self.cap.read()

        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_h, frame_w = frame.shape[:2]
            container_w = self.video_frame.winfo_width()
            container_h = self.video_frame.winfo_height()

            if container_w > 20 and container_h > 20:
                ratio = min(container_w / frame_w, container_h / frame_h)
                new_w = int(frame_w * ratio)
                new_h = int(frame_h * ratio)

                resized = cv2.resize(frame, (new_w, new_h))
                canvas = Image.new("RGB", (container_w, container_h), (68, 68, 68))
                img = Image.fromarray(resized)

                x_offset = (container_w - new_w) // 2
                y_offset = (container_h - new_h) // 2
                canvas.paste(img, (x_offset, y_offset))

                imgtk = ImageTk.PhotoImage(canvas)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)

        self.after(30, self.play_video)

    # ====== SCALE ======
    def scale_widgets(self, factor):
        label_size = max(int(10 * factor), 8)
        value_size = max(int(16 * factor), 10)

        for l in self.labels.values():
            l.config(font=("Arial", label_size))

        for v in self.data_labels.values():
            v.config(font=("Courier", value_size, "bold"))

    # ====== UPDATE DATA ======
    def update_data(self, data):
        for k, v in data.items():
            if k in self.data_labels:
                self.data_labels[k].config(text=str(v))