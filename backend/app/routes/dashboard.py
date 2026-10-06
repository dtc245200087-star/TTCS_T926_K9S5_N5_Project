from flask import Blueprint, jsonify
from ..models.cong_trinh import CongTrinh
from ..models.cong_viec import CongViec
from ..models.nhan_su import NhanSu

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.get("")
def dashboard():
    cong_trinh = CongTrinh.query.all()
    cong_viec = CongViec.query.all()
    return jsonify({
        "tong_cong_trinh": len(cong_trinh),
        "dang_thi_cong": sum(x.trang_thai == "Đang thi công" for x in cong_trinh),
        "hoan_thanh": sum(x.trang_thai == "Hoàn thành" for x in cong_trinh),
        "tong_cong_viec": len(cong_viec),
        "cong_viec_hoan_thanh": sum(x.trang_thai == "Hoàn thành" for x in cong_viec),
        "tong_nhan_su": NhanSu.query.count(),
        "tien_do_trung_binh": round(
            sum(x.tien_do for x in cong_trinh) / len(cong_trinh), 1
        ) if cong_trinh else 0
    })
