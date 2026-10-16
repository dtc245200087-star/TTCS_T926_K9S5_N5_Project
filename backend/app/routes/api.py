from flask import Blueprint, jsonify, request
from datetime import datetime
from .auth import login_required, roles_required

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
    return jsonify(nhat_ky)

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
    all_day_rain = data.get("mua_ca_ngay", False)
    if not isinstance(all_day_rain, bool):
        return jsonify({"error": "invalid_all_day_rain", "message": "Đánh dấu mưa cả ngày không hợp lệ."}), 400
    if all_day_rain and weather != "Mưa":
        return jsonify({"error": "invalid_all_day_rain", "message": "Chỉ có thể đánh dấu mưa cả ngày khi thời tiết là Mưa."}), 400
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
        all_day_rain=all_day_rain,
    )
    return jsonify(summary)
