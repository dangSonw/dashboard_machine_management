# ===== IMPORT API CHÍNH =====
from .connection import connect_plc, ensure_connection, get_client, lock
from .reader import (
    read_words,
    read_fault,
    read_all_bits,
    read_words_device,
    read_bits_device,
    read_machine_bits,
    read_dword
)

from .commands import (
    set_auto,
    set_manual,
    dummy_mode,
    empty_mode,
    power_on,
    origin,
    rotate_table
)

# ===== TRẠNG THÁI KẾT NỐI =====
def is_connected():
    try:
        from .connection import connected
        return connected
    except:
        return False


# ===== BUFFER DATA (GLOBAL SHARED) =====
latest_data = {}
latest_bits = []
latest_fault = (0, 0)

# 🔥 DATA REALTIME
latest_angle = 0
latest_d7000 = []
latest_m = [0] * 50   # 🔥 đọc M900 -> M949

# 🔥 BUFFER MODE BITS (M0, M303, M312, M315, M500)
latest_m_modes = {
    "M0": 0,
    "M303": 0,
    "M312": 0,
    "M315": 0,
    "M500": 0,
}


# ===== EXPORT =====
__all__ = [
    # connection
    "connect_plc",
    "ensure_connection",
    "get_client",
    "lock",

    # reader
    "read_words",
    "read_fault",
    "read_all_bits",
    "read_words_device",
    "read_bits_device",
    "read_machine_bits",
    "read_dword",

    # commands
    "set_auto",
    "set_manual",
    "dummy_mode",
    "empty_mode",
    "power_on",
    "origin",
    "rotate_table",

    # trạng thái
    "is_connected",

    # dữ liệu realtime
    "latest_data",
    "latest_bits",
    "latest_fault",
    "latest_angle",
    "latest_d7000",
    "latest_m",
    "latest_m_modes"
]