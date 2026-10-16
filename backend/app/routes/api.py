from datetime import date, datetime
import sqlite3

from pathlib import Path
import uuid

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from ..models import cong_viec as tasks
from ..models import milestone as milestone_data
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


@api.get("/schedule-results")
@login_required
def get_schedule_results():
    database = current_app.config["USER_DATABASE"]
    schedule_results, has_cycle = tasks.get_schedule_results(database)
    return jsonify({
        "tasks": tasks.list_tasks(database),
        "schedule_results": [] if has_cycle else schedule_results,
        "has_cycle": has_cycle,
        "message": (
            "Dữ liệu công việc có vòng lặp phụ thuộc, không thể tính tiến độ."
            if has_cycle else ""
        ),
    })


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
    except milestone_data.DependencyCycleError as error:
        return jsonify({"error": "dependency_cycle", "message": str(error)}), 422
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
    data = request.get_json(silent=True) if request.is_json else request.form.to_dict()
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_payload", "message": "Dữ liệu gửi lên không hợp lệ."}), 400

    project = data.get("cong_trinh")
    diary_date = data.get("ngay")
    work_item_id = data.get("cong_viec_id")
    entry_time = data.get("gio")
    description = data.get("noi_dung")
    client_uid = data.get("client_uid")
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
    if client_uid is not None and (
        not isinstance(client_uid, str) or not client_uid.strip() or len(client_uid) > 64
    ):
        return jsonify({"error": "invalid_client_uid", "message": "Mã đồng bộ nhật ký không hợp lệ."}), 400

    entry = diaries.create_entry(
        current_app.config["USER_DATABASE"],
        project=project,
        diary_date=diary_date,
        task_id=work_item_id,
        entry_time=entry_time,
        description=description.strip(),
        user_id=request.current_user["id"],
        client_uid=client_uid,
    )
    return jsonify(entry), 200 if entry.get("client_uid") == client_uid and client_uid else 201


@api.post("/nhat-ky/<int:entry_id>/images")
@roles_required("admin", "manager", "engineer")
def upload_nhat_ky_image(entry_id):
    database_path = current_app.config["USER_DATABASE"]
    if not diaries.entry_exists(database_path, entry_id):
        return jsonify({"error": "not_found", "message": "Không tìm thấy mục nhật ký."}), 404
    upload_id = request.form.get("upload_id", "")
    if not upload_id or len(upload_id) > 64:
        return jsonify({"error": "invalid_upload_id", "message": "Mã lần tải ảnh không hợp lệ."}), 400
    existing_image = diaries.get_entry_image_by_upload_id(database_path, entry_id, upload_id)
    if existing_image:
        return jsonify(existing_image), 200
    if diaries.count_entry_images(database_path, entry_id) >= 10:
        return jsonify({"error": "too_many_images", "message": "Mỗi mục nhật ký được đính tối đa 10 ảnh."}), 409

    image_file = request.files.get("image")
    thumbnail_file = request.files.get("thumbnail")
    note = request.form.get("ghi_chu_anh", "")
    if image_file is None or thumbnail_file is None:
        return jsonify({"error": "missing_image", "message": "Cần tải cả ảnh và ảnh thu nhỏ."}), 400
    if len(note) > 500:
        return jsonify({"error": "invalid_image_note", "message": "Ghi chú ảnh tối đa 500 ký tự."}), 400

    image_contents = image_file.stream.read(1024 * 1024 + 1)
    thumbnail_contents = thumbnail_file.stream.read(150 * 1024 + 1)
    if (
        len(image_contents) >= 1024 * 1024
        or not image_contents.startswith(b"\xff\xd8\xff")
        or len(thumbnail_contents) > 150 * 1024
        or not thumbnail_contents.startswith(b"\xff\xd8\xff")
    ):
        return jsonify({
            "error": "invalid_image",
            "message": "Ảnh phải là JPEG hợp lệ, tối đa 1 MB; ảnh thu nhỏ tối đa 150 KB.",
        }), 400

    filename = f"{uuid.uuid4().hex}.jpg"
    thumbnail_filename = f"{uuid.uuid4().hex}-thumb.jpg"
    upload_folder = Path(database_path).parent / "diary_images"
    image_path = upload_folder / filename
    thumbnail_path = upload_folder / thumbnail_filename
    try:
        upload_folder.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(image_contents)
        thumbnail_path.write_bytes(thumbnail_contents)
        image = diaries.add_entry_image(
            database_path,
            entry_id=entry_id,
            filename=filename,
            thumbnail_filename=thumbnail_filename,
            upload_id=upload_id,
            note=note.strip(),
        )
    except sqlite3.IntegrityError:
        image_path.unlink(missing_ok=True)
        thumbnail_path.unlink(missing_ok=True)
        existing_image = diaries.get_entry_image_by_upload_id(database_path, entry_id, upload_id)
        if existing_image:
            return jsonify(existing_image), 200
        raise
    except (OSError, sqlite3.Error):
        image_path.unlink(missing_ok=True)
        thumbnail_path.unlink(missing_ok=True)
        raise
    return jsonify(image), 201


@api.get("/nhat-ky/images/<path:filename>")
@login_required
def get_nhat_ky_image(filename):
    upload_folder = Path(current_app.config["USER_DATABASE"]).parent / "diary_images"
    return send_from_directory(upload_folder, filename)


@api.get("/nhat-ky/thumbnails/<path:filename>")
@login_required
def get_nhat_ky_thumbnail(filename):
    upload_folder = Path(current_app.config["USER_DATABASE"]).parent / "diary_images"
    return send_from_directory(upload_folder, filename)


@api.get("/nhat-ky/thong-tin-ngay")
@login_required
def get_nhat_ky_thong_tin_ngay():
    project = request.args.get("cong_trinh")
    diary_date = request.args.get("ngay")
    if not isinstance(project, str) or project not in {item["ten"] for item in cong_trinh}:
        return jsonify({"error": "invalid_project", "message": "Công trình không hợp lệ."}), 400
    if not isinstance(diary_date, str):
        return jsonify({"error": "invalid_date", "message": "Ngày nhật ký là bắt buộc."}), 400
    try:
        if date.fromisoformat(diary_date).isoformat() != diary_date:
            raise ValueError
    except ValueError:
        return jsonify({"error": "invalid_date", "message": "Ngày phải theo định dạng YYYY-MM-DD."}), 400
    return jsonify(diaries.get_daily_summary(current_app.config["USER_DATABASE"], project, diary_date))


@api.put("/nhat-ky/thong-tin-ngay")
@roles_required("admin", "manager", "engineer")
def update_nhat_ky_thong_tin_ngay():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_payload", "message": "Dữ liệu gửi lên không hợp lệ."}), 400
    project = data.get("cong_trinh")
    diary_date = data.get("ngay")
    if not isinstance(project, str) or project not in {item["ten"] for item in cong_trinh}:
        return jsonify({"error": "invalid_project", "message": "Công trình không hợp lệ."}), 400
    if not isinstance(diary_date, str):
        return jsonify({"error": "invalid_date", "message": "Ngày nhật ký là bắt buộc."}), 400
    try:
        if date.fromisoformat(diary_date).isoformat() != diary_date:
            raise ValueError
    except ValueError:
        return jsonify({"error": "invalid_date", "message": "Ngày phải theo định dạng YYYY-MM-DD."}), 400

    workforce_count = data.get("nhan_luc_so_nguoi")
    if workforce_count is not None and (
        isinstance(workforce_count, bool) or not isinstance(workforce_count, int) or not 0 <= workforce_count <= 10000
    ):
        return jsonify({"error": "invalid_workforce_count", "message": "Số nhân lực phải từ 0 đến 10000."}), 400
    weather = data.get("thoi_tiet", "")
    if not isinstance(weather, str) or weather not in ("", "Nắng", "Nhiều mây", "Mưa", "Khác"):
        return jsonify({"error": "invalid_weather", "message": "Tình trạng thời tiết không hợp lệ."}), 400
    text_fields = (
        ("nhan_luc_ghi_chu", "Ghi chú nhân lực", 2000),
        ("thiet_bi", "Thiết bị", 4000),
        ("ghi_chu_thoi_tiet", "Ghi chú thời tiết", 2000),
    )
    for field, label, limit in text_fields:
        value = data.get(field, "")
        if not isinstance(value, str) or len(value.strip()) > limit:
            return jsonify({"error": "invalid_text", "message": f"{label} tối đa {limit} ký tự."}), 400

    summary = diaries.update_daily_summary(
        current_app.config["USER_DATABASE"],
        project=project,
        diary_date=diary_date,
        user_id=request.current_user["id"],
        workforce_count=workforce_count,
        workforce_notes=data.get("nhan_luc_ghi_chu", "").strip(),
        equipment=data.get("thiet_bi", "").strip(),
        weather=weather,
        weather_notes=data.get("ghi_chu_thoi_tiet", "").strip(),
    )
    return jsonify(summary)
