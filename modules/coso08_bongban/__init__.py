"""
modules/coso08_bongban/__init__.py
───────────────────────────────────
Khai báo hợp đồng module cơ sở 08 (Bóng Bàn) theo chuẩn mục 5 của Quy ước v1.0.
"""

from flask import Blueprint
from . import service

CO_SO_ID = 8
TEN_MON = "Bóng bàn"
KIEU_DAT_LICH = "SAN"

# Khởi tạo Blueprint cho cơ sở 8, url_prefix bắt buộc là /coso/8
bp = Blueprint(
    "coso08",
    __name__,
    url_prefix="/coso/8",
    template_folder="templates",
    static_folder="static"
)


# ── 3 HÀM HỢP ĐỒNG GIAO TIẾP VỚI LÕI (Bắt buộc theo mục 5) ───────────────────

def lay_danh_sach_tai_nguyen():
    """Trả về list[dict]: [{"taiNguyenId": 1, "ten": "Bàn 1", "loai": "Ban", "sucChua": 4, "giaMoiGio": 40000}]"""
    return service.lay_danh_sach_tai_nguyen()


def kiem_tra_khung_gio(tai_nguyen_id, bat_dau, ket_thuc, so_nguoi):
    """Trả về (True, "") nếu đặt được, (False, "lý do") nếu không."""
    return service.kiem_tra_khung_gio(tai_nguyen_id, bat_dau, ket_thuc, so_nguoi)


def tinh_gia(tai_nguyen_id, bat_dau, ket_thuc, so_nguoi):
    """Trả về int (VND)."""
    return service.tinh_gia(tai_nguyen_id, bat_dau, ket_thuc, so_nguoi)
