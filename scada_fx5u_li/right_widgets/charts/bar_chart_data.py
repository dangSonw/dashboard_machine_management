import random
import plc_comm

# ================= GLOBAL =================
last_ng = 0
defect_counts = [0]*6

# bật chế độ test nếu PLC chưa chạy
TEST_MODE = False

def get_bar_data():
    global last_ng, defect_counts

    try:
        # ===== TEST MODE =====
        if TEST_MODE:
            index = random.randint(0, 5)
            defect_counts[index] += 1
            return defect_counts

        # ===== READ PLC =====
        data = plc_comm.read_words_device("D16", 1)

        if not data:
            return defect_counts

        ng = data[0]

        # ===== TÍNH DELTA (QUAN TRỌNG NHẤT) =====
        delta = ng - last_ng

        if delta > 0:
            for _ in range(delta):
                index = random.randint(0, 5)
                defect_counts[index] += 1

            last_ng = ng

        return defect_counts

    except Exception as e:
        print("BAR ERROR:", e)
        return defect_counts