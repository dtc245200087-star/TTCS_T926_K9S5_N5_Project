from flask import Blueprint, request, jsonify
from datetime import date
from ..extensions import db
from ..models.cong_viec import CongViec
from ..models.cong_trinh import CongTrinh
from ..models.lich_lam_viec import CongViecPhuThuoc, LichLamViec
from ..services.tien_do_service import du_bao_cong_trinh

cong_viec_bp = Blueprint("cong_viec", __name__)

@cong_viec_bp.get("")
def get_all():
    items = []
    try:
        for project in CongTrinh.query.order_by(CongTrinh.id).all():
            calendar = LichLamViec.query.filter_by(cong_trinh_id=project.id).first()
            if calendar is None:
                calendar = LichLamViec(cong_trinh_id=project.id, ngay_lam_viec=[0, 1, 2, 3, 4, 5])
                db.session.add(calendar)
                db.session.commit()
            items.extend(du_bao_cong_trinh(project, calendar)["cong_viec"])
    except ValueError as error:
        return jsonify({"message": str(error)}), 409
    return jsonify(sorted(items, key=lambda item: item["id"], reverse=True))

@cong_viec_bp.post("")
def create():
    data = request.get_json() or {}
    try:
        duration = int(data.get("thoi_luong_ngay", 1))
        progress = float(data.get("tien_do", 0))
        planned_finish = date.fromisoformat(data["han_hoan_thanh"]) if data.get("han_hoan_thanh") else None
        actual_start = date.fromisoformat(data["ngay_bat_dau_thuc_te"]) if data.get("ngay_bat_dau_thuc_te") else None
        actual_finish = date.fromisoformat(data["ngay_hoan_thanh_thuc_te"]) if data.get("ngay_hoan_thanh_thuc_te") else None
    except (TypeError, ValueError):
        return jsonify({"message": "Ngày cần theo định dạng YYYY-MM-DD; thời lượng và tiến độ cần là số hợp lệ."}), 400
    item = CongViec(
        ten_cong_viec=data.get("ten_cong_viec", "").strip(),
        mo_ta=data.get("mo_ta"),
        trang_thai=data.get("trang_thai", "Chưa thực hiện"),
        tien_do=progress,
        uu_tien=data.get("uu_tien", "Trung bình"),
        han_hoan_thanh=planned_finish,
        thoi_luong_ngay=duration,
        ngay_bat_dau_thuc_te=actual_start,
        ngay_hoan_thanh_thuc_te=actual_finish,
        cong_trinh_id=data.get("cong_trinh_id"),
        nhan_su_id=data.get("nhan_su_id")
    )
    if not item.ten_cong_viec or not item.cong_trinh_id:
        return jsonify({"message": "Tên công việc và công trình là bắt buộc."}), 400
    if item.thoi_luong_ngay < 1 or not 0 <= item.tien_do <= 100:
        return jsonify({"message": "Thời lượng cần từ 1 ngày; tiến độ cần trong khoảng 0 đến 100%."}), 400
    if item.tien_do == 100 and not item.ngay_hoan_thanh_thuc_te:
        item.ngay_hoan_thanh_thuc_te = date.today()
        item.trang_thai = "Hoàn thành"
    elif item.ngay_hoan_thanh_thuc_te:
        item.tien_do = 100
        item.trang_thai = "Hoàn thành"
    elif item.ngay_bat_dau_thuc_te or item.tien_do > 0:
        item.trang_thai = "Đang thực hiện"
    db.session.add(item)
    db.session.commit()
    predecessors = data.get("phu_thuoc", [])
    validation_error = _validate_predecessors(item, predecessors)
    if validation_error:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": validation_error}), 400
    db.session.add_all([CongViecPhuThuoc(cong_viec_id=item.id, tien_quyet_id=predecessor_id) for predecessor_id in predecessors])
    db.session.commit()
    return jsonify(_serialize(item)), 201

@cong_viec_bp.put("/<int:item_id>")
def update(item_id):
    item = CongViec.query.get_or_404(item_id)
    data = request.get_json() or {}
    for field in ["ten_cong_viec", "mo_ta", "trang_thai", "uu_tien", "cong_trinh_id", "nhan_su_id"]:
        if field in data:
            setattr(item, field, data[field])
    if "tien_do" in data:
        try:
            item.tien_do = float(data["tien_do"])
        except (TypeError, ValueError):
            return jsonify({"message": "Tiến độ cần là số từ 0 đến 100%."}), 400
    if "han_hoan_thanh" in data:
        try:
            item.han_hoan_thanh = date.fromisoformat(data["han_hoan_thanh"]) if data["han_hoan_thanh"] else None
        except (TypeError, ValueError):
            return jsonify({"message": "Hạn hoàn thành cần theo định dạng YYYY-MM-DD."}), 400
    for field in ["thoi_luong_ngay"]:
        if field in data:
            try:
                duration = int(data[field])
            except (TypeError, ValueError):
                return jsonify({"message": "Thời lượng cần là số ngày làm việc từ 1 trở lên."}), 400
            if duration < 1:
                return jsonify({"message": "Thời lượng cần là số ngày làm việc từ 1 trở lên."}), 400
            item.thoi_luong_ngay = duration
    if "ngay_bat_dau_thuc_te" in data:
        try:
            item.ngay_bat_dau_thuc_te = date.fromisoformat(data["ngay_bat_dau_thuc_te"]) if data["ngay_bat_dau_thuc_te"] else None
        except (TypeError, ValueError):
            return jsonify({"message": "Ngày bắt đầu thực tế cần theo định dạng YYYY-MM-DD."}), 400
    if "ngay_hoan_thanh_thuc_te" in data:
        try:
            item.ngay_hoan_thanh_thuc_te = date.fromisoformat(data["ngay_hoan_thanh_thuc_te"]) if data["ngay_hoan_thanh_thuc_te"] else None
        except (TypeError, ValueError):
            return jsonify({"message": "Ngày hoàn thành thực tế cần theo định dạng YYYY-MM-DD."}), 400
    if item.ngay_hoan_thanh_thuc_te:
        item.tien_do = 100
        item.trang_thai = "Hoàn thành"
    elif item.ngay_bat_dau_thuc_te or item.tien_do > 0:
        item.trang_thai = "Đang thực hiện"
    elif "ngay_hoan_thanh_thuc_te" in data or "ngay_bat_dau_thuc_te" in data:
        item.trang_thai = "Chưa thực hiện"
    if not 0 <= item.tien_do <= 100:
        return jsonify({"message": "Tiến độ cần nằm trong khoảng 0 đến 100%."}), 400
    if item.tien_do == 100 and not item.ngay_hoan_thanh_thuc_te:
        item.ngay_hoan_thanh_thuc_te = date.today()
    if "phu_thuoc" in data:
        validation_error = _validate_predecessors(item, data["phu_thuoc"])
        if validation_error:
            return jsonify({"message": validation_error}), 400
        CongViecPhuThuoc.query.filter_by(cong_viec_id=item.id).delete()
        db.session.add_all([CongViecPhuThuoc(cong_viec_id=item.id, tien_quyet_id=predecessor_id) for predecessor_id in data["phu_thuoc"]])
    db.session.commit()
    return jsonify(_serialize(item))

def _serialize(item):
    data = item.to_dict()
    data["phu_thuoc"] = [relation.tien_quyet_id for relation in CongViecPhuThuoc.query.filter_by(cong_viec_id=item.id).all()]
    return data

def _validate_predecessors(item, predecessors):
    if not isinstance(predecessors, list) or any(type(value) is not int for value in predecessors) or len(set(predecessors)) != len(predecessors):
        return "Danh sách công việc tiên quyết không hợp lệ."
    if item.id in predecessors:
        return "Công việc không thể phụ thuộc vào chính nó."
    valid_ids = {task.id for task in CongViec.query.filter_by(cong_trinh_id=item.cong_trinh_id).all()}
    if any(value not in valid_ids for value in predecessors):
        return "Công việc tiên quyết phải thuộc cùng công trình."
    graph = {task_id: set() for task_id in valid_ids}
    for relation in CongViecPhuThuoc.query.filter(CongViecPhuThuoc.cong_viec_id.in_(valid_ids)).all() if valid_ids else []:
        if relation.cong_viec_id != item.id:
            graph[relation.cong_viec_id].add(relation.tien_quyet_id)
    graph[item.id] = set(predecessors)
    successors = {key: [] for key in graph}
    remaining = {key: len(value) for key, value in graph.items()}
    for task_id, task_predecessors in graph.items():
        for predecessor_id in task_predecessors:
            successors[predecessor_id].append(task_id)
    ready = [key for key, count in remaining.items() if count == 0]
    visited = 0
    while ready:
        task_id = ready.pop()
        visited += 1
        for successor_id in successors[task_id]:
            remaining[successor_id] -= 1
            if remaining[successor_id] == 0:
                ready.append(successor_id)
    return None if visited == len(graph) else "Mối phụ thuộc tạo thành chu trình trong mạng công việc."

@cong_viec_bp.delete("/<int:item_id>")
def delete(item_id):
    item = CongViec.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Đã xóa công việc"})
