from datetime import datetime
from ..extensions import db

class CongViec(db.Model):
    __tablename__ = "cong_viec"

    id = db.Column(db.Integer, primary_key=True)
    ten_cong_viec = db.Column(db.String(255), nullable=False)
    mo_ta = db.Column(db.Text)
    trang_thai = db.Column(db.String(50), default="Chưa thực hiện")
    tien_do = db.Column(db.Float, default=0)
    uu_tien = db.Column(db.String(30), default="Trung bình")
    han_hoan_thanh = db.Column(db.Date)

    thoi_luong_ngay = db.Column(db.Integer, nullable=False, default=1)
    ngay_bat_dau_thuc_te = db.Column(db.Date)
    ngay_hoan_thanh_thuc_te = db.Column(db.Date)

    cong_trinh_id = db.Column(
        db.Integer,
        db.ForeignKey("cong_trinh.id"),
        nullable=False
    )
    nhan_su_id = db.Column(db.Integer, db.ForeignKey("nhan_su.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ten_cong_viec": self.ten_cong_viec,
            "mo_ta": self.mo_ta,
            "trang_thai": self.trang_thai,
            "tien_do": self.tien_do,
            "uu_tien": self.uu_tien,
            "han_hoan_thanh": self.han_hoan_thanh.isoformat() if self.han_hoan_thanh else None,

            "thoi_luong_ngay": self.thoi_luong_ngay,
            "ngay_bat_dau_thuc_te": self.ngay_bat_dau_thuc_te.isoformat() if self.ngay_bat_dau_thuc_te else None,
            "ngay_hoan_thanh_thuc_te": self.ngay_hoan_thanh_thuc_te.isoformat() if self.ngay_hoan_thanh_thuc_te else None,

            "cong_trinh_id": self.cong_trinh_id,
            "nhan_su_id": self.nhan_su_id
        }
