import plc_comm.connection as conn


# ================= CONVERT ADDRESS (OCTAL X/Y → HEX) =================
def _convert_address(dev_name):
    """
    FX5U X/Y địa chỉ là octal, pymcprotocol cần hex.
    Ví dụ: X111 (octal) → X049 (hex)
    M/D giữ nguyên (decimal).
    """
    if dev_name and dev_name[0] in ('X', 'Y'):
        try:
            prefix = dev_name[0]
            num_str = dev_name[1:]
            decimal_val = int(num_str, 8)   # đọc là octal
            hex_str = format(decimal_val, '03X')
            converted = f"{prefix}{hex_str}"
            print(f"[SCADA] Convert: {dev_name} (oct) → {converted} (hex)")
            return converted
        except ValueError:
            return dev_name
    return dev_name


# ================= WRITE BIT =================
def write_bit(device, value):
    client = conn.get_client()
    if client is None:
        return False

    converted = _convert_address(device)

    with conn.lock:
        try:
            client.batchwrite_bitunits(converted, [value])
            return True

        except Exception as e:
            print("WRITE BIT ERROR:", e)
            return False


# ================= WRITE PULSE =================
def write_pulse(device):
    client = conn.get_client()
    if client is None:
        return False

    converted = _convert_address(device)

    with conn.lock:
        try:
            client.batchwrite_bitunits(converted, [1])
            client.batchwrite_bitunits(converted, [0])
            return True

        except Exception as e:
            print("WRITE PULSE ERROR:", e)
            return False

# ================= WRITE WORD (D register) =================
def write_word(device, value):
    client = conn.get_client()
    if client is None:
        return False
    with conn.lock:
        try:
            client.batchwrite_wordunits(device, [int(value)])
            print(f'[SCADA] write_word {device} = {value} OK')
            return True
        except Exception as e:
            print(f'WRITE WORD ERROR ({device}):', e)
            return False
