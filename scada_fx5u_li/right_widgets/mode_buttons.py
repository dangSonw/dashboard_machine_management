import tkinter as tk
import threading
import time
import plc_comm
from plc_comm.writer import write_bit


class ModeButtons(tk.Frame):

    HOLD_TIME = 2  # dùng cho origin, auto, dummy

    def __init__(self, parent):
        super().__init__(parent)

        self.buttons = {}
        self._origin_active = False   # origin hold state
        self._run1step_active = False # run 1 step hold state
        self._auto_active = False     # auto hold state
        self._discharge_active = False # discharge hold state
        self._empty_active = False    # empty hold state

        # ===== TẠO BUTTON =====
        self.create_button("START", "#22c55e", self.start_action) # Green
        self.create_button("STOP", "#ef4444", self.stop_action)   # Red
        self.create_button("POWER", "#2e7d32", self.power_toggle)
        self.create_origin_button()   # 🔥 ORIGIN (X111)
        self.create_run1step_button() # 🔥 RUN 1 STEP (X112)
        self.create_button("EMPTY", "#888888", self.empty_mode) # Xám
        self.create_auto_button()     # 🔥 AUTO (X300)
        self.create_discharge_button() # 🔥 DISCHANGE (X306)

        # 🔥 LOOP UPDATE
        self.after(300, self.update_ui)

    # ================= UI =================
    def create_button(self, text, color, command):

        btn = tk.Button(
            self,
            text=text,
            bg=color,
            fg="white",
            font=("Arial", 12, "bold"),
            command=command
        )
        btn.pack(side="left", expand=True, fill="x", padx=3)

        self.buttons[text] = btn

    # ===== ORIGIN: Tạo button momentary giống web =====
    def create_origin_button(self):
        btn = tk.Button(
            self,
            text="ORIGIN",
            bg="#888888",
            fg="white",
            font=("Arial", 12, "bold")
        )
        btn.pack(side="left", expand=True, fill="x", padx=3)

        # 🔥 Giống web: onmousedown=1, onmouseup/leave=0
        btn.bind("<ButtonPress-1>", self._origin_press)
        btn.bind("<ButtonRelease-1>", self._origin_release)
        btn.bind("<Leave>", self._origin_release)   # an toàn: rời khỏi button cũng release

        self.buttons["ORIGIN"] = btn

    # ===== RUN 1 STEP: Tạo button momentary giống web =====
    def create_run1step_button(self):
        btn = tk.Button(
            self,
            text="RUN 1 STEP",
            bg="#888888",
            fg="white",
            font=("Arial", 12, "bold")
        )
        btn.pack(side="left", expand=True, fill="x", padx=3)

        # 🔥 Giống web: onmousedown=1, onmouseup/leave=0
        btn.bind("<ButtonPress-1>", self._run1step_press)
        btn.bind("<ButtonRelease-1>", self._run1step_release)
        btn.bind("<Leave>", self._run1step_release)

        self.buttons["RUN 1 STEP"] = btn

    # ===== AUTO: Tạo button momentary giống web =====
    def create_auto_button(self):
        btn = tk.Button(
            self,
            text="AUTO",
            bg="#888888",
            fg="white",
            font=("Arial", 12, "bold")
        )
        btn.pack(side="left", expand=True, fill="x", padx=3)

        btn.bind("<ButtonPress-1>", self._auto_press)
        btn.bind("<ButtonRelease-1>", self._auto_release)
        btn.bind("<Leave>", self._auto_release)

        self.buttons["AUTO"] = btn

    # ===== DISCHARGE: Tạo button momentary giống web =====
    def create_discharge_button(self):
        btn = tk.Button(
            self,
            text="DISCHANGE",
            bg="#888888",
            fg="white",
            font=("Arial", 12, "bold")
        )
        btn.pack(side="left", expand=True, fill="x", padx=3)

        btn.bind("<ButtonPress-1>", self._discharge_press)
        btn.bind("<ButtonRelease-1>", self._discharge_release)
        btn.bind("<Leave>", self._discharge_release)

        self.buttons["DISCHANGE"] = btn

    # ================= READ BIT =================
    def get_bit(self, name):
        # 🔥 Dùng latest_m_modes cho M0, M303, M312, M315, M500
        modes = getattr(plc_comm, "latest_m_modes", {})
        if name in modes:
            return modes.get(name, 0)

        # Fallback: M900-M949 dùng latest_bits
        bits = getattr(plc_comm, "latest_bits", [])
        if not bits:
            return 0

        try:
            if name.startswith("M"):
                m = int(name[1:])
                offset = m - 900

                if 0 <= offset < len(bits):
                    return bits[offset]

        except Exception as e:
            print("GET BIT ERROR:", e)

        return 0

    # ================= UPDATE UI =================
    def update_ui(self):

        try:
            mapping = {
                "POWER": "M0"
            }

            for name, bit in mapping.items():

                state = self.get_bit(bit)

                if state:
                    self.buttons[name].config(bg="#22c55e")  # xanh
                else:
                    self.buttons[name].config(bg="#888888")  # xám

            # 🔥 ORIGIN dùng _origin_active state
            if self._origin_active:
                self.buttons["ORIGIN"].config(bg="#1565c0")  # dark blue when held
            else:
                self.buttons["ORIGIN"].config(bg="#888888")  # gray when released

            # 🔥 RUN 1 STEP dùng _run1step_active state
            if self._run1step_active:
                self.buttons["RUN 1 STEP"].config(bg="#8e24aa")  # purple when held
            else:
                self.buttons["RUN 1 STEP"].config(bg="#888888")  # gray when released

            # 🔥 AUTO dùng _auto_active state
            if self._auto_active:
                self.buttons["AUTO"].config(bg="#eab308")  # vàng cam
            else:
                self.buttons["AUTO"].config(bg="#888888")

            # 🔥 DISCHANGE dùng _discharge_active state
            if self._discharge_active:
                self.buttons["DISCHANGE"].config(bg="#eab308")  # vàng cam
            else:
                self.buttons["DISCHANGE"].config(bg="#888888")

            # 🔥 EMPTY dùng _empty_active state
            if self._empty_active:
                self.buttons["EMPTY"].config(bg="#eab308")  # vàng cam
            else:
                self.buttons["EMPTY"].config(bg="#888888")

        except Exception as e:
            print("UI ERROR:", e)

        self.after(300, self.update_ui)

    # ================= LOGIC =================

    def start_action(self):
        threading.Thread(target=self._short_pulse, args=("X125",), daemon=True).start()

    def stop_action(self):
        threading.Thread(target=self._short_pulse, args=("X124",), daemon=True).start()

    def _short_pulse(self, device):
        """Send 0.5s pulse like web pulseCommand"""
        try:
            write_bit(device, 1)
            print(f"[{device}] = 1 (PULSE START)")
            time.sleep(0.5)
            write_bit(device, 0)
            print(f"[{device}] = 0 (PULSE END)")
        except Exception as e:
            print("PULSE ERROR:", e)

    # 🔥 POWER → toggle ON/OFF
    def power_toggle(self):
        state = self.get_bit("M0")
        write_bit("M0", 0 if state else 1)

    # 🔥 ORIGIN (MOMENTARY giống web) → hold X111=1, release X111=0
    def _origin_press(self, event=None):
        if not self._origin_active:
            self._origin_active = True
            threading.Thread(target=self._origin_press_task, daemon=True).start()

    def _origin_press_task(self):
        """Ghi X111=1 khi người dùng nhấn hold button"""
        write_bit("X111", 1)
        print("[ORIGIN] X111 = 1 (HOLD)")

    def _origin_release(self, event=None):
        if self._origin_active:
            self._origin_active = False
            threading.Thread(target=self._origin_release_task, daemon=True).start()

    def _origin_release_task(self):
        """Ghi X111=0 khi người dùng release button"""
        write_bit("X111", 0)
        print("[ORIGIN] X111 = 0 (RELEASE)")

    # 🔥 RUN 1 STEP (MOMENTARY giống web) → hold X112=1, release X112=0
    def _run1step_press(self, event=None):
        if not self._run1step_active:
            self._run1step_active = True
            threading.Thread(target=self._run1step_press_task, daemon=True).start()

    def _run1step_press_task(self):
        """Ghi X112=1 khi người dùng nhấn hold button"""
        write_bit("X112", 1)
        print("[RUN 1 STEP] X112 = 1 (HOLD)")

    def _run1step_release(self, event=None):
        if self._run1step_active:
            self._run1step_active = False
            threading.Thread(target=self._run1step_release_task, daemon=True).start()

    def _run1step_release_task(self):
        """Ghi X112=0 khi người dùng release button"""
        write_bit("X112", 0)
        print("[RUN 1 STEP] X112 = 0 (RELEASE)")

    # 🔥 AUTO (MOMENTARY giống web) → hold X300=1, release X300=0
    def _auto_press(self, event=None):
        if not self._auto_active:
            self._auto_active = True
            threading.Thread(target=self._auto_press_task, daemon=True).start()

    def _auto_press_task(self):
        write_bit("X300", 1)
        print("[AUTO] X300 = 1 (HOLD)")

    def _auto_release(self, event=None):
        if self._auto_active:
            self._auto_active = False
            threading.Thread(target=self._auto_release_task, daemon=True).start()

    def _auto_release_task(self):
        write_bit("X300", 0)
        print("[AUTO] X300 = 0 (RELEASE)")

    # 🔥 DISCHARGE (MOMENTARY giống web) → hold X306=1, release X306=0
    def _discharge_press(self, event=None):
        if not self._discharge_active:
            self._discharge_active = True
            threading.Thread(target=self._discharge_press_task, daemon=True).start()

    def _discharge_press_task(self):
        write_bit("X306", 1)
        print("[DISCHARGE] X306 = 1 (HOLD)")

    def _discharge_release(self, event=None):
        if self._discharge_active:
            self._discharge_active = False
            threading.Thread(target=self._discharge_release_task, daemon=True).start()

    def _discharge_release_task(self):
        write_bit("X306", 0)
        print("[DISCHARGE] X306 = 0 (RELEASE)")

    # 🔥 EMPTY (send command X304=1 exactly like web)
    def empty_mode(self):
        self._empty_active = not self._empty_active
        if self._empty_active:
            write_bit("X304", 1)
            print("[EMPTY] X304 = 1 (ON)")
        else:
            write_bit("X304", 0)
            print("[EMPTY] X304 = 0 (OFF)")

    # ================= HOLD 2s =================
    def _hold_pulse(self, device):
        try:
            write_bit(device, 1)
            time.sleep(self.HOLD_TIME)
            write_bit(device, 0)
        except Exception as e:
            print("PULSE ERROR:", e)