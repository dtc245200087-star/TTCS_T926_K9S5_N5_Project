from ..extensions import db

class NhanSu(db.Model):
    __tablename__ = "nhan_su"

    id = db.Column(db.Integer, primary_key=True)
    ho_ten = db.Column(db.String(150), nullable=False)
    chuc_vu = db.Column(db.String(100))
    so_dien_thoai = db.Column(db.String(30))
    email = db.Column(db.String(150))
    trang_thai = db.Column(db.String(50), default="Đang làm việc")

    cong_viec = db.relationship("CongViec", backref="nhan_su", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "ho_ten": self.ho_ten,
            "chuc_vu": self.chuc_vu,
            "so_dien_thoai": self.so_dien_thoai,
            "email": self.email,
            "trang_thai": self.trang_thai
        }
