import tkinter as tk

class PieChart(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, width=200, height=200)
        self.canvas.pack()

        self.ok = 1
        self.ng = 1

    def update_data(self, ok, ng):
        self.ok = ok
        self.ng = ng
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        total = self.ok + self.ng
        if total == 0:
            total = 1

        ok_angle = (self.ok / total) * 360

        self.canvas.create_arc(30, 30, 170, 170,
                               start=0, extent=ok_angle,
                               fill="green")

        self.canvas.create_arc(30, 30, 170, 170,
                               start=ok_angle,
                               extent=360-ok_angle,
                               fill="red")

        self.canvas.create_text(
          100, 100,
          text=f"{int(self.ok/total*100)}% OK\n{int(self.ng/total*100)}% NG",
          font=("Arial", 14, "bold"),
          fill="black" )