from flask import Blueprint, current_app, jsonify, request
from datetime import date, datetime
import re
from .auth import login_required, roles_required
from ..models import nhat_ky as diary

api = Blueprint("api", __name__)

cong_trinh = [
    {"id": 1, "ten": "Khu đô thị Bắc Sông Cầu", "dia_diem": "Thái Nguyên", "tien_do": 80, "trang_thai": "Đang thi công"},
    {"id": 2, "ten": "Tòa nhà văn phòng A1", "dia_diem": "Hà Nội", "tien_do": 60, "trang_thai": "Đang thi công"},
    {"id": 3, "ten": "Nhà máy sản xuất B2", "dia_diem": "Bắc Ninh", "tien_do": 95, "trang_thai": "Sắp hoàn thành"},
    {"id": 4, "ten": "Trường học Green School", "dia_diem": "Hải Phòng", "tien_do": 35, "trang_thai": "Mới khởi công"},
]

cong_viec = [
    {"id": 1, "ten": "Đổ bê tông móng", "cong_trinh": "Khu đô thị Bắc Sông Cầu", "nguoi_phu_trach": "Nguyễn Văn An", "trang_thai": "Đang thực hiện", "han": "2026-10-05"},
    {"id": 2, "ten": "Lắp đặt cốt thép", "cong_trinh": "Tòa nhà văn phòng A1", "nguoi_phu_trach": "Trần Minh Đức", "trang_thai": "Hoàn thành", "han": "2026-10-02"},
    {"id": 3, "ten": "Kiểm tra vật tư", "cong_trinh": "Nhà máy sản xuất B2", "nguoi_phu_trach": "Lê Hoàng Nam", "trang_thai": "Chờ xử lý", "han": "2026-10-04"},
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

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def valid_day(value):
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def diary_database():
    return current_app.config["USER_DATABASE"]


def diary_locked_response():
    return jsonify({"error": "diary_day_locked", "message": "Nhật ký ngày này đã khóa sổ. Hãy yêu cầu quản lý mở khóa trước khi sửa."}), 423

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
        "cong_viec_hom_nay": cong_viec
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
    return jsonify(cong_viec)

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
    return jsonify(diary.list_entries(diary_database()))

@api.post("/nhat-ky")
@roles_required("admin", "manager", "engineer")
def add_nhat_ky():
    data = request.get_json() or {}
    day = data.get("ngay", datetime.now().strftime("%Y-%m-%d"))
    project = data.get("cong_trinh")
    content = data.get("noi_dung")
    if not valid_day(day):
        return jsonify({"error": "invalid_date", "message": "Ngày nhật ký không hợp lệ."}), 400
    if not isinstance(project, str) or not project.strip() or len(project.strip()) > 255:
        return jsonify({"error": "invalid_project", "message": "Tên công trình là bắt buộc và tối đa 255 ký tự."}), 400
    if not isinstance(content, str) or not content.strip() or len(content.strip()) > 10000:
        return jsonify({"error": "invalid_content", "message": "Nội dung nhật ký là bắt buộc và tối đa 10.000 ký tự."}), 400
    user = request.current_user
    entry_id = diary.add_entry(
        diary_database(), day=day, project=project.strip(), content=content.strip(),
        author=user["full_name"], author_id=user["id"],
    )
    if entry_id is None:
        return diary_locked_response()
    return jsonify(next(item for item in diary.list_entries(diary_database()) if item["id"] == entry_id)), 201


@api.patch("/nhat-ky/<int:entry_id>")
@roles_required("admin", "manager", "engineer")
def edit_nhat_ky(entry_id):
    data = request.get_json(silent=True)
    data = data if isinstance(data, dict) else {}
    project = data.get("cong_trinh")
    content = data.get("noi_dung")
    if not isinstance(project, str) or not project.strip() or len(project.strip()) > 255:
        return jsonify({"error": "invalid_project", "message": "Tên công trình là bắt buộc và tối đa 255 ký tự."}), 400
    if not isinstance(content, str) or not content.strip() or len(content.strip()) > 10000:
        return jsonify({"error": "invalid_content", "message": "Nội dung nhật ký là bắt buộc và tối đa 10.000 ký tự."}), 400
    result = diary.update_entry(diary_database(), entry_id, project=project.strip(), content=content.strip())
    if result == "not_found":
        return jsonify({"error": "not_found", "message": "Không tìm thấy nhật ký."}), 404
    if result == "locked":
        return diary_locked_response()
    return jsonify(next(item for item in diary.list_entries(diary_database()) if item["id"] == entry_id))


@api.post("/nhat-ky/ngay/<day>/lock")
@roles_required("admin", "manager", "engineer")
def lock_nhat_ky_day(day):
    if not valid_day(day):
        return jsonify({"error": "invalid_date", "message": "Ngày nhật ký không hợp lệ."}), 400
    user = request.current_user
    if not diary.lock_day(diary_database(), day, user["id"], user["full_name"]):
        return jsonify({"error": "already_locked", "message": "Nhật ký ngày này đã được khóa."}), 409
    return jsonify({"ngay": day, "is_locked": True}), 200


@api.post("/nhat-ky/ngay/<day>/unlock")
@roles_required("admin", "manager")
def unlock_nhat_ky_day(day):
    if not valid_day(day):
        return jsonify({"error": "invalid_date", "message": "Ngày nhật ký không hợp lệ."}), 400
    data = request.get_json(silent=True)
    data = data if isinstance(data, dict) else {}
    reason = data.get("ly_do")
    if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 500:
        return jsonify({"error": "invalid_reason", "message": "Lý do mở khóa là bắt buộc và tối đa 500 ký tự."}), 400
    user = request.current_user
    if not diary.unlock_day(diary_database(), day, user["id"], user["full_name"], reason.strip()):
        return jsonify({"error": "not_locked", "message": "Nhật ký ngày này hiện chưa khóa."}), 409
    return jsonify({"ngay": day, "is_locked": False}), 200


@api.get("/nhat-ky/audit")
@roles_required("admin", "manager")
def get_nhat_ky_audit():
    day = request.args.get("ngay")
    if day and not valid_day(day):
        return jsonify({"error": "invalid_date", "message": "Ngày nhật ký không hợp lệ."}), 400
    return jsonify(diary.list_audit(diary_database(), day))
