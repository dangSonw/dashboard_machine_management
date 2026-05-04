import plc_comm
import time

history = []

def get_productivity():
    try:
        data = plc_comm.read_words_device("D14", 3)

        ok = data[0]
        ng = data[2]

        total = ok + ng

        # lưu theo phút
        current_hour = time.strftime("%H:%M")

        history.append((current_hour, total))

        if len(history) > 3:
            history.pop(0)

        return total, history

    except Exception as e:
        print("PROD ERROR:", e)
        return 0, history