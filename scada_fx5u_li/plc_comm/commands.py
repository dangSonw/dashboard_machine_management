from .writer import write_pulse, write_bit
# ================= MODE =================
def set_auto():
    write_pulse("M315")

def set_manual():
    write_pulse("M301")

def dummy_mode():
    write_pulse("M312")

def empty_mode(value):
    """
    🔥 Toggle ON/OFF
    value = 1 → ON
    value = 0 → OFF
    """
    write_bit("M303", value)
# ================= MACHINE =================
def power_on():
    write_pulse("M0")
def origin():
    write_pulse("M500")
# ================= ROTATE =================
def rotate_table():
    write_bit("M5001", 1)
