import plc_comm

def get_pie_data():
    try:
        data = plc_comm.read_words_device("D14", 3)

        ok = data[0]
        ng = data[2]

        return ok, ng

    except Exception as e:
        print("PIE ERROR:", e)
        return 0, 0