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

from flask import Flask, render_template, g, request, redirect, url_for, flash, jsonify
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
            title="Quản Lý Chuỗi Dịch Vụ Thể Dục Thể Thao — Trang Chủ",
            total_kh=total_kh,
            total_hlv=total_hlv,
        )

    # ── Trang khuyến mãi toàn chuỗi ─────────────────────────────────────────
    @app.route("/khuyen-mai")
    def khuyen_mai():
        from core.db import get_db
        danh_sach_km = []
        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("""
                SELECT K.KhuyenMaiId, K.MaCode, K.TieuDe, K.MoTa, K.GiamPhanTram, K.GiamToiDa,
                       K.Badge, K.CoSoId, C.TenCoSo,
                       CONVERT(varchar(10), K.NgayKetThuc, 120) AS NgayKetThuc,
                       K.TrangThai
                FROM KhuyenMai K
                LEFT JOIN CoSo C ON K.CoSoId = C.CoSoId
                WHERE K.TrangThai = 'HoatDong'
                ORDER BY K.KhuyenMaiId DESC
            """)
            rows = cur.fetchall()
            db.close()
            danh_sach_km = [{
                "id": r[0], "code": r[1], "tieuDe": r[2], "moTa": r[3],
                "giamPhanTram": r[4], "giamToiDa": r[5], "badge": r[6] or "Ưu Đãi",
                "coSoId": r[7], "tenCoSo": r[8] or "Toàn Chuỗi",
                "hsd": r[9] or "Không giới hạn", "trangThai": r[10]
            } for r in rows]
        except Exception as e:
            print("Loi lay danh sach khuyen mai:", e)

        return render_template(
            "khuyen_mai.html",
            title="Khuyến Mãi & Ưu Đãi Thể Thao — SportChain Network",
            danhSachKhuyenMai=danh_sach_km
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

    # ── Bảng điều khiển Quản trị hệ thống & Quản lý cơ sở ───────────────────
    from core.auth import yeu_cau_vai_tro, hash_password
    @app.route("/admin")
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_dashboard():
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        danh_sach_coso = []
        danh_sach_tk = []
        danh_sach_datlich = []
        danh_sach_khuyenmai = []
        current_coso_info = None
        thong_ke = {
            "tong_coso": 0,
            "tong_tk": 0,
            "tong_quanly": 0,
            "tong_hoivien": 0,
            "tong_datlich": 0,
            "tong_doanhthu": 0,
            "tong_khuyenmai": 0
        }
        try:
            db = get_db()
            cur = db.cursor()

            if is_admin:
                # ── ADMIN / QUẢN TRỊ VIÊN: Toàn quyền xem 10 cơ sở, toàn bộ tài khoản, toàn bộ đơn đặt
                cur.execute("SELECT CoSoId, TenCoSo, MonTheThao, DiaChi, GioMoCua, GioDongCua, KieuDatLich FROM CoSo ORDER BY CoSoId")
                danh_sach_coso = cur.fetchall()

                cur.execute("""
                    SELECT T.TaiKhoanId, T.TenDangNhap, T.HoTen, T.Email, T.VaiTro, T.CoSoId, C.TenCoSo
                    FROM TaiKhoan T
                    LEFT JOIN CoSo C ON T.CoSoId = C.CoSoId
                    ORDER BY CASE T.VaiTro WHEN 'Admin' THEN 1 WHEN 'QuanLy' THEN 2 ELSE 3 END, T.TaiKhoanId
                """)
                danh_sach_tk = cur.fetchall()

                cur.execute("""
                    SELECT D.DatLichId,
                           CONVERT(varchar(10), D.BatDau, 120) AS NgayDat,
                           CONVERT(varchar(5), D.BatDau, 108) AS GioBatDau,
                           CONVERT(varchar(5), D.KetThuc, 108) AS GioKetThuc,
                           D.TongTien, D.TrangThai,
                           T.HoTen, T.TenDangNhap, C.TenCoSo, C.MonTheThao, D.NgayTao
                    FROM DatLich D
                    LEFT JOIN TaiKhoan T ON D.TaiKhoanId = T.TaiKhoanId
                    LEFT JOIN CoSo C ON D.CoSoId = C.CoSoId
                    ORDER BY D.DatLichId DESC
                """)
                danh_sach_datlich = cur.fetchall()

                # Danh sách khuyến mãi toàn hệ thống
                cur.execute("""
                    SELECT K.KhuyenMaiId, K.MaCode, K.TieuDe, K.MoTa, K.GiamPhanTram, K.GiamToiDa,
                           K.Badge, K.CoSoId, C.TenCoSo,
                           CONVERT(varchar(10), K.NgayKetThuc, 120) AS NgayKetThuc,
                           K.TrangThai, K.NgayTao
                    FROM KhuyenMai K
                    LEFT JOIN CoSo C ON K.CoSoId = C.CoSoId
                    ORDER BY K.KhuyenMaiId DESC
                """)
                danh_sach_khuyenmai = cur.fetchall()

                cur.execute("SELECT COUNT(*) FROM CoSo")
                thong_ke["tong_coso"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM TaiKhoan")
                thong_ke["tong_tk"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM TaiKhoan WHERE VaiTro='QuanLy'")
                thong_ke["tong_quanly"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM TaiKhoan WHERE VaiTro='HoiVien'")
                thong_ke["tong_hoivien"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*), ISNULL(SUM(TongTien), 0) FROM DatLich")
                dl_row = cur.fetchone()
                if dl_row:
                    thong_ke["tong_datlich"] = dl_row[0]
                    thong_ke["tong_doanhthu"] = dl_row[1]

                thong_ke["tong_khuyenmai"] = len([k for k in danh_sach_khuyenmai if k[10] == 'HoatDong'])

            else:
                # ── QUẢN LÝ CƠ SỞ: CHỈ xem cơ sở của mình, CHỈ xem hội viên thuộc cơ sở của mình
                cur.execute("SELECT CoSoId, TenCoSo, MonTheThao, DiaChi, GioMoCua, GioDongCua, KieuDatLich FROM CoSo WHERE CoSoId = ?", (quan_ly_cs_id,))
                danh_sach_coso = cur.fetchall()
                if danh_sach_coso:
                    current_coso_info = danh_sach_coso[0]

                # CHỈ LẤY HỘI VIÊN ĐĂNG KÝ HOẶC ĐẶT CHỖ TẠI CƠ SỞ NÀY (Tuyệt đối không xem Admin hay Quản lý khác)
                cur.execute("""
                    SELECT DISTINCT T.TaiKhoanId, T.TenDangNhap, T.HoTen, T.Email, T.VaiTro, T.CoSoId, C.TenCoSo
                    FROM TaiKhoan T
                    LEFT JOIN CoSo C ON C.CoSoId = ?
                    WHERE T.VaiTro = 'HoiVien' AND (
                        T.CoSoId = ?
                        OR EXISTS (SELECT 1 FROM TheHoiVien TH WHERE TH.TaiKhoanId = T.TaiKhoanId AND TH.CoSoId = ?)
                        OR EXISTS (SELECT 1 FROM DatLich DL WHERE DL.TaiKhoanId = T.TaiKhoanId AND DL.CoSoId = ?)
                    )
                    ORDER BY T.TaiKhoanId DESC
                """, (quan_ly_cs_id, quan_ly_cs_id, quan_ly_cs_id, quan_ly_cs_id))
                danh_sach_tk = cur.fetchall()

                # CHỈ LẤY LỊCH ĐẶT CỦA CƠ SỞ NÀY
                cur.execute("""
                    SELECT D.DatLichId,
                           CONVERT(varchar(10), D.BatDau, 120) AS NgayDat,
                           CONVERT(varchar(5), D.BatDau, 108) AS GioBatDau,
                           CONVERT(varchar(5), D.KetThuc, 108) AS GioKetThuc,
                           D.TongTien, D.TrangThai,
                           T.HoTen, T.TenDangNhap, C.TenCoSo, C.MonTheThao, D.NgayTao
                    FROM DatLich D
                    LEFT JOIN TaiKhoan T ON D.TaiKhoanId = T.TaiKhoanId
                    LEFT JOIN CoSo C ON D.CoSoId = C.CoSoId
                    WHERE D.CoSoId = ?
                    ORDER BY D.DatLichId DESC
                """, (quan_ly_cs_id,))
                danh_sach_datlich = cur.fetchall()

                # Khuyến mãi áp dụng toàn chuỗi hoặc riêng cho cơ sở này
                cur.execute("""
                    SELECT K.KhuyenMaiId, K.MaCode, K.TieuDe, K.MoTa, K.GiamPhanTram, K.GiamToiDa,
                           K.Badge, K.CoSoId, C.TenCoSo,
                           CONVERT(varchar(10), K.NgayKetThuc, 120) AS NgayKetThuc,
                           K.TrangThai, K.NgayTao
                    FROM KhuyenMai K
                    LEFT JOIN CoSo C ON K.CoSoId = C.CoSoId
                    WHERE K.CoSoId IS NULL OR K.CoSoId = ?
                    ORDER BY K.KhuyenMaiId DESC
                """, (quan_ly_cs_id,))
                danh_sach_khuyenmai = cur.fetchall()

                thong_ke["tong_coso"] = 1
                thong_ke["tong_tk"] = len(danh_sach_tk)
                thong_ke["tong_quanly"] = 1
                thong_ke["tong_hoivien"] = len(danh_sach_tk)

                cur.execute("SELECT COUNT(*), ISNULL(SUM(TongTien), 0) FROM DatLich WHERE CoSoId = ?", (quan_ly_cs_id,))
                dl_row = cur.fetchone()
                if dl_row:
                    thong_ke["tong_datlich"] = dl_row[0]
                    thong_ke["tong_doanhthu"] = dl_row[1]

                thong_ke["tong_khuyenmai"] = len([k for k in danh_sach_khuyenmai if k[10] == 'HoatDong'])

            db.close()
        except Exception as e:
            print("Loi lay thong tin admin/quanly:", e)

        title = "Bảng Điều Khiển Quản Trị Hệ Thống — SportChain" if is_admin else f"Bảng Điều Khiển Quản Lý Cơ Sở {quan_ly_cs_id} — SportChain"
        active_tab = request.args.get("tab", "tongquan")
        return render_template(
            "admin_dashboard.html",
            title=title,
            coso_list=danh_sach_coso,
            tk_list=danh_sach_tk,
            datlich_list=danh_sach_datlich,
            khuyenmai_list=danh_sach_khuyenmai,
            stats=thong_ke,
            is_admin=is_admin,
            quan_ly_cs_id=quan_ly_cs_id,
            current_coso_info=current_coso_info,
            active_tab=active_tab
        )

    # ── 1. Thêm tài khoản mới ──────────────────────────────────────────────
    @app.route("/admin/taikhoan/them", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_them_taikhoan():
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        tdn = request.form.get("ten_dang_nhap", "").strip()
        mk = request.form.get("mat_khau", "").strip()
        ho_ten = request.form.get("ho_ten", "").strip()
        email = request.form.get("email", "").strip()

        if is_admin:
            vai_tro = request.form.get("vai_tro", "HoiVien").strip()
            cs_id = request.form.get("co_so_id")
            co_so_id = int(cs_id) if cs_id and cs_id.isdigit() and vai_tro in ("QuanLy", "HLV", "HoiVien") else None
        else:
            # Quản lý cơ sở: CHỈ được thêm Hội viên trực thuộc cơ sở của mình!
            vai_tro = "HoiVien"
            co_so_id = quan_ly_cs_id

        if not tdn or not mk or not ho_ten:
            flash("❌ Vui lòng điền đầy đủ Tên đăng nhập, Mật khẩu và Họ tên!", "danger")
            return redirect(url_for("admin_dashboard", tab="taikhoan") + "#taikhoan")

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT 1 FROM TaiKhoan WHERE TenDangNhap = ?", (tdn,))
            if cur.fetchone():
                db.close()
                flash(f"❌ Tên đăng nhập '{tdn}' đã tồn tại trong hệ thống!", "danger")
                return redirect(url_for("admin_dashboard", tab="taikhoan") + "#taikhoan")

            mk_hash = hash_password(mk)
            cur.execute("""
                INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (tdn, mk_hash, ho_ten, email, vai_tro, co_so_id))
            db.commit()
            db.close()
            flash(f"✅ Đã thêm tài khoản '{tdn}' ({ho_ten}) thành công!", "success")
        except Exception as e:
            flash(f"❌ Lỗi khi thêm tài khoản: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="taikhoan") + "#taikhoan")

    # ── 2. Sửa tài khoản ───────────────────────────────────────────────────
    @app.route("/admin/taikhoan/sua/<int:tk_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_sua_taikhoan(tk_id):
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        ho_ten = request.form.get("ho_ten", "").strip()
        email = request.form.get("email", "").strip()
        mk_moi = request.form.get("mat_khau_moi", "").strip()

        try:
            db = get_db()
            cur = db.cursor()

            # Quản lý cơ sở: Kiểm tra xem tài khoản này có phải là Hội viên thuộc cơ sở của mình không
            if not is_admin:
                cur.execute("""
                    SELECT TaiKhoanId FROM TaiKhoan
                    WHERE TaiKhoanId = ? AND VaiTro = 'HoiVien' AND (
                        CoSoId = ?
                        OR EXISTS (SELECT 1 FROM TheHoiVien WHERE TaiKhoanId = ? AND CoSoId = ?)
                        OR EXISTS (SELECT 1 FROM DatLich WHERE TaiKhoanId = ? AND CoSoId = ?)
                    )
                """, (tk_id, quan_ly_cs_id, tk_id, quan_ly_cs_id, tk_id, quan_ly_cs_id))
                if not cur.fetchone():
                    db.close()
                    flash("⛔ Bạn chỉ có quyền chỉnh sửa tài khoản Hội viên thuộc cơ sở của bạn!", "danger")
                    return redirect(url_for("admin_dashboard", tab="taikhoan") + "#taikhoan")
                vai_tro = "HoiVien"
                co_so_id = quan_ly_cs_id
            else:
                vai_tro = request.form.get("vai_tro", "HoiVien").strip()
                cs_id = request.form.get("co_so_id")
                co_so_id = int(cs_id) if cs_id and cs_id.isdigit() and vai_tro in ("QuanLy", "HLV", "HoiVien") else None

            if mk_moi:
                mk_hash = hash_password(mk_moi)
                cur.execute("""
                    UPDATE TaiKhoan
                    SET HoTen = ?, Email = ?, VaiTro = ?, CoSoId = ?, MatKhauHash = ?
                    WHERE TaiKhoanId = ?
                """, (ho_ten, email, vai_tro, co_so_id, mk_hash, tk_id))
            else:
                cur.execute("""
                    UPDATE TaiKhoan
                    SET HoTen = ?, Email = ?, VaiTro = ?, CoSoId = ?
                    WHERE TaiKhoanId = ?
                """, (ho_ten, email, vai_tro, co_so_id, tk_id))
            db.commit()
            db.close()
            flash(f"✅ Đã cập nhật thành công tài khoản #{tk_id} ({ho_ten})!", "success")
        except Exception as e:
            flash(f"❌ Lỗi khi sửa tài khoản: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="taikhoan") + "#taikhoan")

    # ── 3. Xóa tài khoản ───────────────────────────────────────────────────
    @app.route("/admin/taikhoan/xoa/<int:tk_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_xoa_taikhoan(tk_id):
        from core.db import get_db
        u = get_current_user()
        if u and u.get("TaiKhoanId") == tk_id:
            flash("❌ Không thể xóa tài khoản của chính bạn đang đăng nhập!", "danger")
            return redirect(url_for("admin_dashboard", tab="taikhoan") + "#taikhoan")

        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        try:
            db = get_db()
            cur = db.cursor()

            # Quản lý cơ sở: Kiểm tra xem tài khoản này có phải là Hội viên thuộc cơ sở của mình không
            if not is_admin:
                cur.execute("""
                    SELECT TaiKhoanId FROM TaiKhoan
                    WHERE TaiKhoanId = ? AND VaiTro = 'HoiVien' AND (
                        CoSoId = ?
                        OR EXISTS (SELECT 1 FROM TheHoiVien WHERE TaiKhoanId = ? AND CoSoId = ?)
                        OR EXISTS (SELECT 1 FROM DatLich WHERE TaiKhoanId = ? AND CoSoId = ?)
                    )
                """, (tk_id, quan_ly_cs_id, tk_id, quan_ly_cs_id, tk_id, quan_ly_cs_id))
                if not cur.fetchone():
                    db.close()
                    flash("⛔ Bạn chỉ có quyền xóa tài khoản Hội viên thuộc cơ sở của bạn!", "danger")
                    return redirect(url_for("admin_dashboard", tab="taikhoan") + "#taikhoan")

            cur.execute("SELECT TenDangNhap FROM TaiKhoan WHERE TaiKhoanId = ?", (tk_id,))
            row = cur.fetchone()
            tdn = row[0] if row else str(tk_id)

            cur.execute("DELETE FROM HoaDon WHERE TaiKhoanId = ?", (tk_id,))
            cur.execute("DELETE FROM DatLich WHERE TaiKhoanId = ?", (tk_id,))
            cur.execute("DELETE FROM TheHoiVien WHERE TaiKhoanId = ?", (tk_id,))
            cur.execute("DELETE FROM DanhGia WHERE TaiKhoanId = ?", (tk_id,))
            cur.execute("DELETE FROM TaiKhoan WHERE TaiKhoanId = ?", (tk_id,))
            db.commit()
            db.close()
            flash(f"✅ Đã xóa tài khoản '{tdn}' khỏi hệ thống!", "success")
        except Exception as e:
            flash(f"❌ Không thể xóa tài khoản: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="taikhoan") + "#taikhoan")

    # ── 4. Thêm cơ sở mới ──────────────────────────────────────────────────
    @app.route("/admin/coso/them", methods=["POST"])
    @yeu_cau_vai_tro("Admin")
    def admin_them_coso():
        from core.db import get_db
        try:
            cs_id = int(request.form.get("co_so_id"))
            ten_cs = request.form.get("ten_co_so", "").strip()
            mon_tt = request.form.get("mon_the_thao", "").strip()
            dia_chi = request.form.get("dia_chi", "").strip()
            gio_mo = request.form.get("gio_mo_cua", "06:00").strip()
            gio_dong = request.form.get("gio_dong_cua", "22:00").strip()
            kieu_dl = request.form.get("kieu_dat_lich", "SAN").strip()

            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT 1 FROM CoSo WHERE CoSoId = ?", (cs_id,))
            if cur.fetchone():
                db.close()
                flash(f"❌ Mã cơ sở #{cs_id} đã tồn tại trong chuỗi!", "danger")
                return redirect(url_for("admin_dashboard", tab="coso") + "#coso")

            cur.execute("""
                INSERT INTO CoSo (CoSoId, TenCoSo, MonTheThao, DiaChi, GioMoCua, GioDongCua, KieuDatLich)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cs_id, ten_cs, mon_tt, dia_chi, gio_mo, gio_dong, kieu_dl))
            db.commit()
            db.close()
            flash(f"✅ Đã thêm cơ sở #{cs_id}: {ten_cs}!", "success")
        except Exception as e:
            flash(f"❌ Lỗi khi thêm cơ sở: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="coso") + "#coso")

    # ── 5. Sửa cơ sở ───────────────────────────────────────────────────────
    @app.route("/admin/coso/sua/<int:coso_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_sua_coso(coso_id):
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        if not is_admin and coso_id != quan_ly_cs_id:
            flash("⛔ Bạn chỉ có quyền chỉnh sửa thông tin cơ sở do mình phụ trách!", "danger")
            return redirect(url_for("admin_dashboard", tab="coso") + "#coso")

        try:
            ten_cs = request.form.get("ten_co_so", "").strip()
            mon_tt = request.form.get("mon_the_thao", "").strip()
            dia_chi = request.form.get("dia_chi", "").strip()
            gio_mo = request.form.get("gio_mo_cua", "").strip()
            gio_dong = request.form.get("gio_dong_cua", "").strip()
            kieu_dl = request.form.get("kieu_dat_lich", "SAN").strip()

            db = get_db()
            cur = db.cursor()
            cur.execute("""
                UPDATE CoSo
                SET TenCoSo = ?, MonTheThao = ?, DiaChi = ?, GioMoCua = ?, GioDongCua = ?, KieuDatLich = ?
                WHERE CoSoId = ?
            """, (ten_cs, mon_tt, dia_chi, gio_mo, gio_dong, kieu_dl, coso_id))
            db.commit()
            db.close()
            flash(f"✅ Đã cập nhật thành công cơ sở #{coso_id}: {ten_cs}!", "success")
        except Exception as e:
            flash(f"❌ Lỗi khi sửa cơ sở: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="coso") + "#coso")

    # ── 6. Xóa cơ sở ───────────────────────────────────────────────────────
    @app.route("/admin/coso/xoa/<int:coso_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin")
    def admin_xoa_coso(coso_id):
        from core.db import get_db
        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("UPDATE TaiKhoan SET CoSoId = NULL WHERE CoSoId = ?", (coso_id,))
            cur.execute("DELETE FROM DatLich WHERE CoSoId = ?", (coso_id,))
            cur.execute("DELETE FROM HoaDon WHERE CoSoId = ?", (coso_id,))
            cur.execute("DELETE FROM TaiNguyen WHERE CoSoId = ?", (coso_id,))
            cur.execute("DELETE FROM GoiHoiVien WHERE CoSoId = ?", (coso_id,))
            cur.execute("DELETE FROM TheHoiVien WHERE CoSoId = ?", (coso_id,))
            cur.execute("DELETE FROM DanhGia WHERE CoSoId = ?", (coso_id,))
            cur.execute("DELETE FROM CoSo WHERE CoSoId = ?", (coso_id,))
            db.commit()
            db.close()
            flash(f"✅ Đã xóa cơ sở #{coso_id} khỏi hệ thống!", "success")
        except Exception as e:
            flash(f"❌ Không thể xóa cơ sở #{coso_id}: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="coso") + "#coso")

    # ── 7. Đổi trạng thái lịch đặt ─────────────────────────────────────────
    @app.route("/admin/datlich/doi-trang-thai/<int:datlich_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_doi_trang_thai_datlich(datlich_id):
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        trang_thai = request.form.get("trang_thai", "DaXacNhan")
        try:
            db = get_db()
            cur = db.cursor()
            if not is_admin:
                cur.execute("SELECT 1 FROM DatLich WHERE DatLichId = ? AND CoSoId = ?", (datlich_id, quan_ly_cs_id))
                if not cur.fetchone():
                    db.close()
                    flash("⛔ Bạn không có quyền duyệt đơn đặt của cơ sở khác!", "danger")
                    return redirect(url_for("admin_dashboard", tab="datlich") + "#datlich")

            cur.execute("UPDATE DatLich SET TrangThai = ? WHERE DatLichId = ?", (trang_thai, datlich_id))
            db.commit()
            db.close()
            flash(f"✅ Đã chuyển trạng thái đơn đặt #{datlich_id} sang '{trang_thai}'!", "success")
        except Exception as e:
            flash(f"❌ Lỗi: {e}", "danger")
        return redirect(url_for("admin_dashboard", tab="datlich") + "#datlich")

    # ── 8. Xóa lịch đặt ────────────────────────────────────────────────────
    @app.route("/admin/datlich/xoa/<int:datlich_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_xoa_datlich(datlich_id):
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        try:
            db = get_db()
            cur = db.cursor()
            if not is_admin:
                cur.execute("SELECT 1 FROM DatLich WHERE DatLichId = ? AND CoSoId = ?", (datlich_id, quan_ly_cs_id))
                if not cur.fetchone():
                    db.close()
                    flash("⛔ Bạn không có quyền xóa đơn đặt của cơ sở khác!", "danger")
                    return redirect(url_for("admin_dashboard", tab="datlich") + "#datlich")

            cur.execute("DELETE FROM HoaDon WHERE DatLichId = ?", (datlich_id,))
            cur.execute("DELETE FROM DatLich WHERE DatLichId = ?", (datlich_id,))
            db.commit()
            db.close()
            flash(f"✅ Đã xóa đơn đặt #{datlich_id}!", "success")
        except Exception as e:
            flash(f"❌ Lỗi: {e}", "danger")
        return redirect(url_for("admin_dashboard", tab="datlich") + "#datlich")

    # ── 9. Thêm khuyến mãi mới ─────────────────────────────────────────────
    @app.route("/admin/khuyenmai/them", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_them_khuyenmai():
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        ma_code = request.form.get("ma_code", "").strip().upper()
        tieu_de = request.form.get("tieu_de", "").strip()
        mo_ta = request.form.get("mo_ta", "").strip()
        giam_pt = int(request.form.get("giam_phan_tram", 0) or 0)
        giam_max = int(request.form.get("giam_toi_da", 0) or 0)
        badge = request.form.get("badge", "Ưu Đãi").strip()
        ngay_kt_str = request.form.get("ngay_ket_thuc", "").strip()
        ngay_kt = f"{ngay_kt_str} 23:59:59" if ngay_kt_str else None

        if is_admin:
            cs_id_val = request.form.get("co_so_id")
            co_so_id = int(cs_id_val) if cs_id_val and cs_id_val.isdigit() else None
        else:
            co_so_id = quan_ly_cs_id

        if not ma_code or not tieu_de:
            flash("❌ Vui lòng điền đầy đủ Mã khuyến mãi và Tiêu đề chương trình!", "danger")
            return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT 1 FROM KhuyenMai WHERE MaCode = ?", (ma_code,))
            if cur.fetchone():
                db.close()
                flash(f"❌ Mã khuyến mãi '{ma_code}' đã tồn tại trong hệ thống!", "danger")
                return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

            cur.execute("""
                INSERT INTO KhuyenMai (MaCode, TieuDe, MoTa, GiamPhanTram, GiamToiDa, Badge, CoSoId, NgayKetThuc, TrangThai)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'HoatDong')
            """, (ma_code, tieu_de, mo_ta, giam_pt, giam_max, badge, co_so_id, ngay_kt))
            db.commit()
            db.close()
            flash(f"🎉 Đã thêm thành công chương trình khuyến mãi '{ma_code}'!", "success")
        except Exception as e:
            flash(f"❌ Lỗi khi thêm khuyến mãi: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

    # ── 10. Sửa khuyến mãi ─────────────────────────────────────────────────
    @app.route("/admin/khuyenmai/sua/<int:km_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_sua_khuyenmai(km_id):
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        ma_code = request.form.get("ma_code", "").strip().upper()
        tieu_de = request.form.get("tieu_de", "").strip()
        mo_ta = request.form.get("mo_ta", "").strip()
        giam_pt = int(request.form.get("giam_phan_tram", 0) or 0)
        giam_max = int(request.form.get("giam_toi_da", 0) or 0)
        badge = request.form.get("badge", "Ưu Đãi").strip()
        ngay_kt_str = request.form.get("ngay_ket_thuc", "").strip()
        ngay_kt = f"{ngay_kt_str} 23:59:59" if (ngay_kt_str and len(ngay_kt_str) == 10) else (ngay_kt_str or None)
        trang_thai = request.form.get("trang_thai", "HoatDong").strip()

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT CoSoId FROM KhuyenMai WHERE KhuyenMaiId = ?", (km_id,))
            km_row = cur.fetchone()
            if not km_row:
                db.close()
                flash("❌ Không tìm thấy chương trình khuyến mãi này!", "danger")
                return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

            if not is_admin and km_row[0] != quan_ly_cs_id:
                db.close()
                flash("⛔ Bạn chỉ có quyền chỉnh sửa khuyến mãi của cơ sở mình!", "danger")
                return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

            if is_admin:
                cs_id_val = request.form.get("co_so_id")
                co_so_id = int(cs_id_val) if cs_id_val and cs_id_val.isdigit() else None
            else:
                co_so_id = quan_ly_cs_id

            cur.execute("SELECT 1 FROM KhuyenMai WHERE MaCode = ? AND KhuyenMaiId <> ?", (ma_code, km_id))
            if cur.fetchone():
                db.close()
                flash(f"❌ Mã khuyến mãi '{ma_code}' đã được dùng cho chương trình khác!", "danger")
                return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

            cur.execute("""
                UPDATE KhuyenMai
                SET MaCode = ?, TieuDe = ?, MoTa = ?, GiamPhanTram = ?, GiamToiDa = ?,
                    Badge = ?, CoSoId = ?, NgayKetThuc = ?, TrangThai = ?
                WHERE KhuyenMaiId = ?
            """, (ma_code, tieu_de, mo_ta, giam_pt, giam_max, badge, co_so_id, ngay_kt, trang_thai, km_id))
            db.commit()
            db.close()
            flash(f"✅ Đã cập nhật thành công khuyến mãi '{ma_code}'!", "success")
        except Exception as e:
            flash(f"❌ Lỗi khi sửa khuyến mãi: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

    # ── 11. Xóa khuyến mãi ─────────────────────────────────────────────────
    @app.route("/admin/khuyenmai/xoa/<int:km_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_xoa_khuyenmai(km_id):
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT CoSoId, MaCode FROM KhuyenMai WHERE KhuyenMaiId = ?", (km_id,))
            km_row = cur.fetchone()
            if not km_row:
                db.close()
                flash("❌ Không tìm thấy khuyến mãi này!", "danger")
                return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

            if not is_admin and km_row[0] != quan_ly_cs_id:
                db.close()
                flash("⛔ Bạn không có quyền xóa khuyến mãi của cơ sở khác!", "danger")
                return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

            ma_code = km_row[1]
            cur.execute("DELETE FROM KhuyenMai WHERE KhuyenMaiId = ?", (km_id,))
            db.commit()
            db.close()
            flash(f"🗑️ Đã xóa chương trình khuyến mãi '{ma_code}'!", "success")
        except Exception as e:
            flash(f"❌ Lỗi khi xóa khuyến mãi: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

    # ── 12. Bật / Tắt trạng thái khuyến mãi nhanh ───────────────────────────
    @app.route("/admin/khuyenmai/trangthai/<int:km_id>", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy")
    def admin_doi_trang_thai_khuyenmai(km_id):
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if not is_admin else None

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT CoSoId, TrangThai, MaCode FROM KhuyenMai WHERE KhuyenMaiId = ?", (km_id,))
            row = cur.fetchone()
            if not row:
                db.close()
                flash("❌ Không tìm thấy khuyến mãi!", "danger")
                return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

            if not is_admin and row[0] != quan_ly_cs_id:
                db.close()
                flash("⛔ Bạn không có quyền thay đổi trạng thái khuyến mãi này!", "danger")
                return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

            moi = "TamDung" if row[1] == "HoatDong" else "HoatDong"
            cur.execute("UPDATE KhuyenMai SET TrangThai = ? WHERE KhuyenMaiId = ?", (moi, km_id))
            db.commit()
            db.close()
            tt_label = "kích hoạt hoạt động" if moi == "HoatDong" else "tạm dừng"
            flash(f"⚡ Đã {tt_label} mã khuyến mãi '{row[2]}'!", "info")
        except Exception as e:
            flash(f"❌ Lỗi: {e}", "danger")

        return redirect(url_for("admin_dashboard", tab="khuyenmai") + "#khuyenmai")

    # ── 13. Xem & In Hóa Đơn toàn chuỗi: /hoa-don/<int:dat_lich_id> ─────────
    @app.route("/hoa-don/<int:dat_lich_id>")
    def xem_hoa_don_tong(dat_lich_id):
        from core.db import get_db
        from modules.coso08_bongban.service import doc_so_thanh_chu
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if (u and not is_admin) else None

        don = None
        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("""
                SELECT D.DatLichId, D.TaiKhoanId, D.CoSoId, D.TaiNguyenId, D.BatDau, D.KetThuc,
                       D.TongTien, D.TrangThai, D.MaQR, D.NgayTao,
                       T.TenTaiNguyen, T.GiaMoiGio, C.TenCoSo, C.DiaChi, C.MonTheThao,
                       U.HoTen, U.TenDangNhap, U.Email
                FROM DatLich D
                LEFT JOIN TaiNguyen T ON D.TaiNguyenId = T.TaiNguyenId
                LEFT JOIN CoSo C ON D.CoSoId = C.CoSoId
                LEFT JOIN TaiKhoan U ON D.TaiKhoanId = U.TaiKhoanId
                WHERE D.DatLichId = ?
            """, (dat_lich_id,))
            r = cur.fetchone()
            db.close()
            if r:
                don = {
                    "datLichId": r[0],
                    "taiKhoanId": r[1],
                    "coSoId": r[2],
                    "taiNguyenId": r[3],
                    "batDau": r[4],
                    "ketThuc": r[5],
                    "tongTien": r[6],
                    "trangThai": r[7],
                    "maQR": r[8],
                    "ngayTao": r[9],
                    "tenBan": r[10] or f"Sân/Bàn #{r[3]}",
                    "giaMoiGio": r[11] or 60000,
                    "tenCoSo": r[12] or "Cơ Sở Thể Thao SportChain",
                    "diaChi": r[13] or "Hệ thống chuỗi cơ sở thể thao SportChain",
                    "monTheThao": r[14] or "Thể thao",
                    "hoTen": r[15] or "Khách hàng",
                    "tenDangNhap": r[16] or "",
                    "email": r[17] or ""
                }
        except Exception as e:
            print("Loi lay hoa don tong:", e)

        if not don:
            flash("❌ Không tìm thấy thông tin đơn đặt lịch này!", "danger")
            return redirect(url_for("admin_dashboard") if (is_admin or quan_ly_cs_id) else url_for("trang_chu"))

        # Kiểm tra bảo mật
        if u and not is_admin:
            if quan_ly_cs_id and don["coSoId"] != quan_ly_cs_id:
                flash("⛔ Bạn không có quyền xem hóa đơn của cơ sở khác!", "danger")
                return redirect(url_for("admin_dashboard"))
            elif not quan_ly_cs_id and u.get("TaiKhoanId") != don["taiKhoanId"]:
                flash("⛔ Bạn không có quyền xem hóa đơn này!", "danger")
                return redirect(url_for("trang_chu"))

        tong_tien_chu = doc_so_thanh_chu(don["tongTien"])
        from modules.coso08_bongban.service import tao_ma_qr_base64
        qr_hoadon_url = tao_ma_qr_base64(f"SPORTCHAIN-HD-{don['datLichId']}-{don['maQR']}")

        return render_template(
            "hoa_don.html",
            title=f"Hóa Đơn Thanh Toán #{don['datLichId']} — SportChain",
            don=don,
            tong_tien_chu=tong_tien_chu,
            qr_hoadon_url=qr_hoadon_url
        )

    # ── 14. Trạm Nhận Diện & Check-in Mã QR Đơn Đặt Sân: /checkin ─────────────
    @app.route("/checkin")
    @app.route("/admin/checkin")
    @yeu_cau_vai_tro("Admin", "QuanLy", "HLV")
    def tram_checkin():
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if (u and not is_admin) else None
        return render_template(
            "checkin.html",
            title="Trạm Nhận Diện & Check-in Mã QR Đơn Đặt Sân — SportChain",
            is_admin=is_admin,
            quan_ly_cs_id=quan_ly_cs_id
        )

    # ── 15. API Tra cứu & Nhận Diện Mã QR / Mã Đơn Đặt ──────────────────────
    @app.route("/api/checkin/tra-cuu", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy", "HLV")
    def api_checkin_tra_cuu():
        import re
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if (u and not is_admin) else None

        req_data = request.get_json(silent=True) or {}
        code_str = (req_data.get("code") or request.form.get("code") or "").strip()

        if not code_str:
            return jsonify({"ok": False, "msg": "Vui lòng nhập hoặc quét mã QR đơn đặt!"}), 400

        # Hàm bóc tách thông minh mã đơn
        parsed_id = None
        m = re.search(r"/hoa-don/(\d+)", code_str)
        if m:
            parsed_id = int(m.group(1))
        if not parsed_id:
            m = re.search(r"SPORTCHAIN-HD-(\d+)", code_str, re.I)
            if m:
                parsed_id = int(m.group(1))
        if not parsed_id:
            m = re.search(r"SPORTCHAIN-DL-(\d+)", code_str, re.I)
            if m:
                parsed_id = int(m.group(1))
        if not parsed_id:
            clean_num = code_str.lstrip("#")
            if clean_num.isdigit():
                parsed_id = int(clean_num)

        try:
            db = get_db()
            cur = db.cursor()

            query = """
                SELECT D.DatLichId, D.TaiKhoanId, D.CoSoId, D.TaiNguyenId, D.BatDau, D.KetThuc,
                       D.TongTien, D.TrangThai, D.MaQR, D.NgayTao,
                       T.TenTaiNguyen, T.GiaMoiGio, C.TenCoSo, C.DiaChi, C.MonTheThao,
                       U.HoTen, U.TenDangNhap, U.Email
                FROM DatLich D
                LEFT JOIN TaiNguyen T ON D.TaiNguyenId = T.TaiNguyenId
                LEFT JOIN CoSo C ON D.CoSoId = C.CoSoId
                LEFT JOIN TaiKhoan U ON D.TaiKhoanId = U.TaiKhoanId
                WHERE """

            if parsed_id:
                query += "D.DatLichId = ?"
                cur.execute(query, (parsed_id,))
            else:
                query += "(D.MaQR = ? OR D.MaQR LIKE ?)"
                cur.execute(query, (code_str, f"%{code_str}%"))

            r = cur.fetchone()
            db.close()

            if not r:
                return jsonify({"ok": False, "msg": f"❌ Không tìm thấy đơn đặt nào khớp với mã: '{code_str}'"}), 404

            don_cs_id = r[2]
            if not is_admin and quan_ly_cs_id and don_cs_id != quan_ly_cs_id:
                return jsonify({
                    "ok": False,
                    "msg": f"⛔ Đơn #{r[0]} thuộc {r[12]} (CS {don_cs_id:02d}), không thuộc phạm vi cơ sở do bạn phụ trách!"
                }), 403

            bat_dau_str = r[4].strftime("%H:%M %d/%m/%Y") if hasattr(r[4], "strftime") else str(r[4])
            ket_thuc_str = r[5].strftime("%H:%M %d/%m/%Y") if hasattr(r[5], "strftime") else str(r[5])
            gio_choi = f"{r[4].strftime('%H:%M') if hasattr(r[4], 'strftime') else ''} - {r[5].strftime('%H:%M') if hasattr(r[5], 'strftime') else ''}"

            trang_thai = r[7]
            tt_map = {
                "ChoThanhToan": "⏳ Chờ thanh toán tại quầy",
                "DaThanhToan": "💳 Đã thanh toán trực tuyến",
                "ChoXacNhan": "⏳ Chờ duyệt giữ chỗ",
                "DaXacNhan": "✅ Đã duyệt giữ chỗ hợp lệ",
                "HoanThanh": "🏁 Đã hoàn thành ca chơi",
                "Huy": "❌ Đã hủy"
            }

            don_data = {
                "datLichId": r[0],
                "maQR": r[8] or f"DL-{r[0]}",
                "coSoId": r[2],
                "tenCoSo": r[12] or "Cơ sở thể thao",
                "monTheThao": r[14] or "Thể thao",
                "tenBan": r[10] or f"Sân #{r[3]}",
                "batDau": bat_dau_str,
                "ketThuc": ket_thuc_str,
                "gioChoi": gio_choi,
                "tongTien": r[6],
                "tongTienFmt": f"{r[6]:,.0f}đ",
                "trangThai": trang_thai,
                "trangThaiText": tt_map.get(trang_thai, trang_thai),
                "hoTen": r[15] or "Khách hàng",
                "tenDangNhap": r[16] or "",
                "email": r[17] or "",
                "hoaDonUrl": f"/hoa-don/{r[0]}"
            }

            return jsonify({
                "ok": True,
                "msg": f"✅ Đã nhận diện thành công đơn đặt #{r[0]}!",
                "don": don_data
            })
        except Exception as e:
            return jsonify({"ok": False, "msg": f"❌ Lỗi máy chủ khi tra cứu: {e}"}), 500

    # ── 16. API Xác Nhận Check-in & Cập Nhật Trạng Thái ─────────────────────
    @app.route("/api/checkin/xac-nhan", methods=["POST"])
    @yeu_cau_vai_tro("Admin", "QuanLy", "HLV")
    def api_checkin_xac_nhan():
        from core.db import get_db
        u = get_current_user()
        is_admin = bool(u and (u.get("VaiTro") == "Admin" or u.get("role") == "Admin"))
        quan_ly_cs_id = (u.get("CoSoId") or u.get("coSoId")) if (u and not is_admin) else None

        req_data = request.get_json(silent=True) or {}
        dat_lich_id = req_data.get("datLichId")
        trang_thai_moi = req_data.get("trangThai", "DaXacNhan")

        if not dat_lich_id:
            return jsonify({"ok": False, "msg": "Thiếu mã đơn đặt!"}), 400

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT CoSoId, TrangThai FROM DatLich WHERE DatLichId = ?", (dat_lich_id,))
            row = cur.fetchone()
            if not row:
                db.close()
                return jsonify({"ok": False, "msg": "Không tìm thấy đơn đặt!"}), 404

            if not is_admin and quan_ly_cs_id and row[0] != quan_ly_cs_id:
                db.close()
                return jsonify({"ok": False, "msg": "Bạn không có quyền check-in đơn của cơ sở khác!"}), 403

            cur.execute("UPDATE DatLich SET TrangThai = ? WHERE DatLichId = ?", (trang_thai_moi, dat_lich_id))
            db.commit()
            db.close()

            tt_msg = "✅ Đã check-in cho khách vào sân thành công!" if trang_thai_moi == "DaXacNhan" else (
                "💳 Đã xác nhận thu tiền và check-in thành công!" if trang_thai_moi == "DaThanhToan" else
                f"⚡ Đã cập nhật trạng thái đơn #{dat_lich_id} sang '{trang_thai_moi}'!"
            )
            return jsonify({"ok": True, "msg": tt_msg, "trangThaiMoi": trang_thai_moi})
        except Exception as e:
            return jsonify({"ok": False, "msg": f"Lỗi cập nhật: {e}"}), 500

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
    print("  🏟️  Quản Lý Chuỗi Dịch Vụ Thể Dục Thể Thao  —  http://localhost:5000")
    print("  🏓  Cơ sở Bóng Bàn      —  http://localhost:5000/coso/8")
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
