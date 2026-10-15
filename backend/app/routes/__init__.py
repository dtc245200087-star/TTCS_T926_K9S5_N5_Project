from app.routes.cong_viec_routes import cong_viec_bp

# Trong file này nếu dự án đang dùng hàm init_app() hoặc khởi tạo Blueprint chung,
# bạn dán dòng sau để đăng ký cong_viec_bp:
# app.register_blueprint(cong_viec_bp)