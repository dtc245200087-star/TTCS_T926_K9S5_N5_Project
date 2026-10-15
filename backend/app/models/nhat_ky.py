from app.extensions import db
from datetime import datetime

# Bảng lịch sử chuyển đổi đội thi công (S-25)
class LichSuPhanCong(db.Model):
    __tablename__ = 'lich_su_phan_cong'

    id = db.Column(db.Integer, primary_key=True)
    cong_viec_id = db.Column(db.Integer, db.ForeignKey('cong_viec.id'), nullable=False)
    doi_cu_id = db.Column(db.Integer, nullable=True)
    doi_moi_id = db.Column(db.Integer, nullable=False)
    nguoi_thuc_hien = db.Column(db.String(100), default="Chỉ huy trưởng")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Bảng báo cáo khối lượng làm theo ngày (S-26)
class NhatKyKhoiLuong(db.Model):
    __tablename__ = 'nhat_ky_khoi_luong'

    id = db.Column(db.Integer, primary_key=True)
    cong_viec_id = db.Column(db.Integer, db.ForeignKey('cong_viec.id'), nullable=False)
    khoi_luong_ngay = db.Column(db.Float, nullable=False)
    nguoi_bao_cao = db.Column(db.String(100), default="Đội trưởng")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Lưu mốc thời điểm báo cáo