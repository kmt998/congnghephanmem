"""
core/auth.py
────────────
Module xác thực JWT & phân quyền dùng chung cho toàn bộ 10 cơ sở.
KHÔNG SỬA FILE NÀY NẾU KHÔNG PHẢI TRƯỞNG NHÓM (Theo quy ước v1.0).
"""

import os
import functools
import hashlib
import datetime
import jwt
from flask import request, session, redirect, url_for, jsonify, g
from core.db import get_db

SECRET_KEY    = os.environ.get("JWT_SECRET", "sportchain-jwt-secret-2026-trungtamthethao")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_H  = 24

# ── Hashing mật khẩu ─────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    """Hash SHA-256."""
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed


# ── JWT Token ────────────────────────────────────────────────────────────────
def generate_token(tai_khoan_id: int, vai_tro: str, co_so_id: int | None) -> str:
    """
    Quy ước JWT: Đúng 3 trường { "userId": 15, "role": "QuanLy", "coSoId": 3 }
    - role chỉ nhận: 'Admin' | 'QuanLy' | 'HLV' | 'HoiVien'
    - coSoId: null với Admin và HoiVien
    """
    payload = {
        "userId": tai_khoan_id,
        "role":   vai_tro,
        "coSoId": None if vai_tro in ("Admin", "HoiVien") else co_so_id,
        "exp":    datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRE_H),
        "iat":    datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


# ── Lấy người dùng hiện tại ───────────────────────────────────────────────────
def get_current_user() -> dict | None:
    if hasattr(g, "current_user") and g.current_user is not None:
        return g.current_user

    payload = None

    # 1. Thử lấy từ session (web cookie)
    if "jwt_token" in session:
        payload = decode_token(session["jwt_token"])

    # 2. Thử lấy từ Authorization header Bearer (API)
    if payload is None:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            payload = decode_token(auth_header[7:].strip())

    if payload:
        # Lấy thông tin chi tiết từ DB
        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("""
                SELECT TaiKhoanId, TenDangNhap, HoTen, Email, VaiTro, CoSoId
                FROM TaiKhoan WHERE TaiKhoanId = ?
            """, (payload["userId"],))
            row = cur.fetchone()
            db.close()
            if row:
                g.current_user = {
                    "TaiKhoanId":  row[0],
                    "TenDangNhap": row[1],
                    "HoTen":       row[2],
                    "Email":       row[3],
                    "VaiTro":      row[4],
                    "CoSoId":      row[5],
                    "userId":      payload["userId"],
                    "role":        payload["role"],
                    "coSoId":      payload["coSoId"],
                }
                return g.current_user
        except Exception:
            pass

    g.current_user = None
    return None


# ── Decorators phân quyền (Bắt buộc theo mục 4) ──────────────────────────────
def yeu_cau_vai_tro(*roles):
    """
    Decorator kiểm tra vai trò người dùng ('Admin', 'QuanLy', 'HLV', 'HoiVien').
    Cách dùng: @yeu_cau_vai_tro('Admin', 'QuanLy')
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            u = get_current_user()
            if u is None:
                if request.is_json:
                    return jsonify({"error": "Chưa đăng nhập", "code": 401}), 401
                return redirect(url_for("auth.login", next=request.url))
            if u["VaiTro"] not in roles and u["role"] not in roles:
                if request.is_json:
                    return jsonify({"error": "Không có quyền truy cập", "code": 403}), 403
                return redirect(url_for("trang_chu"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


def chi_dung_co_so(co_so_id: int):
    """
    Decorator chặn người quản lý cơ sở này truy cập vào cơ sở khác.
    - Admin toàn quyền (coSoId = None)
    - Quản lý/HLV: bắt buộc u.coSoId == co_so_id
    - Hội viên: xem và đặt lịch bình thường
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            u = get_current_user()
            if u:
                if u["VaiTro"] == "Admin" or u["role"] == "Admin":
                    return f(*args, **kwargs)
                if u["VaiTro"] in ("QuanLy", "HLV"):
                    if u.get("coSoId") != co_so_id and u.get("CoSoId") != co_so_id:
                        if request.is_json:
                            return jsonify({"error": "Không có quyền quản lý cơ sở này", "code": 403}), 403
                        return redirect(url_for("trang_chu"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ── Nghiệp vụ Đăng Nhập / Đăng Ký ───────────────────────────────────────────
def dang_nhap(ten_dang_nhap: str, mat_khau: str) -> dict:
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT TaiKhoanId, TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId
            FROM TaiKhoan WHERE TenDangNhap = ?
        """, (ten_dang_nhap,))
        row = cur.fetchone()
        db.close()

        if not row:
            return {"ok": False, "error": "Tên đăng nhập không tồn tại"}

        tai_khoan_id, tdn, mk_hash, ho_ten, email, vai_tro, co_so_id = row
        if not verify_password(mat_khau, mk_hash):
            return {"ok": False, "error": "Mật khẩu không chính xác"}

        token = generate_token(tai_khoan_id, vai_tro, co_so_id)
        return {
            "ok": True,
            "token": token,
            "user": {
                "userId": tai_khoan_id,
                "username": tdn,
                "hoTen": ho_ten,
                "role": vai_tro,
                "coSoId": co_so_id
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Lỗi cơ sở dữ liệu: {str(e)}"}


def dang_ky(ho_ten: str, email: str, ten_dang_nhap: str, mat_khau: str) -> dict:
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT 1 FROM TaiKhoan WHERE TenDangNhap = ? OR Email = ?", (ten_dang_nhap, email))
        if cur.fetchone():
            db.close()
            return {"ok": False, "error": "Tên đăng nhập hoặc email đã được sử dụng"}

        mk_hash = hash_password(mat_khau)
        cur.execute("""
            INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
            VALUES (?, ?, ?, ?, 'HoiVien', NULL)
        """, (ten_dang_nhap, mk_hash, ho_ten, email))
        db.commit()
        db.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": f"Lỗi cơ sở dữ liệu: {str(e)}"}
