from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.cong_trinh import CongTrinh
from ..models.lich_lam_viec import LichLamViec, NgayNghi

lich_lam_viec_bp = Blueprint("lich_lam_viec", __name__)


@lich_lam_viec_bp.get("")
def get_all():
    calendars = LichLamViec.query.join(CongTrinh).order_by(CongTrinh.ten_cong_trinh).all()
    return jsonify([calendar.to_dict() for calendar in calendars])


@lich_lam_viec_bp.patch("/<int:project_id>")
def update_week(project_id):
    calendar = LichLamViec.query.filter_by(cong_trinh_id=project_id).first_or_404()
    data = request.get_json(silent=True) or {}
    weekdays = data.get("ngay_lam_viec")
    if (not isinstance(weekdays, list) or not weekdays
            or any(type(day) is not int or day < 0 or day > 6 for day in weekdays)
            or len(set(weekdays)) != len(weekdays)):
        return jsonify({"message": "Chọn ít nhất một ngày làm việc hợp lệ trong tuần."}), 400
    calendar.ngay_lam_viec = sorted(weekdays)
    db.session.commit()
    return jsonify(calendar.to_dict())


@lich_lam_viec_bp.post("/<int:project_id>/ngay-nghi")
def create_holiday(project_id):
    calendar = LichLamViec.query.filter_by(cong_trinh_id=project_id).first_or_404()
    data = request.get_json(silent=True) or {}
    name = data.get("ten", "")
    try:
        holiday_date = date.fromisoformat(data.get("ngay", ""))
    except (TypeError, ValueError):
        return jsonify({"message": "Ngày nghỉ cần theo định dạng YYYY-MM-DD."}), 400
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
        return jsonify({"message": "Tên ngày nghỉ là bắt buộc và tối đa 120 ký tự."}), 400
    holiday = NgayNghi(calendar_id=calendar.id, ngay=holiday_date, ten=name.strip())
    db.session.add(holiday)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Ngày nghỉ này đã tồn tại trong lịch công trình."}), 409
    return jsonify(holiday.to_dict()), 201


@lich_lam_viec_bp.delete("/ngay-nghi/<int:holiday_id>")
def delete_holiday(holiday_id):
    holiday = NgayNghi.query.get_or_404(holiday_id)
    db.session.delete(holiday)
    db.session.commit()
    return jsonify({"message": "Đã xóa ngày nghỉ."})
