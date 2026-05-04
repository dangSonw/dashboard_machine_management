from .connection import connect_plc
from .reader import read_words, read_fault, read_machine_bits, read_words_device
from .commands import (
    set_auto,
    set_manual,
    dummy_mode,
    empty_mode,
    power_on,
    origin,
    rotate_table
)

# ===== REALTIME DATA =====
latest_bits = []
latest_data = {}
latest_fault = (False, False)

# 🔥 THÊM MỚI (QUAN TRỌNG)
latest_angle = 0
latest_d7000 = []

# ===== CONNECTION CHECK =====
def is_connected():
    try:
        from .connection import connected
        return connected
    except:
        return False

# =========================
__all__ = [
    "connect_plc",
    "read_words",
    "read_fault",
    "read_machine_bits",
    "read_words_device",
    "set_auto",
    "set_manual",
    "dummy_mode",
    "empty_mode",
    "power_on",
    "origin",
    "rotate_table",
    "latest_bits",
    "latest_data",
    "latest_fault",
    "latest_angle",
    "latest_d7000",
    "is_connected"
]