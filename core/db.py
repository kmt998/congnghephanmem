"""
core/db.py
──────────
Kết nối SQL Server — database TrungTamTheThao.
KHÔNG SỬA FILE NÀY NẾU KHÔNG PHẢI TRƯỞNG NHÓM (Theo quy ước v1.0).
"""

import os
import pyodbc

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    pass

# ── Cấu hình kết nối SQL Server ──────────────────────────────────────────────
_SERVER   = os.environ.get("DB_SERVER",   r"localhost,1433")
_DATABASE = os.environ.get("DB_NAME",     "TrungTamTheThao")
_DRIVER   = os.environ.get("DB_DRIVER",   "ODBC Driver 17 for SQL Server")
_UID      = os.environ.get("DB_USER") or os.environ.get("DB_UID", "")
_PWD      = os.environ.get("DB_PASSWORD") or os.environ.get("DB_PWD", "")

_DB_AVAILABLE = None


def _build_conn_str() -> str:
    timeout_part = "LoginTimeout=2;Connection Timeout=2;"
    trust_part = "TrustServerCertificate=yes;"
    if _UID:
        return (
            f"DRIVER={{{_DRIVER}}};"
            f"SERVER={_SERVER};"
            f"DATABASE={_DATABASE};"
            f"UID={_UID};PWD={_PWD};{trust_part}{timeout_part}"
        )
    return (
        f"DRIVER={{{_DRIVER}}};"
        f"SERVER={_SERVER};"
        f"DATABASE={_DATABASE};"
        f"Trusted_Connection=yes;{trust_part}{timeout_part}"
    )


def is_db_available() -> bool:
    """Kiểm tra xem SQL Server có đang online không."""
    global _DB_AVAILABLE
    if _DB_AVAILABLE is True:
        return True
    try:
        conn = pyodbc.connect(_build_conn_str(), autocommit=False)
        conn.close()
        _DB_AVAILABLE = True
    except Exception:
        _DB_AVAILABLE = False
    return _DB_AVAILABLE


def get_db() -> pyodbc.Connection:
    """Mở và trả về 1 connection SQL Server mới nếu online, ngược lại ném lỗi nhanh."""
    if not is_db_available():
        raise ConnectionError("SQL Server hien chua bat hoac chua ket noi (he thong dung du lieu offline)")
    return pyodbc.connect(_build_conn_str(), autocommit=False)


def init_db():
    """Tạo database TrungTamTheThao nếu chưa tồn tại (chạy 1 lần đầu)."""
    if not is_db_available():
        return
    master_str = _build_conn_str().replace(f"DATABASE={_DATABASE};", "DATABASE=master;")
    conn = pyodbc.connect(master_str, autocommit=True)
    cur  = conn.cursor()
    cur.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{_DATABASE}')
            CREATE DATABASE [{_DATABASE}]
    """)
    conn.close()
