import tkinter as tk
from tkinter import ttk
import time


class HistoryView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        # STYLE chỉnh font
        style = ttk.Style()

        style.configure(
            "Treeview",
            font=("Arial", 12)   # chữ trong bảng
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 13, "bold")   # chữ tiêu đề
        )

        columns = ("Time", "Cycle(ms)", "Defect")

        self.table = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=6
        )

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center")

        self.table.pack(fill="both", expand=True)

    def add_row(self, cycle, defect):

        timestamp = time.strftime("%H:%M:%S")

        self.table.insert(
            "",
            0,
            values=(timestamp, cycle, defect)
        )

        if len(self.table.get_children()) > 30:
            self.table.delete(self.table.get_children()[-1])