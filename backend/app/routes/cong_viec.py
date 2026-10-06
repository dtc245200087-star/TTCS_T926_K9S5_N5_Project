from flask import Blueprint, request, jsonify
from datetime import date
from ..extensions import db
from ..models.cong_viec import CongViec

cong_viec_bp = Blueprint("cong_viec", __name__)

@cong_viec_bp.get("")
def get_all():
    return jsonify([x.to_dict() for x in CongViec.query.order_by(CongViec.id.desc()).all()])

@cong_viec_bp.post("")
def create():
    data = request.get_json() or {}
    item = CongViec(
        ten_cong_viec=data.get("ten_cong_viec", "").strip(),
        mo_ta=data.get("mo_ta"),
        trang_thai=data.get("trang_thai", "Chưa thực hiện"),
        tien_do=float(data.get("tien_do", 0)),
        uu_tien=data.get("uu_tien", "Trung bình"),
        han_hoan_thanh=date.fromisoformat(data["han_hoan_thanh"]) if data.get("han_hoan_thanh") else None,
        cong_trinh_id=data.get("cong_trinh_id"),
        nhan_su_id=data.get("nhan_su_id")
    )
    if not item.ten_cong_viec or not item.cong_trinh_id:
        return jsonify({"message": "Tên công việc và công trình là bắt buộc"}), 400
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@cong_viec_bp.put("/<int:item_id>")
def update(item_id):
    item = CongViec.query.get_or_404(item_id)
    data = request.get_json() or {}
    for field in ["ten_cong_viec", "mo_ta", "trang_thai", "uu_tien", "cong_trinh_id", "nhan_su_id"]:
        if field in data:
            setattr(item, field, data[field])
    if "tien_do" in data:
        item.tien_do = float(data["tien_do"])
    if "han_hoan_thanh" in data:
        item.han_hoan_thanh = date.fromisoformat(data["han_hoan_thanh"]) if data["han_hoan_thanh"] else None
    db.session.commit()
    return jsonify(item.to_dict())

@cong_viec_bp.delete("/<int:item_id>")
def delete(item_id):
    item = CongViec.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Đã xóa công việc"})
