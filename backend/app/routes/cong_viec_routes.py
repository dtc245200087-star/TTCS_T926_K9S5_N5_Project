from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import db
from app.models.cong_viec import CongViec, Team

cong_viec_bp = Blueprint('cong_viec', __name__)

# Hàm hỗ trợ ghi log an toàn (tránh lỗi ImportError nếu Class tên khác)
def save_nhat_ky(cong_viec_id, noi_dung, thoi_gian):
    try:
        import app.models.nhat_ky as nhat_ky_module
        NhatKyClass = getattr(nhat_ky_module, 'NhatKy', None) or \
                       getattr(nhat_ky_module, 'NhatKyThiCong', None) or \
                       getattr(nhat_ky_module, 'TaskHistory', None)
        
        if NhatKyClass:
            log = NhatKyClass(
                cong_viec_id=cong_viec_id,
                noi_dung=noi_dung,
                thoi_gian=thoi_gian
            )
            db.session.add(log)
    except Exception:
        pass


# =========================================================
# 1. API CHO CHỈ HUY TRƯỞNG: PHÂN CÔNG CÔNG VIỆC (TASK S-25)
# =========================================================
@cong_viec_bp.route('/api/tasks/assign', methods=['POST'])
def assign_task():
    data = request.get_json() or {}
    task_id = data.get('task_id')
    team_id = data.get('team_id')
    user_id = data.get('user_id', 1)
    confirm_overload = data.get('confirm_overload', False)

    if not task_id or not team_id:
        return jsonify({'error': 'Thiếu task_id hoặc team_id'}), 400

    task = CongViec.query.get(task_id)
    if not task:
        return jsonify({'error': 'Không tìm thấy công việc'}), 404

    overlapping_tasks = []
    if getattr(task, 'tu_ngay', None) and getattr(task, 'den_ngay', None):
        query = CongViec.query.filter(
            CongViec.doi_id == team_id,
            CongViec.id != task_id,
            CongViec.tu_ngay <= task.den_ngay,
            CongViec.den_ngay >= task.tu_ngay
        )
        overlapping_tasks = query.all()

    if len(overlapping_tasks) >= 3 and not confirm_overload:
        return jsonify({
            'warning': True,
            'overload': True,
            'message': f'Đội thi công hiện đang đảm nhận {len(overlapping_tasks)} công việc trùng thời gian. Bạn có muốn tiếp tục giao việc?',
            'current_task_count': len(overlapping_tasks)
        }), 200

    old_team_id = getattr(task, 'doi_id', None)
    task.doi_id = team_id

    log_msg = f"Chỉ huy trưởng (ID: {user_id}) giao việc '{getattr(task, 'ten_cong_viec', '')}' cho Đội ID: {team_id} (Đội cũ: {old_team_id})"
    save_nhat_ky(task.id, log_msg, datetime.now())

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Đã giao công việc thành công cho Đội ID: {team_id}",
        'task_id': task.id,
        'assigned_team_id': team_id
    }), 200


# =========================================================
# 2. API CHO ĐỘI TRƯỞNG: XEM VIỆC & BÁO CÁO KHỐI LƯỢNG (TASK S-26)
# =========================================================

# 2.1 API Đội trưởng xem danh sách công việc của đội
@cong_viec_bp.route('/api/doi-truong/tasks', methods=['GET'])
def get_doi_truong_tasks():
    doi_id = request.args.get('doi_id', type=int)
    ngay_bat_dau = request.args.get('ngay_bat_dau')

    if not doi_id:
        return jsonify({"error": "Thiếu tham số doi_id"}), 400

    query = CongViec.query.filter_by(doi_id=doi_id)
    
    if ngay_bat_dau:
        try:
            ngay_dt = datetime.strptime(ngay_bat_dau, '%Y-%m-%d')
            query = query.filter(CongViec.tu_ngay >= ngay_dt)
        except ValueError:
            pass

    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "ten_cong_viec": getattr(task, 'ten_cong_viec', ''),
            "tu_ngay": task.tu_ngay.strftime('%Y-%m-%d') if getattr(task, 'tu_ngay', None) else None,
            "den_ngay": task.den_ngay.strftime('%Y-%m-%d') if getattr(task, 'den_ngay', None) else None,
            "khoi_luong_tong": getattr(task, 'khoi_luong_tong', 100),
            "khoi_luong_luy_ke": getattr(task, 'khoi_luong_luy_ke', 0),
            "don_vi_tinh": getattr(task, 'don_vi_tinh', 'm3'),
            "la_cong_viec_gang": getattr(task, 'la_cong_viec_gang', False)
        })

    return jsonify({"success": True, "data": result}), 200


# 2.2 API Đội trưởng báo cáo khối lượng công việc trong ngày
@cong_viec_bp.route('/api/doi-truong/tasks/<int:task_id>/bao-cao', methods=['POST'])
def bao_cao_khoi_luong(task_id):
    data = request.get_json() or {}
    khoi_luong_ngay = data.get('khoi_luong_ngay', 0)
    ghi_chu = data.get('ghi_chu', '')

    task = CongViec.query.get(task_id)
    if not task:
        return jsonify({"error": "Không tìm thấy công việc"}), 404

    khoi_luong_tong = getattr(task, 'khoi_luong_tong', 100) or 100
    khoi_luong_luy_ke_cu = getattr(task, 'khoi_luong_luy_ke', 0) or 0

    khoi_luong_luy_ke_moi = khoi_luong_luy_ke_cu + khoi_luong_ngay
    thoi_diem_bao_cao = datetime.now()

    canh_bao = None
    if khoi_luong_luy_ke_moi > khoi_luong_tong:
        canh_bao = f"Cảnh báo: Khối lượng lũy kế ({khoi_luong_luy_ke_moi}) vượt quá khối lượng kế hoạch ({khoi_luong_tong})!"

    if hasattr(task, 'khoi_luong_luy_ke'):
        task.khoi_luong_luy_ke = khoi_luong_luy_ke_moi
    if hasattr(task, 'thoi_diem_bao_cao_cuoi'):
        task.thoi_diem_bao_cao_cuoi = thoi_diem_bao_cao

    log_msg = f"Báo cáo ngày: +{khoi_luong_ngay}. Lũy kế: {khoi_luong_luy_ke_moi}. {ghi_chu}"
    save_nhat_ky(task.id, log_msg, thoi_diem_bao_cao)

    db.session.commit()

    response_data = {
        "success": True,
        "message": "Đã ghi nhận báo cáo khối lượng thành công.",
        "task_id": task.id,
        "khoi_luong_ngay": khoi_luong_ngay,
        "khoi_luong_luy_ke": khoi_luong_luy_ke_moi,
        "khoi_luong_tong": khoi_luong_tong,
        "thoi_diem_bao_cao": thoi_diem_bao_cao.strftime('%Y-%m-%d %H:%M:%S')
    }

    if canh_bao:
        response_data["warning"] = canh_bao

    return jsonify(response_data), 200