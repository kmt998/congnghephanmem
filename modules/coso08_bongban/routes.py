"""
modules/coso08_bongban/routes.py
────────────────────────────────
Routes cho cơ sở 08 (Bóng Bàn Đỉnh Cao).
Tuân thủ chuẩn route mục 7: /coso/8/..., /api/coso/8/...
"""

from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, g
from . import bp, CO_SO_ID
from . import service
from core.auth import get_current_user, yeu_cau_vai_tro, chi_dung_co_so

@bp.before_request
def load_user():
    g.current_user = get_current_user()


# ── 1. Trang chủ cơ sở bóng bàn: /coso/8/ ─────────────────────────────────────
@bp.route("/")
@bp.route("/trang-chu")
@chi_dung_co_so(CO_SO_ID)
def trang_chu():
    danh_sach_ban = service.lay_danh_sach_tai_nguyen()
    danh_sach_hlv = service.lay_danh_sach_hlv()
    danh_sach_dv  = service.lay_danh_sach_dich_vu()

    hom_nay = date.today().strftime("%Y-%m-%d")

    return render_template(
        "coso08_bongban/trang_chu.html",
        title="Cơ Sở Bóng Bàn Đỉnh Cao — Đặt Bàn Thi Đấu ITTF | SportChain",
        coSoId=CO_SO_ID,
        danhSachBan=danh_sach_ban,
        danhSachHlv=danh_sach_hlv,
        danhSachDv=danh_sach_dv,
        homNay=hom_nay
    )


# ── 2. Danh sách tài nguyên: /coso/8/tai-nguyen ──────────────────────────────
@bp.route("/tai-nguyen")
@chi_dung_co_so(CO_SO_ID)
def tai_nguyen():
    danh_sach_ban = service.lay_danh_sach_tai_nguyen()
    return render_template(
        "coso08_bongban/tai_nguyen.html",
        title="Danh Sách Bàn Bóng Bàn — Chuẩn Thi Đấu ITTF | SportChain",
        danhSachBan=danh_sach_ban,
        coSoId=CO_SO_ID
    )


# ── 3. Trang & Xử lý đặt bàn: /coso/8/dat-lich ────────────────────────────────
@bp.route("/dat-lich", methods=["GET", "POST"])
@chi_dung_co_so(CO_SO_ID)
def dat_lich():
    danh_sach_ban = service.lay_danh_sach_tai_nguyen()
    danh_sach_hlv = service.lay_danh_sach_hlv()
    danh_sach_dv  = service.lay_danh_sach_dich_vu()

    ban_chon_id = request.args.get("ban_id", type=int) or (danh_sach_ban[0]["taiNguyenId"] if danh_sach_ban else 801)

    if request.method == "POST":
        if not g.current_user:
            flash("⚠️ Vui lòng đăng nhập để hoàn tất đặt bàn bóng bàn!", "warning")
            return redirect(url_for("auth.login", next=request.url))

        tai_khoan_id = g.current_user.get("TaiKhoanId") or g.current_user.get("userId")
        tai_nguyen_id = int(request.form.get("taiNguyenId", ban_chon_id))
        ngay = request.form.get("ngay")
        gio_bd = request.form.get("gioBatDau")
        gio_kt = request.form.get("gioKetThuc")
        hlv_id = request.form.get("hlvId")
        dv_ids = request.form.getlist("dichVuIds")

        str_bd = f"{ngay} {gio_bd}"
        str_kt = f"{ngay} {gio_kt}"

        kq = service.tao_dat_lich_moi(tai_khoan_id, tai_nguyen_id, str_bd, str_kt, hlv_id, dv_ids)
        if kq["ok"]:
            flash("🎉 Đặt bàn thành công!", "success")
            # Chuyển hướng tới Thank You Page
            return redirect(url_for("coso08.cam_on", qr=kq["don"]["maQR"]))
        else:
            flash(f"❌ {kq['error']}", "danger")

    ngay_mac_dinh = date.today().strftime("%Y-%m-%d")

    return render_template(
        "coso08_bongban/dat_lich.html",
        title="Đặt Bàn Bóng Bàn Trực Tuyến — Chọn Khung Giờ & HLV | SportChain",
        coSoId=CO_SO_ID,
        banChonId=ban_chon_id,
        danhSachBan=danh_sach_ban,
        danhSachHlv=danh_sach_hlv,
        danhSachDv=danh_sach_dv,
        ngayMacDinh=ngay_mac_dinh
    )


# ── 4. Thank You Page: /coso/8/cam-on (Hạng mục 4) ───────────────────────────
@bp.route("/cam-on")
def cam_on():
    qr = request.args.get("qr", "")
    don = next((d for d in service.IN_MEMORY_DAT_LICH if d["maQR"] == qr), None)
    if not don:
        if service.IN_MEMORY_DAT_LICH:
            don = service.IN_MEMORY_DAT_LICH[0]
        else:
            return redirect(url_for("coso08.trang_chu"))
    return render_template("coso08_bongban/cam_on.html", don=don)


# ── 5. Lịch sử đặt của hội viên ──────────────────────────────────────────────
@bp.route("/lich-su")
def lich_su_dat():
    if not g.current_user:
        return redirect(url_for("auth.login", next=request.url))
    tai_khoan_id = g.current_user.get("TaiKhoanId") or g.current_user.get("userId")
    lich_su = service.lay_lich_su_cua_user(tai_khoan_id)
    return render_template(
        "coso08_bongban/lich_su.html",
        title="Lịch Sử Đặt Bàn Bóng Bàn Của Tôi | SportChain",
        lichSu=lich_su,
        coSoId=CO_SO_ID
    )


# ── 6. Đánh giá: /coso/8/danh-gia ─────────────────────────────────────────────
@bp.route("/danh-gia")
def danh_gia():
    return redirect(url_for("coso08.trang_chu"))


# ── 7. API JSON theo chuẩn mục 7: /api/coso/8/... ────────────────────────────
@bp.route("/api/tai-nguyen")
def api_tai_nguyen():
    return jsonify(service.lay_danh_sach_tai_nguyen())


@bp.route("/api/kiem-tra-gia", methods=["POST"])
def api_kiem_tra_gia():
    data = request.get_json(force=True)
    tn_id = int(data.get("taiNguyenId", 801))
    bd = data.get("batDau")
    kt = data.get("ketThuc")
    so_nguoi = int(data.get("soNguoi", 2))

    ok, msg = service.kiem_tra_khung_gio(tn_id, bd, kt, so_nguoi)
    gia = service.tinh_gia(tn_id, bd, kt, so_nguoi)
    return jsonify({"hopLe": ok, "thongBao": msg, "tongTien": gia})
