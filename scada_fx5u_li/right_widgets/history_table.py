import tkinter as tk
import plc_comm

from right_widgets.history_view import HistoryView
from right_widgets.history_buttons import HistoryButtons


class HistoryTable(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        # ===== LAYOUT =====
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)

        self.history_view = HistoryView(self)
        self.history_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.buttons = HistoryButtons(self)
        self.buttons.grid(row=0, column=1, sticky="ns", padx=5, pady=5)

        # ===== BIẾN LƯU TRẠNG THÁI CŨ =====
        self.last_ok = 0
        self.last_ng = 0

        # 🔥 LOOP
        self.after(500, self.update_auto)

    # =========================
    # 🔥 ĐỌC WORD PLC
    # =========================
    def read_word(self, device):

        try:
            data = plc_comm.read_words_device(device, 1)
            if data:
                return data[0]
        except Exception as e:
            print("READ WORD ERROR:", e)

        return 0

    # =========================
    # 🔥 LOGIC CHÍNH
    # =========================
    def update_auto(self):

        try:
            ok = self.read_word("D14")
            ng = self.read_word("D16")
            cycle = self.read_word("D6")

            # ===== OK TĂNG =====
            if ok > self.last_ok:
                self.history_view.add_row(cycle, 1)

            # ===== NG TĂNG =====
            if ng > self.last_ng:
                self.history_view.add_row(cycle, 0)

            # ===== UPDATE LẠI =====
            self.last_ok = ok
            self.last_ng = ng

        except Exception as e:
            print("HISTORY ERROR:", e)

        # LOOP
        self.after(500, self.update_auto)