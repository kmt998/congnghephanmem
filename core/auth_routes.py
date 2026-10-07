"""
core/auth_routes.py
───────────────────
Routes đăng nhập / đăng ký / đăng xuất dùng chung cho toàn bộ hệ thống.
KHÔNG SỬA FILE NÀY NẾU KHÔNG PHẢI TRƯỞNG NHÓM.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, g
from core.auth import dang_nhap, dang_ky, get_current_user

auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.before_request
def load_user():
    g.current_user = get_current_user()


@auth_bp.route("/dang-nhap", methods=["GET", "POST"])
def login():
    if g.current_user:
        return redirect(url_for("trang_chu"))

    if request.method == "POST":
        tdn = request.form.get("ten_dang_nhap", "").strip()
        mk  = request.form.get("mat_khau", "")
        kq  = dang_nhap(tdn, mk)

        if kq["ok"]:
            session["jwt_token"] = kq["token"]
            session.permanent = True
            flash("✅ Đăng nhập thành công!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("trang_chu"))
        flash(f"❌ {kq['error']}", "danger")

    return render_template("auth/login.html", title="Đăng Nhập — Trung Tâm Thể Thao")


@auth_bp.route("/dang-ky", methods=["GET", "POST"])
def register():
    if g.current_user:
        return redirect(url_for("trang_chu"))

    if request.method == "POST":
        ho_ten  = request.form.get("ho_ten", "").strip()
        email   = request.form.get("email", "").strip()
        tdn     = request.form.get("ten_dang_nhap", "").strip()
        mk      = request.form.get("mat_khau", "")
        xac_nhan = request.form.get("xac_nhan", "")

        if mk != xac_nhan:
            flash("❌ Mật khẩu xác nhận không khớp!", "danger")
        elif len(mk) < 6:
            flash("❌ Mật khẩu phải có ít nhất 6 ký tự!", "danger")
        else:
            kq = dang_ky(ho_ten, email, tdn, mk)
            if kq["ok"]:
                flash("✅ Đăng ký thành công! Vui lòng đăng nhập.", "success")
                return redirect(url_for("auth.login"))
            flash(f"❌ {kq['error']}", "danger")

    return render_template("auth/register.html", title="Đăng Ký Hội Viên — Trung Tâm Thể Thao")


@auth_bp.route("/dang-xuat")
def logout():
    session.clear()
    flash("👋 Đã đăng xuất thành công!", "info")
    return redirect(url_for("trang_chu"))


# API JSON dùng cho AJAX
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True)
    kq = dang_nhap(data.get("username", ""), data.get("password", ""))
    if kq["ok"]:
        return jsonify(token=kq["token"], user=kq["user"])
    return jsonify(error=kq["error"]), 401
