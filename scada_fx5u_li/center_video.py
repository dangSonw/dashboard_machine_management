import tkinter as tk
import plc_comm
from plc_comm.writer import write_pulse

from center_modules.carousel.carousel_core import CarouselCore
from center_modules.carousel.carousel_renderer import CarouselRenderer

from center_modules.indicators.sensor_lamp import SensorLamp
from center_modules.indicators.camera_lamp import CameraLamp
from center_modules.indicators.stack_lamp import StackLamp

from center_modules.controls.start_buttons import StartButton
from center_modules.controls.stack_buttons import StackButtons

from center_modules.config.colors import *


class CarouselPanel(tk.Canvas):

    def __init__(self, parent):
        super().__init__(parent, bg=BG, highlightthickness=0)

        # ===== CORE =====
        self.core = CarouselCore()
        self.renderer = CarouselRenderer(self)

        # ===== UI OBJECT =====
        self.cam = None
        self.stack = None
        self.ctrl = None
        self.sensors = []
        self.buttons = []

        # ===== OFFSET =====
        self.btn_offset_x = 120
        self.btn_offset_y = 150

        # ===== LOOP =====
        self.after(40, self.animate)

    # ================= WRITE PLC =================
    def write_plc(self, bit, value):
        try:
            write_pulse(bit)
        except Exception as e:
            print("WRITE FAIL:", e)

    # ================= READ BIT =================
    def get_bit(self, name):

        bits = getattr(plc_comm, "latest_bits", [])

        if not bits:
            return False

        try:
            # ===== Y → M900+ =====
            if name.startswith("Y"):
                y_index = int(name[1:])
                m_index = 900 + y_index
                offset = m_index - 900

                if offset < len(bits):
                    return bits[offset]

            # ===== M TRỰC TIẾP =====
            elif name.startswith("M"):
                m_index = int(name[1:])
                offset = m_index - 900

                if 0 <= offset < len(bits):
                    return bits[offset]

        except Exception as e:
            print("GET BIT ERROR:", e)

        return False

    # ================= LOOP =================
    def animate(self):
        self.update_ui()
        self.after(40, self.animate)

    # ================= UI =================
    def update_ui(self):

        w = self.winfo_width()
        h = self.winfo_height()

        if w < 50 or h < 50:
            return

        center_x = w // 2
        center_y = h // 2
        radius = min(w, h) // 3

        # ===== DRAW CAROUSEL =====
        self.renderer.draw(center_x, center_y, radius, self.core)

        # ===== INIT (CHỈ CHẠY 1 LẦN) =====
        if self.cam is None:

            # CAMERA
            self.cam = CameraLamp(self, center_x, center_y - radius - 130)

            # STACK LAMP
            self.stack = StackLamp(self, center_x + 200, center_y - radius - 130)

            # CONTROL BUTTON
            self.ctrl = StackButtons(
                self,
                center_x - 200,
                center_y - radius - 130,
                plc_write_callback=self.write_plc
            )

            # SENSOR
            self.sensors = [
                SensorLamp(self, center_x - radius - 80, center_y, "NG"),
                SensorLamp(self, center_x - 100, center_y + radius + 20, "INPUT"),
                SensorLamp(self, center_x + 100, center_y + radius + 20, "OUTPUT")
            ]

            # START BUTTON
            

        # ===== UPDATE STACK LAMP =====
        red = self.get_bit("Y17")
        yellow = self.get_bit("Y14")
        green = self.get_bit("Y16")

        self.stack.update(red, yellow, green)
        self.ctrl.update(red, yellow, green)

        # ===== CAMERA =====
        self.cam.update(self.get_bit("Y20"))

        # ===== SENSOR (M925 - M927) =====
        ng_state = self.get_bit("M925")
        input_state = self.get_bit("M926")
        output_state = self.get_bit("M927")

        if len(self.sensors) >= 3:
            self.sensors[0].update(ng_state)
            self.sensors[1].update(input_state)
            self.sensors[2].update(output_state)