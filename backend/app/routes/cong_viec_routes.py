from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.cong_viec import CongViec
from app.models.nhat_ky import LichSuPhanCong, NhatKyKhoiLuong

# Khởi tạo Blueprint với tiền tố URL chung là /api
cong_viec_bp = Blueprint('cong_viec_bp', __name__, url_prefix='/api')

# =========================================================================
# FEATURE S-25: CHỈ HUY TRƯỞNG GIAO CÔNG VIỆC CHO ĐỘI THI CÔNG
# =========================================================================
@cong_viec_bp.route('/cong-viec/<int:id>/phan-cong', methods=['POST'])
def phan_cong_cong_viec(id):
    data = request.json or {}
    doi_moi_id = data.get('doi_moi_id')
    force_assign = data.get('force_assign', False)  # Xác nhận giao đè khi có cảnh báo
    
    cv = CongViec.query.get_or_404(id)
    
    # 1. Đếm số công việc trùng khoảng thời gian thi công của đội mới
    cac_viec_trung = CongViec.query.filter(
        CongViec.doi_thi_cong_id == doi_moi_id,
        CongViec.id != id,
        CongViec.tu_ngay <= cv.den_ngay,
        CongViec.den_ngay >= cv.tu_ngay
    ).all()
    
    overlap_count = len(cac_viec_trung)
    
    # 2. Cảnh báo nếu số việc trùng > 3 và người dùng chưa bấm xác nhận (force_assign = False)
    if overlap_count > 3 and not force_assign:
        return jsonify({
            "status": "WARNING_OVERLOAD",
            "overlap_count": overlap_count,
            "message": f"Hệ thống cảnh báo: Đội này đang có {overlap_count} công việc chồng lấn thời gian. Bạn có chắc chắn muốn tiếp tục phân công?"
        }), 200
        
    # 3. Tiến hành phân công & Ghi vết đổi đội vào CSDL (Audit Trail)
    doi_cu_id = cv.doi_thi_cong_id
    cv.doi_thi_cong_id = doi_moi_id
    
    ls = LichSuPhanCong(
        cong_viec_id=id,
        doi_cu_id=doi_cu_id,
        doi_moi_id=doi_moi_id,
        nguoi_thuc_hien=data.get('nguoi_thuc_hien', 'Chỉ huy trưởng')
    )
    
    db.session.add(ls)
    db.session.commit()
    
    return jsonify({
        "status": "SUCCESS",
        "message": "Phân công công việc thành công và đã lưu lịch sử đổi đội!"
    }), 200


# =========================================================================
# FEATURE S-26: ĐỘI TRƯỜNG XEM VIỆC & BÁO CÁO KHỐI LƯỢNG HÀNG NGÀY
# =========================================================================

# 1. Xem danh sách việc của Đội (Sắp xếp theo Ngày bắt đầu)
@cong_viec_bp.route('/doi-thi-cong/<int:doi_id>/cong-viec', methods=['GET'])
def lay_danh_sach_viec_doi(doi_id):
    # Lấy danh sách việc của đội, sắp xếp tăng dần theo tu_ngay
    ds_cong_viec = CongViec.query.filter_by(doi_thi_cong_id=doi_id)\
        .order_by(CongViec.tu_ngay.asc()).all()
    
    result = []
    for cv in ds_cong_viec:
        # Tính tổng khối lượng lũy kế từ nhật ký báo cáo
        reports = NhatKyKhoiLuong.query.filter_by(cong_viec_id=cv.id).all()
        luy_ke = sum(r.khoi_luong_ngay for r in reports)
        
        result.append({
            "id": cv.id,
            "ten_cong_viec": cv.ten_cong_viec,
            "tu_ngay": cv.tu_ngay.strftime('%Y-%m-%d'),
            "den_ngay": cv.den_ngay.strftime('%Y-%m-%d'),
            "is_critical": cv.is_critical,                  # Nhận biết công việc găng
            "khoi_luong_ke_hoach": cv.khoi_luong_ke_hoach,
            "khoi_luong_luy_ke": luy_ke
        })
        
    return jsonify(result), 200

# 2. Đội trưởng báo cáo khối lượng làm trong ngày
@cong_viec_bp.route('/cong-viec/<int:id>/bao-cao-ngay', methods=['POST'])
def bao_cao_khoi_luong_ngay(id):
    data = request.json or {}
    kl_ngay = float(data.get('khoi_luong_ngay', 0))
    
    cv = CongViec.query.get_or_404(id)
    
    # Lưu nhật ký (CSDL tự động ghi thời điểm tạo created_at)
    nk = NhatKyKhoiLuong(
        cong_viec_id=id,
        khoi_luong_ngay=kl_ngay,
        nguoi_bao_cao=data.get('nguoi_bao_cao', 'Đội trưởng')
    )
    db.session.add(nk)
    db.session.commit()
    
    # Tính lại tổng khối lượng lũy kế
    reports = NhatKyKhoiLuong.query.filter_by(cong_viec_id=id).all()
    luy_ke_moi = sum(r.khoi_luong_ngay for r in reports)
    
    # Cảnh báo nếu lũy kế vượt khối lượng kế hoạch
    warning = None
    if luy_ke_moi > cv.khoi_luong_ke_hoach:
        warning = f"Lưu ý: Khối lượng lũy kế ({luy_ke_moi}) đã vượt quá khối lượng kế hoạch ({cv.khoi_luong_ke_hoach})!"
        
    return jsonify({
        "status": "SUCCESS",
        "message": "Đã lưu báo cáo khối lượng thành công!",
        "thoi_diem_bao_cao": nk.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "khoi_luong_luy_ke": luy_ke_moi,
        "warning": warning
    }), 200