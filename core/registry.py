"""
core/registry.py
────────────────
Đăng ký các Blueprint cơ sở và danh sách cơ sở thể thao hiển thị ở web tổng.
KHÔNG SỬA FILE NÀY NẾU KHÔNG PHẢI TRƯỞNG NHÓM (Theo quy ước v1.0).
"""

from flask import Flask

# ── Danh sách 10 cơ sở thể thao (Loại bỏ hoàn toàn mã CS rườm rà) ─────────────
FACILITY_REGISTRY = [
    {"id": 1,  "slug": "boi-loi",     "ten": "Bơi Lội",         "icon": "🏊", "url": "/coso/1",  "tu_gia": "50.000đ/h",    "active": False, "mo_ta": "Hồ bơi chuẩn Olympic 50m & 25m"},
    {"id": 2,  "slug": "gym",         "ten": "Gym & Thể Hình",  "icon": "🏋️", "url": "/coso/2",  "tu_gia": "50.000đ/buổi", "active": False, "mo_ta": "Phòng tập thể hình thiết bị cao cấp"},
    {"id": 3,  "slug": "cau-long",    "ten": "Cầu Lông",        "icon": "🏸", "url": "/coso/3",  "tu_gia": "60.000đ/h",    "active": False, "mo_ta": "12 sân thảm tiêu chuẩn thi đấu"},
    {"id": 4,  "slug": "bong-da",     "ten": "Bóng Đá Mini",    "icon": "⚽", "url": "/coso/4",  "tu_gia": "300.000đ/h",   "active": False, "mo_ta": "Sân cỏ nhân tạo 5v5 & 7v7 ngoài trời"},
    {"id": 5,  "slug": "tennis",      "ten": "Tennis",          "icon": "🎾", "url": "/coso/5",  "tu_gia": "80.000đ/h",    "active": False, "mo_ta": "Sân cứng & đất nện tiêu chuẩn quốc tế"},
    {"id": 6,  "slug": "yoga",        "ten": "Yoga & Thiền",    "icon": "🧘", "url": "/coso/6",  "tu_gia": "60.000đ/buổi", "active": False, "mo_ta": "Không gian yoga yên tĩnh và thư giãn"},
    {"id": 7,  "slug": "bong-ro",     "ten": "Bóng Rổ",         "icon": "🏀", "url": "/coso/7",  "tu_gia": "100.000đ/h",   "active": False, "mo_ta": "Sân bóng rổ sàn gỗ chuyên dụng"},
    {"id": 8,  "slug": "bong-ban",    "ten": "Bóng Bàn",        "icon": "🏓", "url": "/coso/8",  "tu_gia": "45.000đ/h",    "active": True,  "mo_ta": "16 bàn chuẩn thi đấu ITTF & Robot bắn bóng", "mine": True},
    {"id": 9,  "slug": "vo-thuat",    "ten": "Võ Thuật",        "icon": "🥋", "url": "/coso/9",  "tu_gia": "80.000đ/buổi", "active": False, "mo_ta": "Taekwondo, Karate, Boxing & Kickfit"},
    {"id": 10, "slug": "pickleball",  "ten": "Pickleball",      "icon": "🎯", "url": "/coso/10", "tu_gia": "70.000đ/h",    "active": False, "mo_ta": "Cụm sân pickleball xu hướng mới"},
]


def register_all_blueprints(app: Flask):
    """Tự động mount Blueprint các cơ sở đã hoàn thành."""
    try:
        from modules.coso08_bongban.routes import bp as bongban_bp
        app.register_blueprint(bongban_bp)
        print("[Registry] OK: Da nap module CoSo 08: Bong Ban (/coso/8)")
    except Exception as e:
        print(f"[Registry] WARNING: Chua the nap CoSo 08: {e}")
