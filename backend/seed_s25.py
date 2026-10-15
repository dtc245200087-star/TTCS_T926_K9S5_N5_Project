from app import create_app
from app.extensions import db
from app.models.cong_viec import Team, CongViec
from datetime import datetime

app = create_app()

with app.app_context():
    # Xóa dữ liệu cũ nếu có
    db.session.query(CongViec).delete()
    db.session.query(Team).delete()
    db.session.commit()

    # 1. Tạo 2 Đội thi công
    team_a = Team(id=1, name="Đội Thi Công A", leader_id=101)
    team_b = Team(id=2, name="Đội Thi Công B", leader_id=102)
    db.session.add_all([team_a, team_b])
    db.session.commit()

    # Thời gian trùng nhau
    start_time = datetime(2026, 10, 20, 8, 0)
    end_time = datetime(2026, 10, 25, 17, 0)

    # 2. Tạo sẵn 4 công việc bị trùng thời gian cho Đội A
    for i in range(1, 5):
        task = CongViec(
            ten_cong_viec=f"Công việc trùng {i} của Đội A",
            tu_ngay=start_time,
            den_ngay=end_time,
            doi_id=team_a.id
        )
        db.session.add(task)

    # 3. Tạo 1 công việc mới chưa giao đội nào (Task ID = 5)
    new_task = CongViec(
        id=5,
        ten_cong_viec="Công việc mới cần phân công (S-25)",
        tu_ngay=start_time,
        den_ngay=end_time,
        doi_id=None
    )
    db.session.add(new_task)
    db.session.commit()

    print("--> NAP DU LIEU MAU THU NGHIEM S-25 THANH CONG!")