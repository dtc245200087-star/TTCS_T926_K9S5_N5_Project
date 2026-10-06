from flask import Flask
from .config import Config
from .extensions import db, cors
from .routes import register_routes
from .models import CongTrinh, LichLamViec
from sqlalchemy import inspect, text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app)

    register_routes(app)

    with app.app_context():
        db.create_all()

        # Tự động nâng cấp schema cho các cột mới (nếu chưa tồn tại)
        columns = {column["name"] for column in inspect(db.engine).get_columns("cong_viec")}
        with db.engine.begin() as connection:
            for name, definition in (
                ("thoi_luong_ngay", "INTEGER NOT NULL DEFAULT 1"),
                ("ngay_bat_dau_thuc_te", "DATE"),
                ("ngay_hoan_thanh_thuc_te", "DATE"),
            ):
                if name not in columns:
                    connection.execute(text(f"ALTER TABLE cong_viec ADD COLUMN {name} {definition}"))

        # Khởi tạo lịch làm việc mặc định cho các công trình cũ chưa có lịch
        for project in CongTrinh.query.all():
            if project.lich_lam_viec is None:
                db.session.add(LichLamViec(cong_trinh_id=project.id, ngay_lam_viec=[0, 1, 2, 3, 4, 5]))
        db.session.commit()

    return app