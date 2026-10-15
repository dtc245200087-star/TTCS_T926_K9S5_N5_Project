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
