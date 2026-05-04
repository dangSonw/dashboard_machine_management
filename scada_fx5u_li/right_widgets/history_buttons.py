import tkinter as tk
from tkinter import Toplevel, ttk
import os
import time
import csv
from PIL import Image, ImageTk


class HistoryButtons(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.btn_image = tk.Button(
            self,
            text="DỮ LIỆU ẢNH",
            width=18,
            height=2,
            font=("Arial", 12, "bold"),
            command=lambda: self.on_button_click(self.btn_image, self.open_image_data)
        )

        self.btn_error = tk.Button(
            self,
            text="DỮ LIỆU LỖI",
            width=18,
            height=2,
            font=("Arial", 12, "bold"),
            command=lambda: self.on_button_click(self.btn_error, self.open_error_data)
        )

        self.btn_image.pack(pady=10)
        self.btn_error.pack(pady=10)

    # =====================================
    # 🎯 ĐỔI MÀU NÚT
    # =====================================
    def on_button_click(self, button, command):
        for btn in [self.btn_image, self.btn_error]:
            btn.config(bg="SystemButtonFace", fg="black")

        button.config(bg="#00BFFF", fg="white")
        command()

    # =====================================
    # 📸 DỮ LIỆU ẢNH (FINAL)
    # =====================================
    def open_image_data(self):

        folder = r"C:\Users\Public\Documents\RAMDisk\anh"

        if not os.path.exists(folder):
            print("❌ Không tìm thấy thư mục")
            return

        files = [f for f in os.listdir(folder) if f.lower().endswith(".jpg")]
        files.sort(reverse=True)

        win = Toplevel(self)
        win.title("Dữ liệu ảnh")
        win.geometry("1300x750")

        # ===== PANED WINDOW (KÉO ĐƯỢC) =====
        paned = tk.PanedWindow(win, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)

        left_frame = tk.Frame(paned, bg="#f5f6fa")
        right_frame = tk.Frame(paned, bg="#dfe6e9")

        paned.add(left_frame, minsize=780)   # ~60%
        paned.add(right_frame, minsize=520)  # ~40%

        tk.Label(left_frame,
                 text="DỮ LIỆU ẢNH - THIẾT BỊ LỖI",
                 font=("Arial", 16, "bold"),
                 bg="#f5f6fa").pack(pady=10)

        image_frame = tk.Frame(left_frame, bg="#f5f6fa")
        image_frame.pack(pady=10)

        self.image_refs = []

        # ===== DANH SÁCH FILE =====
        tk.Label(right_frame,
                 text="Danh sách file",
                 bg="#dfe6e9",
                 font=("Arial", 12, "bold")).pack(pady=5)

        file_list = tk.Listbox(right_frame, font=("Courier", 10))
        file_list.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(file_list)
        scrollbar.pack(side="right", fill="y")

        file_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=file_list.yview)

        base_time = time.time() - 120

        # ===== LOAD =====
        for i, f in enumerate(files):

            fake_time = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(base_time + i)
            )

            display = f"{fake_time} | {f}"

            if i < 4:
                path = os.path.join(folder, f)

                try:
                    img = Image.open(path)

                    # ===== FIX TỶ LỆ CHUẨN =====
                    w, h = img.size
                    scale = min(240 / w, 180 / h)
                    new_size = (int(w * scale), int(h * scale))
                    img = img.resize(new_size, Image.LANCZOS)

                    photo = ImageTk.PhotoImage(img)

                    frame = tk.Frame(image_frame, bg="white", bd=2, relief="ridge")
                    frame.grid(row=i // 2, column=i % 2, padx=10, pady=10)

                    canvas = tk.Canvas(frame, width=240, height=180,
                                       bg="white", highlightthickness=0)
                    canvas.pack()

                    canvas.create_image(120, 90, image=photo)

                    lbl_name = tk.Label(frame, text=f, font=("Arial", 9), bg="white")
                    lbl_name.pack(pady=3)

                    self.image_refs.append(photo)

                    # click phóng to
                    canvas.bind("<Button-1>", lambda e, p=path: self.show_full_image(p))

                    # hover
                    def on_enter(e): frame.config(bg="#e6f7ff")
                    def on_leave(e): frame.config(bg="white")

                    frame.bind("<Enter>", on_enter)
                    frame.bind("<Leave>", on_leave)

                except Exception as e:
                    print("Lỗi load ảnh:", e)

            file_list.insert(tk.END, display)

        # ===== DOUBLE CLICK =====
        def open_selected(event):
            selection = file_list.curselection()
            if not selection:
                return

            index = selection[0]
            filename = files[index]
            full_path = os.path.join(folder, filename)

            try:
                os.startfile(full_path)
            except:
                print("Không mở được file:", full_path)

        file_list.bind("<Double-Button-1>", open_selected)

    # =====================================
    # 🔍 PHÓNG TO ẢNH
    # =====================================
    def show_full_image(self, path):

        win = Toplevel(self)
        win.title("Xem ảnh")
        win.geometry("800x600")

        img = Image.open(path)
        img.thumbnail((750, 550))
        photo = ImageTk.PhotoImage(img)

        lbl = tk.Label(win, image=photo)
        lbl.image = photo
        lbl.pack(expand=True)

    # =====================================
    # 📊 DỮ LIỆU LỖI
    # =====================================
    def open_error_data(self):

        file_path = r"D:\taocsv\data\logdata.csv"

        if not os.path.exists(file_path):
            print("❌ Không tìm thấy file CSV")
            return

        win = Toplevel(self)
        win.title("Dữ liệu lỗi")
        win.geometry("1200x700")

        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                data = list(reader)

            if not data:
                return

            headers = data[0]
            rows = data[1:]

            table = ttk.Treeview(win, columns=headers, show="headings")

            for col in headers:
                table.heading(col, text=col)
                table.column(col, anchor="center", width=150)

            table.pack(fill="both", expand=True)

            table.tag_configure("error", background="#ffcccc")

            for row in rows:
                text = " ".join(row).lower()
                tag = "error" if ("error" in text or "fail" in text) else ""

                table.insert("", "end", values=row, tags=(tag,))

        except Exception as e:
            print("CSV ERROR:", e)