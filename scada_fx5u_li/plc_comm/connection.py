from pymcprotocol import Type3E
import threading
import time

_plc = None
connected = False
lock = threading.Lock()

last_connect_time = 0
RECONNECT_DELAY = 3  # seconds


# ================= CONNECT =================
def connect_plc(ip="192.168.1.10", port=5008):
    global _plc, connected, last_connect_time

    with lock:
        try:
            plc = Type3E()
            plc.setaccessopt(commtype="binary")
            plc.timer = 2

            plc.connect(ip, port)

            _plc = plc
            connected = True

            print("PLC CONNECTED")
            return True

        except Exception as e:
            connected = False
            last_connect_time = time.time()
            print("PLC CONNECTION FAILED:", e)
            return False


# ================= ENSURE =================
def ensure_connection():
    global connected, last_connect_time

    if connected:
        return True

    if time.time() - last_connect_time < RECONNECT_DELAY:
        return False

    return connect_plc()


# ================= GET CLIENT =================
def get_client():
    if ensure_connection():
        return _plc
    return None