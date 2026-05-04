import time
import plc_comm

plc_comm.connect_plc()

while True:
    try:
        data = plc_comm.read_words_device("D100", 2)

        if not data or len(data) < 2:
            print("NO DATA")
            continue

        low = data[0] & 0xFFFF
        high = data[1] & 0xFFFF

        raw = (high << 16) | low

        angle = raw / 1000
        angle = angle % 360

        # 🔥 map về 6 vị trí
        position = round(angle / 60) % 6

        print(f"ANGLE: {angle:.2f}° | POS: {position}")

    except Exception as e:
        print("ERROR:", e)

    time.sleep(0.2)