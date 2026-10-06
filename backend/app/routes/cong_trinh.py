from flask import Blueprint, request, jsonify
from datetime import date
from ..extensions import db
from ..models.cong_trinh import CongTrinh

from ..models.lich_lam_viec import LichLamViec
from ..services.tien_do_service import du_bao_cong_trinh

cong_trinh_bp = Blueprint("cong_trinh", __name__)

@cong_trinh_bp.get("")
def get_all():
    return jsonify([x.to_dict() for x in CongTrinh.query.order_by(CongTrinh.id.desc()).all()])

@cong_trinh_bp.get("/<int:item_id>")
def get_one(item_id):
    item = CongTrinh.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@cong_trinh_bp.post("")
def create():
    data = request.get_json() or {}
    item = CongTrinh(
        ma_cong_trinh=data.get("ma_cong_trinh", "").strip(),
        ten_cong_trinh=data.get("ten_cong_trinh", "").strip(),
        dia_diem=data.get("dia_diem"),
        chu_dau_tu=data.get("chu_dau_tu"),
        ngay_bat_dau=date.fromisoformat(data["ngay_bat_dau"]) if data.get("ngay_bat_dau") else None,
        ngay_ket_thuc_du_kien=date.fromisoformat(data["ngay_ket_thuc_du_kien"]) if data.get("ngay_ket_thuc_du_kien") else None,
        tien_do=float(data.get("tien_do", 0)),
        trang_thai=data.get("trang_thai", "Đang thi công")
    )
    if not item.ma_cong_trinh or not item.ten_cong_trinh:
        return jsonify({"message": "Mã và tên công trình là bắt buộc"}), 400

    db.session.add(item)
    db.session.commit()

    # Tạo lịch làm việc mặc định (Thứ 2 - Thứ 7)
    db.session.add(LichLamViec(cong_trinh_id=item.id, ngay_lam_viec=[0, 1, 2, 3, 4, 5]))
    db.session.commit()

    return jsonify(item.to_dict()), 201

@cong_trinh_bp.get("/<int:item_id>/tien-do")
def get_tien_do(item_id):
    item = CongTrinh.query.get_or_404(item_id)
    calendar = LichLamViec.query.filter_by(cong_trinh_id=item.id).first()
    if calendar is None:
        calendar = LichLamViec(cong_trinh_id=item.id, ngay_lam_viec=[0, 1, 2, 3, 4, 5])
        db.session.add(calendar)
        db.session.commit()
    try:
        return jsonify(du_bao_cong_trinh(item, calendar))
    except ValueError as error:
        return jsonify({"message": str(error)}), 409

@cong_trinh_bp.put("/<int:item_id>")
def update(item_id):
    item = CongTrinh.query.get_or_404(item_id)
    data = request.get_json() or {}
    for field in ["ma_cong_trinh", "ten_cong_trinh", "dia_diem", "chu_dau_tu", "trang_thai"]:
        if field in data:
            setattr(item, field, data[field])
    if "tien_do" in data:
        item.tien_do = float(data["tien_do"])
    if "ngay_bat_dau" in data:
        item.ngay_bat_dau = date.fromisoformat(data["ngay_bat_dau"]) if data["ngay_bat_dau"] else None
    if "ngay_ket_thuc_du_kien" in data:
        item.ngay_ket_thuc_du_kien = date.fromisoformat(data["ngay_ket_thuc_du_kien"]) if data["ngay_ket_thuc_du_kien"] else None
    db.session.commit()
    return jsonify(item.to_dict())

@cong_trinh_bp.delete("/<int:item_id>")
def delete(item_id):
    item = CongTrinh.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Đã xóa công trình"})