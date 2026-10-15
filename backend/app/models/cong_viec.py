from app.extensions import db

class CongViec(db.Model):
    __tablename__ = 'cong_viec'

    id = db.Column(db.Integer, primary_key=True)
    ten_cong_viec = db.Column(db.String(255), nullable=False)
    tu_ngay = db.Column(db.Date, nullable=False)
    den_ngay = db.Column(db.Date, nullable=False)
    
    # --- 3 TRƯỜNG MỚI ĐƯỢC THÊM CHO TÍNH NĂNG S-25 VÀ S-26 ---
    doi_thi_cong_id = db.Column(db.Integer, nullable=True)     # ID đội thi công được giao (S-25)
    khoi_luong_ke_hoach = db.Column(db.Float, default=0.0)     # Tổng khối lượng cần làm (S-26)
    is_critical = db.Column(db.Boolean, default=False)         # True: Công việc găng (S-26)