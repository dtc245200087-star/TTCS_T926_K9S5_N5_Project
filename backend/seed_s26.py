import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models.cong_viec import CongViec
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    t1 = CongViec(
        ten_cong_viec="Đào hố móng trụ T1 (Công việc găng)",
        tu_ngay=datetime.now(),
        den_ngay=datetime.now() + timedelta(days=5),
        doi_id=1
    )
    if hasattr(t1, 'la_cong_viec_gang'):
        t1.la_cong_viec_gang = True
    if hasattr(t1, 'khoi_luong_tong'):
        t1.khoi_luong_tong = 100
    if hasattr(t1, 'khoi_luong_luy_ke'):
        t1.khoi_luong_luy_ke = 80

    db.session.add(t1)
    db.session.commit()
    print(f"Đã tạo dữ liệu mẫu S-26 thành công với Task ID = {t1.id}")