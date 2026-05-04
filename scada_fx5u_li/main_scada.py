import tkinter as tk
import plc_comm

from plc_comm.plc_thread import start_plc_thread  # 🔥 thêm

from header_ui import Header
from left_panel import LeftPanel
from center_video import CarouselPanel
from right_panel import RightPanel
from footer_log import Footer


class ScadaApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # ===== CONNECT PLC =====
        self.plc_ok = plc_comm.connect_plc()

        # ===== START PLC THREAD =====
        start_plc_thread()   # 🔥 QUAN TRỌNG

        # ===== WINDOW =====
        self.title("SCADA FX5U - DYNAMIC SCALING")
        self.state("zoomed")

        self.base_width = 1200
        self.scale_factor = 1.0

        # ===== GRID =====
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # ===== HEADER =====
        self.header = Header(self)
        self.header.grid(row=0, column=0, sticky="nsew")

        # ===== MAIN FRAME =====
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        self.main_frame.columnconfigure(0, weight=16)
        self.main_frame.columnconfigure(1, weight=26)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # ===== PANELS =====
        self.left = LeftPanel(self.main_frame)
        self.left.grid(row=0, column=0, sticky="nsew")

        self.center = CarouselPanel(self.main_frame)
        self.center.grid(row=0, column=1, sticky="nsew")

        self.right = RightPanel(self.main_frame)
        self.right.grid(row=0, column=2, sticky="nsew")

        # ===== FOOTER =====
        self.footer = Footer(self)
        self.footer.grid(row=2, column=0, sticky="nsew")

        self.footer.set_status(self.plc_ok)

        # ===== EVENTS =====
        self.bind("<Configure>", self.on_resize)

        # ===== LOOP =====
        self.after(200, self.update_loop)   # 🔥 nhanh hơn

    # ================= RESIZE =================
    def on_resize(self, event):
        new_width = self.winfo_width()

        if new_width > 100:
            self.scale_factor = new_width / self.base_width
            self.update_fonts()

    def update_fonts(self):
        self.header.scale_widgets(self.scale_factor)
        self.left.scale_widgets(self.scale_factor)
        self.footer.scale_widgets(self.scale_factor)

    # ================= UI LOOP (KHÔNG BLOCK) =================
    def update_loop(self):
        try:
            # 🔥 LẤY DATA TỪ THREAD (KHÔNG ĐỌC PLC TRỰC TIẾP)
            data = plc_comm.latest_data
            bits = plc_comm.latest_bits
            fault_plc, fault_servo = plc_comm.latest_fault

            # LEFT
            if data:
                self.left.update_data(data)

            if bits:
                self.left.update_status(bits)

            # RIGHT
            if data:
                self.right.update_data(data)

            # FOOTER
            plc_ok = plc_comm.is_connected()
            self.footer.set_status(plc_ok)

        except Exception as e:
            print("UI ERROR:", e)
            self.footer.set_status(False)

        self.after(200, self.update_loop)   # 🔥 mượt hơn


if __name__ == "__main__":
    app = ScadaApp()
    app.mainloop()