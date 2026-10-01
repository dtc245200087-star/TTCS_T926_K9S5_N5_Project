from datetime import datetime
from ..extensions import db

class CongTrinh(db.Model):
    __tablename__ = "cong_trinh"

    id = db.Column(db.Integer, primary_key=True)
    ma_cong_trinh = db.Column(db.String(50), unique=True, nullable=False)
    ten_cong_trinh = db.Column(db.String(255), nullable=False)
    dia_diem = db.Column(db.String(255))
    chu_dau_tu = db.Column(db.String(255))
    ngay_bat_dau = db.Column(db.Date)
    ngay_ket_thuc_du_kien = db.Column(db.Date)
    tien_do = db.Column(db.Float, default=0)
    trang_thai = db.Column(db.String(50), default="Đang thi công")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cong_viec = db.relationship(
        "CongViec",
        backref="cong_trinh",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "ma_cong_trinh": self.ma_cong_trinh,
            "ten_cong_trinh": self.ten_cong_trinh,
            "dia_diem": self.dia_diem,
            "chu_dau_tu": self.chu_dau_tu,
            "ngay_bat_dau": self.ngay_bat_dau.isoformat() if self.ngay_bat_dau else None,
            "ngay_ket_thuc_du_kien": self.ngay_ket_thuc_du_kien.isoformat() if self.ngay_ket_thuc_du_kien else None,
            "tien_do": self.tien_do,
            "trang_thai": self.trang_thai
        }
