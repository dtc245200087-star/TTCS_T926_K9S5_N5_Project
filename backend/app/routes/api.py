from datetime import date, datetime
import sqlite3

from flask import Blueprint, current_app, jsonify, request

from ..models import cong_viec as tasks
from ..models import milestone as milestone_data
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

nhat_ky = [
    {"id": 1, "ngay": "2026-10-01", "cong_trinh": "Khu đô thị Bắc Sông Cầu", "noi_dung": "Thi công móng khu A, thời tiết thuận lợi.", "nguoi_lap": "Nguyễn Văn An"},
    {"id": 2, "ngay": "2026-09-30", "cong_trinh": "Tòa nhà văn phòng A1", "noi_dung": "Hoàn thành lắp đặt cốt thép tầng 3.", "nguoi_lap": "Trần Minh Đức"},
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
    update_category = "category_id" in data
    category_id = data.get("category_id")

    if update_category:
        if category_id is not None and (
            not _integer_id(category_id)
            or not milestone_data.get_category(current_app.config["USER_DATABASE"], category_id)
        ):
            return jsonify({"error": "invalid_category", "message": "Hạng mục không hợp lệ."}), 400

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
        current_app.config["USER_DATABASE"],
        task_id,
        start_date,
        end_date,
        completion,
        category_id=category_id,
        update_category=update_category,
    ):
        return jsonify({"error": "not_found", "message": "Không tìm thấy công việc."}), 404
    updated = next(
        task for task in tasks.list_tasks(current_app.config["USER_DATABASE"])
        if task["id"] == task_id
    )
    return jsonify(updated)


def _database_path():
    return current_app.config["USER_DATABASE"]


def _integer_id(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


@api.get("/categories")
@login_required
def get_categories():
    return jsonify(milestone_data.list_categories(_database_path()))


@api.get("/categories/unassigned-tasks")
@login_required
def get_unassigned_tasks():
    return jsonify(milestone_data.list_unassigned_tasks(_database_path()))


@api.post("/categories")
@roles_required("admin", "manager")
def add_category():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_payload", "message": "Dữ liệu gửi lên không hợp lệ."}), 400
    name = data.get("name")
    parent_id = data.get("parent_id")
    planned_start_date = data.get("planned_start_date")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
        return jsonify({"error": "invalid_name", "message": "Tên hạng mục là bắt buộc và tối đa 120 ký tự."}), 400
    if parent_id is not None and not _integer_id(parent_id):
        return jsonify({"error": "invalid_parent", "message": "Hạng mục cha không hợp lệ."}), 400
    if parent_id is not None and not milestone_data.get_category(_database_path(), parent_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục cha."}), 404
    try:
        category = milestone_data.create_category(
            _database_path(), name.strip(), parent_id, planned_start_date
        )
    except ValueError as error:
        return jsonify({"error": "invalid_date", "message": str(error)}), 400
    return jsonify(category), 201


@api.patch("/categories/<int:category_id>")
@roles_required("admin", "manager")
def edit_category(category_id):
    if not milestone_data.get_category(_database_path(), category_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục."}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_payload", "message": "Dữ liệu gửi lên không hợp lệ."}), 400
    name = data.get("name")
    parent_id = data.get("parent_id")
    planned_start_date = data.get("planned_start_date")
    if name is not None and (
        not isinstance(name, str) or not name.strip() or len(name.strip()) > 120
    ):
        return jsonify({"error": "invalid_name", "message": "Tên hạng mục là bắt buộc và tối đa 120 ký tự."}), 400
    if parent_id is not None:
        if not _integer_id(parent_id) or parent_id == category_id:
            return jsonify({"error": "invalid_parent", "message": "Hạng mục cha không hợp lệ."}), 400
        if not milestone_data.get_category(_database_path(), parent_id):
            return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục cha."}), 404
    try:
        category = milestone_data.update_category(
            _database_path(),
            category_id,
            name=name.strip() if name is not None else None,
            parent_id=parent_id,
            planned_start_date=planned_start_date,
        )
    except ValueError as error:
        return jsonify({"error": "invalid_category", "message": str(error)}), 400
    return jsonify(category)


@api.delete("/categories/<int:category_id>")
@roles_required("admin", "manager")
def remove_category(category_id):
    try:
        if not milestone_data.delete_category(_database_path(), category_id):
            return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục."}), 404
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "category_not_empty",
            "message": "Hãy xóa hạng mục con trước khi xóa hạng mục này.",
        }), 409
    return jsonify({"message": "Đã xóa hạng mục."})


@api.post("/categories/<int:category_id>/tasks")
@roles_required("admin", "manager")
def add_category_task(category_id):
    if not milestone_data.get_category(_database_path(), category_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục."}), 404
    data = request.get_json(silent=True)
    task_id = data.get("task_id") if isinstance(data, dict) else None
    if not _integer_id(task_id):
        return jsonify({"error": "invalid_task", "message": "Công việc không hợp lệ."}), 400
    try:
        milestone_data.assign_task(_database_path(), category_id, task_id)
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "task_assignment_conflict",
            "message": "Công việc không tồn tại hoặc đã được gán vào một hạng mục.",
        }), 409
    return jsonify({"message": "Đã gán công việc vào hạng mục."}), 201


@api.delete("/categories/tasks/<int:task_id>")
@roles_required("admin", "manager")
def remove_category_task(task_id):
    if not milestone_data.unassign_task(_database_path(), task_id):
        return jsonify({"error": "not_found", "message": "Công việc chưa được gán vào hạng mục."}), 404
    return jsonify({"message": "Đã gỡ công việc khỏi hạng mục."})


@api.get("/categories/<int:category_id>/dependencies")
@login_required
def get_category_dependencies(category_id):
    if not milestone_data.get_category(_database_path(), category_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục."}), 404
    return jsonify(milestone_data.list_dependencies(_database_path(), category_id))


@api.post("/categories/<int:category_id>/dependencies")
@roles_required("admin", "manager")
def add_category_dependency(category_id):
    if not milestone_data.get_category(_database_path(), category_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục."}), 404
    data = request.get_json(silent=True)
    task_id = data.get("task_id") if isinstance(data, dict) else None
    depends_on_task_id = data.get("depends_on_task_id") if isinstance(data, dict) else None
    if not _integer_id(task_id) or not _integer_id(depends_on_task_id):
        return jsonify({"error": "invalid_dependency", "message": "Hai công việc phụ thuộc không hợp lệ."}), 400
    try:
        milestone_data.add_dependency(_database_path(), task_id, depends_on_task_id)
    except ValueError as error:
        return jsonify({"error": "invalid_dependency", "message": str(error)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "dependency_exists", "message": "Quan hệ phụ thuộc này đã tồn tại."}), 409
    return jsonify({"message": "Đã thêm quan hệ phụ thuộc."}), 201


@api.delete("/categories/<int:category_id>/dependencies/<int:task_id>/<int:depends_on_task_id>")
@roles_required("admin", "manager")
def remove_category_dependency(category_id, task_id, depends_on_task_id):
    if not milestone_data.get_category(_database_path(), category_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục."}), 404
    if not milestone_data.remove_dependency(_database_path(), task_id, depends_on_task_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy quan hệ phụ thuộc."}), 404
    return jsonify({"message": "Đã xóa quan hệ phụ thuộc."})


@api.get("/milestones")
@login_required
def get_milestones():
    return jsonify(milestone_data.list_milestones(_database_path()))


@api.post("/milestones")
@roles_required("admin", "manager")
def add_milestone():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_payload", "message": "Dữ liệu gửi lên không hợp lệ."}), 400
    category_id, deadline = data.get("category_id"), data.get("deadline")
    if not _integer_id(category_id) or not isinstance(deadline, str):
        return jsonify({"error": "invalid_milestone", "message": "Hạng mục hoặc ngày bàn giao không hợp lệ."}), 400
    if not milestone_data.get_category(_database_path(), category_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy hạng mục."}), 404
    try:
        result = milestone_data.create_milestone(
            _database_path(), category_id, deadline, request.current_user["id"]
        )
    except ValueError as error:
        return jsonify({"error": "invalid_date", "message": str(error)}), 400
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "milestone_exists",
            "message": "Hạng mục này đã có mốc bàn giao. Hãy cập nhật mốc hiện có.",
        }), 409
    return jsonify(result), 201


@api.get("/milestones/calculate")
@login_required
def calculate_category_milestone():
    category_id = request.args.get("category_id", type=int)
    if not category_id:
        return jsonify({"error": "invalid_category", "message": "category_id là bắt buộc."}), 400
    item = milestone_data.get_milestone_for_category(_database_path(), category_id)
    if not item:
        return jsonify({"error": "not_found", "message": "Hạng mục chưa có mốc bàn giao."}), 404
    return jsonify({
        "id": item["id"],
        **milestone_data.calculate_milestone(_database_path(), category_id, item["deadline"]),
    })


@api.get("/milestones/alerts")
@login_required
def get_milestone_alerts():
    return jsonify(milestone_data.list_alerts(_database_path()))


@api.get("/milestones/alerts/<int:milestone_id>")
@login_required
def get_milestone_alert(milestone_id):
    result = milestone_data.get_alert(_database_path(), milestone_id)
    if not result:
        return jsonify({"error": "not_found", "message": "Không tìm thấy mốc bàn giao."}), 404
    return jsonify(result)


@api.get("/milestones/<int:milestone_id>")
@login_required
def get_milestone_detail(milestone_id):
    item = milestone_data.get_milestone(_database_path(), milestone_id)
    if not item:
        return jsonify({"error": "not_found", "message": "Không tìm thấy mốc bàn giao."}), 404
    return jsonify({
        **item,
        **milestone_data.calculate_milestone(
            _database_path(), item["category_id"], item["deadline"]
        ),
    })


@api.patch("/milestones/<int:milestone_id>")
@roles_required("admin", "manager")
def edit_milestone(milestone_id):
    if not milestone_data.get_milestone(_database_path(), milestone_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy mốc bàn giao."}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_payload", "message": "Dữ liệu gửi lên không hợp lệ."}), 400
    category_id, deadline = data.get("category_id"), data.get("deadline")
    if category_id is not None and (
        not _integer_id(category_id)
        or not milestone_data.get_category(_database_path(), category_id)
    ):
        return jsonify({"error": "invalid_category", "message": "Hạng mục không hợp lệ."}), 400
    if deadline is not None and not isinstance(deadline, str):
        return jsonify({"error": "invalid_date", "message": "Ngày bàn giao không hợp lệ."}), 400
    try:
        result = milestone_data.update_milestone(
            _database_path(), milestone_id, category_id=category_id, deadline=deadline
        )
    except ValueError as error:
        return jsonify({"error": "invalid_date", "message": str(error)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "milestone_exists", "message": "Hạng mục đã có mốc bàn giao khác."}), 409
    return jsonify(result)


@api.delete("/milestones/<int:milestone_id>")
@roles_required("admin", "manager")
def remove_milestone(milestone_id):
    if not milestone_data.delete_milestone(_database_path(), milestone_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy mốc bàn giao."}), 404
    return jsonify({"message": "Đã xóa mốc bàn giao."})


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
    return jsonify(nhat_ky)

@api.post("/nhat-ky")
@roles_required("admin", "manager", "engineer")
def add_nhat_ky():
    data = request.get_json() or {}
    item = {
        "id": max([x["id"] for x in nhat_ky], default=0) + 1,
        "ngay": datetime.now().strftime("%Y-%m-%d"),
        "cong_trinh": data.get("cong_trinh", ""),
        "noi_dung": data.get("noi_dung", ""),
        "nguoi_lap": data.get("nguoi_lap", "Quản trị viên")
    }
    nhat_ky.append(item)
    return jsonify(item), 201
