import threading
import time
import plc_comm


def plc_worker():
    while True:
        try:
            # ===== CHECK CONNECTION =====
            if not plc_comm.is_connected():
                time.sleep(1)
                continue

            # ================= READ DATA =================
            try:
                plc_comm.latest_data = plc_comm.read_words()
            except Exception as e:
                print("READ DATA ERROR:", e)
                plc_comm.latest_data = []

            # ================= READ BITS =================
            try:
                plc_comm.latest_bits = plc_comm.read_machine_bits("M900", 30)
            except Exception as e:
                print("READ BITS ERROR:", e)
                plc_comm.latest_bits = []

            # ================= READ FAULT =================
            try:
                plc_comm.latest_fault = plc_comm.read_fault()
            except Exception as e:
                print("READ FAULT ERROR:", e)
                plc_comm.latest_fault = None

            # ================= READ ANGLE =================
            try:
                data_angle = plc_comm.read_words_device("D100", 2)

                if isinstance(data_angle, list) and len(data_angle) >= 2:
                    low = data_angle[0] & 0xFFFF
                    high = data_angle[1] & 0xFFFF

                    raw = (high << 16) | low

                    angle = (raw / 1000.0) % 360

                    # ===== GÓC CHUẨN =====
                    angle_std = (int((angle + 30) // 60) * 60) % 360

                    # ===== POS =====
                    pos = int(angle_std // 60)

                    # ===== SAVE =====
                    plc_comm.latest_angle = angle
                    plc_comm.latest_angle_std = angle_std
                    plc_comm.latest_pos = pos
                else:
                    raise ValueError("Invalid angle data")

            except Exception as e:
                print("ANGLE ERROR:", e)
                plc_comm.latest_angle = 0
                plc_comm.latest_angle_std = 0
                plc_comm.latest_pos = 0

            # ================= READ D7000 =================
            try:
                plc_comm.latest_d7000 = plc_comm.read_words_device("D7000", 6)
            except Exception as e:
                print("D7000 ERROR:", e)
                plc_comm.latest_d7000 = []

            # ================= READ M111 =================
            try:
                plc_comm.latest_m = plc_comm.read_machine_bits("M111", 2)
            except Exception as e:
                print("READ M ERROR:", e)
                plc_comm.latest_m = []

            # ================= READ MODE BITS =================
            try:
                mode_devices = ["M0", "M303", "M312", "M315", "M500"]
                for dev in mode_devices:
                    val = plc_comm.read_bits_device(dev, 1)
                    plc_comm.latest_m_modes[dev] = val[0] if val else 0
            except Exception as e:
                print("READ MODE BITS ERROR:", e)

            # ================= DEBUG =================
            print(
                f"ANGLE: {round(plc_comm.latest_angle, 2)} | "
                f"STD: {plc_comm.latest_angle_std} | "
                f"POS: {plc_comm.latest_pos}"
            )

        except Exception as e:
            print("PLC THREAD CRASH:", e)

        time.sleep(0.3)


def start_plc_thread():
    t = threading.Thread(target=plc_worker, daemon=True)
    t.start()
    return t