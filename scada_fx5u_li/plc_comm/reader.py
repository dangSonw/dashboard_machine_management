import plc_comm.connection as conn


# ================= READ WORD =================
def read_words():
    client = conn.get_client()
    if client is None:
        return None

    with conn.lock:
        try:
            data = client.batchread_wordunits("D6", 15)
            return {
                "cycle": data[0],
                "in": data[4],
                "out": data[6],
                "ok": data[8],
                "ng": data[10],
                "rate": data[14],
            }

        except Exception as e:
            print("READ ERROR:", e)
            return None


# ================= READ BIT M900 =================
def read_all_bits():
    client = conn.get_client()
    if client is None:
        return None

    with conn.lock:
        try:
            # 🔥 đọc M900 → M949
            bits = client.batchread_bitunits("M900", 50)
            return bits if bits else None

        except Exception as e:
            print("READ BIT ERROR:", e)
            return None

# ================= READ FAULT =================
def read_fault():
    bits = read_all_bits()

    if not bits or len(bits) < 20:
        return False, False

    try:
        # ví dụ fault map
        fault1 = bits[16]   # M916
        fault2 = bits[17]   # M917
        return fault1, fault2

    except Exception as e:
        print("READ FAULT ERROR:", e)
        return False, False

# ================= READ WORD DEVICE =================
def read_words_device(device, size):
    client = conn.get_client()
    if client is None:
        return None

    with conn.lock:
        try:
            return client.batchread_wordunits(device, size)

        except Exception as e:
            print("READ DEVICE ERROR:", e)
            return None


# ================= READ DWORD =================
def read_dword(device):
    data = read_words_device(device, 2)

    if not data or len(data) < 2:
        return 0

    low = data[0]
    high = data[1]

    return (high << 16) | low
# thêm code hiển thị đèn
def read_machine_bits(device=None, size=None):
    return read_all_bits()


# ================= READ BIT DEVICE =================
def read_bits_device(device, size):
    """Đọc bit units theo device cụ thể (M0, M303, ...)"""
    client = conn.get_client()
    if client is None:
        return None

    with conn.lock:
        try:
            return client.batchread_bitunits(device, size)

        except Exception as e:
            print("READ BITS DEVICE ERROR:", e)
            return None