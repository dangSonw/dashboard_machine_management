from pymcprotocol import Type3E
import threading
import time as _time

plc = Type3E()
connected = False
lock = threading.Lock()

def _convert_address(dev_name):
    """
    Convert FX5U octal X/Y address to hex format required by pymcprotocol.
    Example: "X200" (octal) → "X080" (hex, because 200oct = 0x80)
             "X150" (octal) → "X068" (hex, because 150oct = 0x68)
             "M200" → "M200" (no change, M is decimal)
    """
    if dev_name and dev_name[0] in ('X', 'Y'):
        try:
            prefix = dev_name[0]
            num_str = dev_name[1:]
            decimal_val = int(num_str, 8)   # treat as octal
            hex_str = format(decimal_val, '03X')
            converted = f"{prefix}{hex_str}"
            print(f"[PLC] Address convert: {dev_name} (octal) → {converted} (hex for pymcprotocol)")
            return converted
        except ValueError:
            # Already hex or invalid — return as-is
            return dev_name
    return dev_name

def connect_plc(ip="192.168.1.10", port=5011):
    global connected
    try:
        plc.setaccessopt(commtype="binary")
        plc.connect(ip, port)
        connected = True
        return True
    except Exception as e:
        print(f"[PLC] Connect failed: {e}")
        connected = False
        return False

def read_words():
    if not connected:
        return None

    with lock:
        try:
            return {
                "cycle": plc.batchread_wordunits("D6", 1)[0],
                "in":    plc.batchread_wordunits("D10", 1)[0],
                "ok":    plc.batchread_wordunits("D14", 1)[0],
                "ng":    plc.batchread_wordunits("D16", 1)[0],
                "out":   plc.batchread_wordunits("D12", 1)[0],
                "rate":  plc.batchread_wordunits("D20", 1)[0],
            }
        except Exception as e:
            print(f"[PLC] read_words error: {e}")
            return None

def read_fault():
    if not connected:
        return False, False

    with lock:
        try:
            plc_fault   = plc.batchread_bitunits("Y010", 1)[0]
            servo_fault = plc.batchread_bitunits("Y011", 1)[0]
            return plc_fault, servo_fault
        except Exception as e:
            print(f"[PLC] read_fault error: {e}")
            return False, False

def set_auto():
    if not connected:
        return
    with lock:
        try:
            plc.batchwrite_bitunits(_convert_address("X300"), [1])
        except Exception as e:
            print(f"[PLC] set_auto error: {e}")

def set_manual():
    if not connected:
        return
    with lock:
        try:
            plc.batchwrite_bitunits(_convert_address("X301"), [1])
        except Exception as e:
            print(f"[PLC] set_manual error: {e}")

def rotate_table():
    if not connected:
        return
    with lock:
        try:
            plc.batchwrite_bitunits("M5001", [1])
        except Exception as e:
            print(f"[PLC] rotate_table error: {e}")

def read_device(dev_name, size=1):
    """Read a PLC device. X/Y addresses are auto-converted from octal."""
    if not connected:
        return None
    converted = _convert_address(dev_name)
    with lock:
        try:
            if converted.startswith('D'):
                return plc.batchread_wordunits(converted, size)
            else:
                return plc.batchread_bitunits(converted, size)
        except Exception as e:
            print(f"[PLC] read_device {dev_name}→{converted} error: {e}")
            return None

def write_device(dev_name, values):
    """
    Write to a PLC device. X/Y addresses are auto-converted from octal.
    Note: Writing to X (physical input) may be rejected by FX5U depending on 
    PLC settings. Use M addresses for internal control signals where possible.
    """
    if not connected:
        return False, "Not connected"
    converted = _convert_address(dev_name)
    with lock:
        try:
            if converted.startswith('D'):
                plc.batchwrite_wordunits(converted, values)
            else:
                plc.batchwrite_bitunits(converted, values)
            print(f"[PLC] write_device {dev_name}→{converted} = {values} ✓")
            return True, "ok"
        except Exception as e:
            err_msg = str(e)
            print(f"[PLC] write_device {dev_name}→{converted} error: {err_msg}")
            return False, err_msg

def pulse_device(dev_name, pulse_ms=200):
    """
    Send a pulse to a bit device: SET 1 → wait pulse_ms → SET 0.
    Used for X/M addresses that act as momentary switches (rising/falling edge triggers).
    Returns (success, message).
    """
    if not connected:
        return False, "Not connected"

    converted = _convert_address(dev_name)
    print(f"[PLC] pulse_device {dev_name}→{converted} pulse={pulse_ms}ms")

    # Step 1: SET = 1
    with lock:
        try:
            plc.batchwrite_bitunits(converted, [1])
            print(f"[PLC] pulse SET {converted}=1 ✓")
        except Exception as e:
            err = str(e)
            print(f"[PLC] pulse SET {converted}=1 FAILED: {err}")
            return False, f"SET=1 failed: {err}"

    # Wait
    _time.sleep(pulse_ms / 1000.0)

    # Step 2: RESET = 0
    with lock:
        try:
            plc.batchwrite_bitunits(converted, [0])
            print(f"[PLC] pulse RESET {converted}=0 ✓")
            return True, "ok"
        except Exception as e:
            err = str(e)
            print(f"[PLC] pulse RESET {converted}=0 FAILED: {err}")
            return False, f"SET=0 failed: {err}"