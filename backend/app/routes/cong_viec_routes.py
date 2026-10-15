from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.cong_viec import CongViec, Team, TaskHistory
from datetime import datetime

cong_viec_bp = Blueprint('cong_viec', __name__)

# 1. API Phân công công việc (Xử lý Cảnh báo quá tải + Ghi log lịch sử)
@cong_viec_bp.route('/api/tasks/assign', methods=['POST'])
def assign_task():
    data = request.get_json() or {}
    task_id = data.get('task_id')
    team_id = data.get('team_id')
    user_id = data.get('user_id', 1)  # ID Chỉ huy trưởng
    confirm_overload = data.get('confirm_overload', False)

    if not task_id or not team_id:
        return jsonify({'error': 'Thiếu task_id hoặc team_id'}), 400

    task = CongViec.query.get(task_id)
    if not task:
        return jsonify({'error': 'Không tìm thấy công việc'}), 404

    target_team = Team.query.get(team_id)
    if not target_team:
        return jsonify({'error': 'Không tìm thấy đội thi công'}), 404

    # Đếm số công việc trùng thời gian của đội được giao
    # Công thức: tu_ngay_A < den_ngay_B AND den_ngay_A > tu_ngay_B
    overlapping_count = CongViec.query.filter(
        CongViec.doi_id == team_id,
        CongViec.id != task_id,
        CongViec.tu_ngay < task.den_ngay,
        CongViec.den_ngay > task.tu_ngay
    ).count()

    # Cảnh báo khi có HƠN 3 công việc bị trùng thời gian (> 3)
    if overlapping_count > 3 and not confirm_overload:
        return jsonify({
            'warning': True,
            'message': f'Đội "{target_team.name}" đang có {overlapping_count} công việc bị trùng thời gian. Bạn có muốn tiếp tục phân công?',
            'overlapping_count': overlapping_count
        }), 200

    # Tiến hành phân công và ghi vết lịch sử
    old_team_id = task.doi_id

    if old_team_id != team_id:
        task.doi_id = team_id

        # Lưu vết vào Audit Log
        history = TaskHistory(
            task_id=task.id,
            old_team_id=old_team_id,
            new_team_id=team_id,
            changed_by_user_id=user_id,
            changed_at=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Đã phân công thành công cho {target_team.name}'
    }), 200


# 2. API Xem công việc theo Đội (Dành cho Đội trưởng)
@cong_viec_bp.route('/api/tasks/team/<int:team_id>', methods=['GET'])
def get_team_tasks(team_id):
    tasks = CongViec.query.filter_by(doi_id=team_id).all()
    result = [{
        'id': t.id,
        'ten_cong_viec': t.ten_cong_viec,
        'tu_ngay': t.tu_ngay.strftime('%Y-%m-%d %H:%M'),
        'den_ngay': t.den_ngay.strftime('%Y-%m-%d %H:%M')
    } for t in tasks]
    return jsonify({'team_id': team_id, 'total': len(result), 'tasks': result}), 200


# 3. API Xem lịch sử đổi đội thi công (Audit Log)
@cong_viec_bp.route('/api/tasks/<int:task_id>/history', methods=['GET'])
def get_task_history(task_id):
    logs = TaskHistory.query.filter_by(task_id=task_id).order_by(TaskHistory.changed_at.desc()).all()
    result = [{
        'id': log.id,
        'old_team_id': log.old_team_id,
        'new_team_id': log.new_team_id,
        'changed_by_user_id': log.changed_by_user_id,
        'changed_at': log.changed_at.strftime('%Y-%m-%d %H:%M:%S')
    } for log in logs]
    return jsonify({'task_id': task_id, 'history': result}), 200