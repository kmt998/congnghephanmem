"""
webtong/app.py
──────────────
Entry point toàn bộ ứng dụng Flask — TrungTamTheThao.
Chỉ trưởng nhóm được chỉnh sửa file này.
"""

import os
import sys

# Thêm thư mục gốc vào PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, g
from core.auth import get_current_user
from core.registry import register_all_blueprints, FACILITY_REGISTRY


def create_app() -> Flask:
    app = Flask(
        __name__,
        # Layout & static dùng chung từ core/
        template_folder=os.path.join(os.path.dirname(__file__), "../core/templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "../core/static"),
    )

    # ── Cấu hình ────────────────────────────────────────────────────────────
    app.secret_key = os.environ.get("SECRET_KEY", "sportchain-2026-changeme")
    app.config["PERMANENT_SESSION_LIFETIME"] = 86400   # 24 giờ

    # ── Đăng ký tất cả Blueprint ────────────────────────────────────────────
    register_all_blueprints(app)

    # ── Inject biến toàn cục vào Jinja ──────────────────────────────────────
    @app.context_processor
    def inject_globals():
        return {
            "facilities": FACILITY_REGISTRY,
            "current_user": get_current_user(),
        }

    # ── Trang chủ web tổng ──────────────────────────────────────────────────
    @app.route("/")
    def trang_chu():
        total_kh = 2450
        total_hlv = 85
        try:
            from core.db import get_db
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT COUNT(*) FROM TaiKhoan WHERE VaiTro='HoiVien'")
            row = cur.fetchone()
            if row:
                total_kh = row[0]
            db.close()
        except Exception:
            pass

        return render_template(
            "trang_chu.html",
            title="Trung Tâm Thể Thao — Trang Chủ Web Tổng",
            total_kh=total_kh,
            total_hlv=total_hlv,
        )

    # ── Trang khuyến mãi toàn chuỗi ─────────────────────────────────────────
    @app.route("/khuyen-mai")
    def khuyen_mai():
        return render_template(
            "khuyen_mai.html",
            title="Khuyến Mãi & Ưu Đãi Thể Thao — SportChain Network"
        )

    # ── Trang câu hỏi thường gặp FAQ ────────────────────────────────────────
    @app.route("/faq")
    def faq():
        return render_template(
            "faq.html",
            title="Câu Hỏi Thường Gặp (FAQ) — Hướng Dẫn & Giải Đáp | SportChain"
        )

    # ── Đặt lịch toàn chuỗi (Bước 1: Chọn cơ sở thể thao) ───────────────────
    @app.route("/dat-lich")
    def dat_lich_tong():
        return render_template(
            "dat_lich_tong.html",
            title="Đặt Lịch Thể Thao Trực Tuyến — Chọn Cơ Sở Thể Thao | SportChain"
        )

    # ── Trang đăng nhập / đăng ký (dùng chung) ──────────────────────────────
    from core.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 55)
    print("  🏟️  Trung Tâm Thể Thao  —  http://localhost:5000")
    print("  🏓  Cơ sở Bóng Bàn      —  http://localhost:5000/coso/8")
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
