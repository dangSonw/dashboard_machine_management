import plc_comm


class CarouselCore:

    def __init__(self):
        self.sensors = [
            {"id": "0", "label": "GỐC"},
            {"id": "1", "label": "Phải 1"},
            {"id": "2", "label": "Phải 2"},
            {"id": "3", "label": "Đối"},
            {"id": "4", "label": "Trái 2"},
            {"id": "5", "label": "Trái 1"},
        ]

    # ================= ROTATION =================
    def get_rotation(self):
        """
        🔥 Logic:
        - Chưa có PLC → 0°
        - Có PLC → dùng angle_std (0,60,120...)
        - Nếu M111 hoặc M500 ON → về gốc (0°)
        """

        # ===== DEFAULT =====
        angle_std = 0

        try:
            # ===== LẤY GÓC CHUẨN =====
            if hasattr(plc_comm, "latest_angle_std"):
                angle_std = plc_comm.latest_angle_std

            # ===== CHECK VỀ GỐC =====
            m = getattr(plc_comm, "latest_m", [0, 0])

            if len(m) >= 2:
                M111 = m[0]
                M500 = m[1]

                if M111 == 1 or M500 == 1:
                    return 0

        except Exception as e:
            print("ROTATION ERROR:", e)

        return angle_std

    # ================= POSITION =================
    def get_position(self):
        """
        🔥 trả về vị trí 0 → 5
        """
        try:
            return getattr(plc_comm, "latest_pos", 0)
        except:
            return 0

    # ================= LED STATE =================
    def get_station_state(self, index):
        """
        🔥 đọc trạng thái đèn từ D7000
        """
        words = getattr(plc_comm, "latest_d7000", [])

        if not words or len(words) < 6:
            return (False, False, False)

        value = words[index]

        yellow = (value >> 1) & 1
        green  = (value >> 3) & 1
        red    = (value >> 5) & 1

        return red, yellow, green