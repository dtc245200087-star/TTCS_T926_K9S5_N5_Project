from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

from ..models import cong_viec as tasks
from ..models import nhat_ky as diaries
from .auth import login_required, roles_required

api = Blueprint("api", __name__)

cong_trinh = [
    {"id": 1, "ten": "Khu đô thị Bắc Sông Cầu", "dia_diem": "Thái Nguyên", "tien_do": 80, "trang_thai": "Đang thi công"},
    {"id": 2, "ten": "Tòa nhà văn phòng A1", "dia_diem": "Hà Nội", "tien_do": 60, "trang_thai": "Đang thi công"},
    {"id": 3, "ten": "Nhà máy sản xuất B2", "dia_diem": "Bắc Ninh", "tien_do": 95, "trang_thai": "Sắp hoàn thành"},
    {"id": 4, "ten": "Trường học Green School", "dia_diem": "Hải Phòng", "tien_do": 35, "trang_thai": "Mới khởi công"},
]

nhan_su = [
    {"id": 1, "ho_ten": "Nguyễn Văn An", "vai_tro": "Chỉ huy trưởng", "cong_trinh": "Khu đô thị Bắc Sông Cầu", "trang_thai": "Đang làm việc"},
    {"id": 2, "ho_ten": "Trần Minh Đức", "vai_tro": "Kỹ sư xây dựng", "cong_trinh": "Tòa nhà văn phòng A1", "trang_thai": "Đang làm việc"},
    {"id": 3, "ho_ten": "Lê Hoàng Nam", "vai_tro": "Giám sát công trình", "cong_trinh": "Nhà máy sản xuất B2", "trang_thai": "Đang làm việc"},
]

vat_tu = [
    {"id": 1, "ten": "Xi măng", "don_vi": "Tấn", "ton_kho": 125, "muc_toi_thieu": 50},
    {"id": 2, "ten": "Thép xây dựng", "don_vi": "Tấn", "ton_kho": 68, "muc_toi_thieu": 30},
    {"id": 3, "ten": "Cát xây dựng", "don_vi": "m³", "ton_kho": 24, "muc_toi_thieu": 40},
]

@api.get("/dashboard")
@login_required
def dashboard():
    return jsonify({
        "cong_trinh": len(cong_trinh),
        "dang_thi_cong": sum(x["trang_thai"] in ["Đang thi công", "Sắp hoàn thành"] for x in cong_trinh),
        "hoan_thanh": sum(x["tien_do"] >= 100 for x in cong_trinh),
        "nhan_su": len(nhan_su),
        "vat_tu_canh_bao": sum(x["ton_kho"] < x["muc_toi_thieu"] for x in vat_tu),
        "cong_trinh_data": cong_trinh,
        "cong_viec_hom_nay": tasks.list_tasks(current_app.config["USER_DATABASE"])
    })

@api.get("/cong-trinh")
@login_required
def get_cong_trinh():
    return jsonify(cong_trinh)

@api.post("/cong-trinh")
@roles_required("admin", "manager")
def add_cong_trinh():
    data = request.get_json() or {}
    item = {
        "id": max([x["id"] for x in cong_trinh], default=0) + 1,
        "ten": data.get("ten", "Công trình mới"),
        "dia_diem": data.get("dia_diem", ""),
        "tien_do": int(data.get("tien_do", 0)),
        "trang_thai": data.get("trang_thai", "Mới khởi công")
    }
    cong_trinh.append(item)
    return jsonify(item), 201

@api.get("/cong-viec")
@login_required
def get_cong_viec():
    return jsonify(tasks.list_tasks(current_app.config["USER_DATABASE"]))


@api.patch("/cong-viec/<int:task_id>")
@roles_required("admin", "manager", "engineer")
def update_cong_viec_progress(task_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_payload", "message": "Dữ liệu gửi lên không hợp lệ."}), 400

    start_date = data.get("ngay_bat_dau_thuc_te")
    end_date = data.get("ngay_ket_thuc_thuc_te")
    completion = data.get("phan_tram_hoan_thanh")

    for value, label in (
        (start_date, "Ngày bắt đầu thực tế"),
        (end_date, "Ngày kết thúc thực tế"),
    ):
        if value is not None:
            if not isinstance(value, str):
                return jsonify({"error": "invalid_date", "message": f"{label} không hợp lệ."}), 400
            try:
                if date.fromisoformat(value).isoformat() != value:
                    raise ValueError
            except ValueError:
                return jsonify({"error": "invalid_date", "message": f"{label} phải theo định dạng YYYY-MM-DD."}), 400

    if start_date and end_date and end_date < start_date:
        return jsonify({
            "error": "invalid_date_range",
            "message": "Ngày kết thúc thực tế không được trước ngày bắt đầu thực tế.",
        }), 400
    if isinstance(completion, bool) or not isinstance(completion, int) or not 0 <= completion <= 100:
        return jsonify({
            "error": "invalid_completion",
            "message": "Phần trăm hoàn thành phải là số nguyên từ 0 đến 100.",
        }), 400

    if not tasks.update_actual_progress(
        current_app.config["USER_DATABASE"], task_id, start_date, end_date, completion
    ):
        return jsonify({"error": "not_found", "message": "Không tìm thấy công việc."}), 404
    updated = next(
        task for task in tasks.list_tasks(current_app.config["USER_DATABASE"])
        if task["id"] == task_id
    )
    return jsonify(updated)

@api.get("/nhan-su")
@login_required
def get_nhan_su():
    return jsonify(nhan_su)

@api.get("/vat-tu")
@login_required
def get_vat_tu():
    return jsonify(vat_tu)

@api.get("/nhat-ky")
@login_required
def get_nhat_ky():
    diary_date = request.args.get("ngay")
    project = request.args.get("cong_trinh")
    work_item_id = request.args.get("cong_viec_id")
    if diary_date:
        try:
            if date.fromisoformat(diary_date).isoformat() != diary_date:
                raise ValueError
        except ValueError:
            return jsonify({"error": "invalid_date", "message": "Ngày phải theo định dạng YYYY-MM-DD."}), 400
    if project and project not in {item["ten"] for item in cong_trinh}:
        return jsonify({"error": "invalid_project", "message": "Công trình không hợp lệ."}), 400
    if work_item_id:
        if not work_item_id.isdigit():
            return jsonify({"error": "invalid_work_item", "message": "Hạng mục không hợp lệ."}), 400
        work_item_id = int(work_item_id)
    else:
        work_item_id = None

    return jsonify(diaries.list_entries(
        current_app.config["USER_DATABASE"],
        project=project,
        diary_date=diary_date,
        work_item_id=work_item_id,
    ))

@api.post("/nhat-ky")
@roles_required("admin", "manager", "engineer")
def add_nhat_ky():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_payload", "message": "Dữ liệu gửi lên không hợp lệ."}), 400

    project = data.get("cong_trinh")
    diary_date = data.get("ngay")
    work_item_id = data.get("cong_viec_id")
    entry_time = data.get("gio")
    description = data.get("noi_dung")
    if not isinstance(project, str) or project not in {item["ten"] for item in cong_trinh}:
        return jsonify({"error": "invalid_project", "message": "Hãy chọn công trình hợp lệ."}), 400
    if not isinstance(diary_date, str):
        return jsonify({"error": "invalid_date", "message": "Ngày nhật ký là bắt buộc."}), 400
    try:
        if date.fromisoformat(diary_date).isoformat() != diary_date:
            raise ValueError
    except ValueError:
        return jsonify({"error": "invalid_date", "message": "Ngày phải theo định dạng YYYY-MM-DD."}), 400
    if isinstance(work_item_id, bool) or not str(work_item_id).isdigit():
        return jsonify({"error": "invalid_work_item", "message": "Mỗi mục nhật ký phải gắn với một hạng mục."}), 400
    work_item_id = int(work_item_id)
    task = next((item for item in tasks.list_tasks(current_app.config["USER_DATABASE"]) if item["id"] == work_item_id), None)
    if not task or task.get("cong_trinh") != project:
        return jsonify({"error": "invalid_work_item", "message": "Hạng mục không thuộc công trình đã chọn."}), 400
    if not isinstance(entry_time, str):
        return jsonify({"error": "invalid_time", "message": "Giờ ghi nhận là bắt buộc."}), 400
    try:
        if datetime.strptime(entry_time, "%H:%M").strftime("%H:%M") != entry_time:
            raise ValueError
    except ValueError:
        return jsonify({"error": "invalid_time", "message": "Giờ ghi nhận phải theo định dạng HH:MM."}), 400
    if not isinstance(description, str) or not description.strip() or len(description.strip()) > 5000:
        return jsonify({"error": "invalid_description", "message": "Nội dung công việc là bắt buộc và tối đa 5000 ký tự."}), 400

    entry = diaries.create_entry(
        current_app.config["USER_DATABASE"],
        project=project,
        diary_date=diary_date,
        task_id=work_item_id,
        entry_time=entry_time,
        description=description.strip(),
        user_id=request.current_user["id"],
    )
    return jsonify(entry), 201
