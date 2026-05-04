import tkinter as tk

from right_widgets.charts.pie_chart_ui import PieChart
from right_widgets.charts.bar_chart_ui import BarChart
from right_widgets.charts.productivity_ui import Productivity

from right_widgets.charts.pie_chart_data import get_pie_data
from right_widgets.charts.bar_chart_data import get_bar_data
from right_widgets.charts.productivity_data import get_productivity


class DefectChart(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.left = tk.Frame(self)
        self.left.pack(side="left", fill="both", expand=True)

        self.right = tk.Frame(self)
        self.right.pack(side="right", fill="both", expand=True)

        # UI
        self.pie = PieChart(self.left)
        self.pie.pack(pady=10)

        self.prod = Productivity(self.left)
        self.prod.pack(pady=10)

        self.bar = BarChart(self.right)
        self.bar.pack(fill="both", expand=True)

        self.update_all()

    def update_all(self):

        ok, ng = get_pie_data()
        self.pie.update_data(ok, ng)

        bar_data = get_bar_data()
        self.bar.update_data(bar_data)

        total, history = get_productivity()
        self.prod.update_data(total, history)

        self.after(1000, self.update_all)