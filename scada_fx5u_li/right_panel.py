import tkinter as tk
from tkinter import ttk
from right_widgets.mode_buttons import ModeButtons
from right_widgets.error_buttons import ErrorButtons
from right_widgets.history_table import HistoryTable
from right_widgets.production_stats import ProductionStats

class RightPanel(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, padx=10, pady=10)

        self.mode = ModeButtons(self)
        self.mode.pack(fill="x")

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=8)

        self.errors = ErrorButtons(self)
        self.errors.pack(fill="x")

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        self.history = HistoryTable(self)

        # ❗ sửa ở đây để bảng không kéo giãn quá lớn
        self.history.pack(fill="x", pady=4)
        #Phần thêm cuối cùng - cài đặt thông số động cơ 
        self.stats = ProductionStats(self)
        self.stats.pack(fill="x", pady=2)

    def update_data(self, data):
        # HistoryTable tự quản lý loop riêng (update_auto)
        # Không cần gọi add_row ở đây nữa
        pass

    # giữ hàm này để không lỗi nhưng không scale
    def scale_widgets(self, factor):
        pass