from plc_comm import plc_comm
from .writer import write_bit, write_pulse
from .reader import read_dword, read_machine_bits
import time
import threading

# ================= READ DATA =================
def read_angle_d100():
    try:
        data = plc_comm.read_words_device("D100", 2)

        if not data or len(data) < 2:
            return 0.0

        low = data[0] & 0xFFFF
        high = data[1] & 0xFFFF

        raw = (high << 16) | low

        angle = raw / 1000.0
        angle = angle % 360

        return angle

    except Exception as e:
        print("READ D100 ERROR:", e)
        return 0.0
#đọc tín hiệu 
def read_production_data():
    try:
        angle = read_angle_d100()

        # ===== GÓC CHUẨN =====
        angle_std = (int((angle + 30) // 60) * 60) % 360

        # ===== POS (0 → 5) =====
        pos = angle_std // 60

        return {
            "angle_real": round(angle, 2),  # góc thực
            "angle_std": angle_std,         # 0,60,120...
            "pos": int(angle_std),                # 🔥 đây của bạn đây
            "manual_speed": read_dword("D300"),
            "auto_speed": read_dword("D302"),
            "org": read_dword("D304"),
            "step": read_dword("D306")
        }

    except Exception as e:
        print("READ PRODUCTION ERROR:", e)
        return None
def read_status():
    try:
        bits = read_machine_bits("M106", 1)

        if bits is None:
            return 0

        return bits[0]

    except Exception as e:
        print("READ STATUS ERROR:", e)
        return 0
# ================= WRITE CONTROL =================

def jog_minus():
    write_bit("M115", 1)
    time.sleep(0.1)
    write_bit("M115", 0)


def jog_plus():
    write_bit("M114", 1)
    time.sleep(0.1)
    write_bit("M114", 0)


def servo_on():
    write_pulse("M117")


def servo_off():
    write_pulse("M110")


def origin():
    write_pulse("M111")
def onlight():
    write_pulse("M151")

def offlight():
    write_pulse("M152")

def run_1_step():
    """
    🔥 giữ 2s
    👉 đổi thời gian tại đây nếu cần
    """
    def task():
        write_bit("M112", 1)
        time.sleep(2)
        write_bit("M112", 0)

    threading.Thread(target=task, daemon=True).start()