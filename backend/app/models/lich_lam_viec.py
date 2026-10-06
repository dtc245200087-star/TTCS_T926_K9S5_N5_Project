from datetime import date
from ..extensions import db


class LichLamViec(db.Model):
    __tablename__ = "calendars"

    id = db.Column(db.Integer, primary_key=True)
    cong_trinh_id = db.Column(db.Integer, db.ForeignKey("cong_trinh.id", ondelete="CASCADE"), nullable=False, unique=True)
    ngay_lam_viec = db.Column(db.JSON, nullable=False, default=lambda: [0, 1, 2, 3, 4, 5])
    cong_trinh = db.relationship("CongTrinh", backref=db.backref("lich_lam_viec", uselist=False, cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            "id": self.id,
            "cong_trinh_id": self.cong_trinh_id,
            "ten_cong_trinh": self.cong_trinh.ten_cong_trinh,
            "ngay_lam_viec": self.ngay_lam_viec,
            "ngay_nghi": [holiday.to_dict() for holiday in sorted(self.ngay_nghi, key=lambda item: item.ngay)],
        }


class NgayNghi(db.Model):
    __tablename__ = "holidays"

    id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey("calendars.id", ondelete="CASCADE"), nullable=False, index=True)
    ngay = db.Column(db.Date, nullable=False)
    ten = db.Column(db.String(120), nullable=False)
    lich = db.relationship("LichLamViec", backref=db.backref("ngay_nghi", cascade="all, delete-orphan", lazy=True))
    __table_args__ = (db.UniqueConstraint("calendar_id", "ngay", name="uq_holidays_calendar_date"),)

    def to_dict(self):
        return {"id": self.id, "ngay": self.ngay.isoformat(), "ten": self.ten}


class CongViecPhuThuoc(db.Model):
    __tablename__ = "cong_viec_phu_thuoc"

    cong_viec_id = db.Column(db.Integer, db.ForeignKey("cong_viec.id", ondelete="CASCADE"), primary_key=True)
    tien_quyet_id = db.Column(db.Integer, db.ForeignKey("cong_viec.id", ondelete="CASCADE"), primary_key=True)
