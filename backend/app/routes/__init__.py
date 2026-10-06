from .cong_trinh import cong_trinh_bp
from .cong_viec import cong_viec_bp
from .dashboard import dashboard_bp
from .lich_lam_viec import lich_lam_viec_bp

def register_routes(app):
    app.register_blueprint(cong_trinh_bp, url_prefix="/api/cong-trinh")
    app.register_blueprint(cong_viec_bp, url_prefix="/api/cong-viec")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(lich_lam_viec_bp, url_prefix="/api/lich-lam-viec")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "message": "Dieu Hanh Thi Cong API đang hoạt động"}
