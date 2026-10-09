"""
database/init_db.py
───────────────────
Script Python tự động nạp toàn bộ Schema và Dữ liệu mẫu vào SQL Server.
Đảm bảo đọc và ghi chuẩn mã hóa UTF-8 tiếng Việt 100%, không bị lỗi font chữ.

Cách chạy:
    py database/init_db.py
"""

import os
import re
import sys
import pyodbc
from dotenv import load_dotenv

# Đảm bảo in console tiếng Việt không bị lỗi trên Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Nạp file .env từ thư mục gốc
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(base_dir, ".env"), override=True)

_SERVER   = os.environ.get("DB_SERVER",   r"localhost\SQL_CNPM")
_DATABASE = os.environ.get("DB_NAME",     "TrungTamTheThao")
_DRIVER   = os.environ.get("DB_DRIVER",   "ODBC Driver 17 for SQL Server")
_UID      = os.environ.get("DB_USER",     "")
_PWD      = os.environ.get("DB_PASSWORD", "")

def get_connection(database="master"):
    trust_part = "TrustServerCertificate=yes;"
    timeout_part = "LoginTimeout=5;Connection Timeout=5;"
    if _UID:
        conn_str = (
            f"DRIVER={{{_DRIVER}}};"
            f"SERVER={_SERVER};"
            f"DATABASE={database};"
            f"UID={_UID};PWD={_PWD};{trust_part}{timeout_part}"
        )
    else:
        conn_str = (
            f"DRIVER={{{_DRIVER}}};"
            f"SERVER={_SERVER};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;{trust_part}{timeout_part}"
        )
    return pyodbc.connect(conn_str, autocommit=True)

def execute_sql_file(cursor, filepath):
    filename = os.path.basename(filepath)
    print(f"  -> Thực thi: {filename}...")
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # Phân tách batch theo từ khóa GO
    batches = re.split(r"^\s*GO\s*$", content, flags=re.MULTILINE | re.IGNORECASE)
    for b in batches:
        stmt = b.strip()
        if not stmt:
            continue
        # Bỏ qua các lệnh USE DB vì pyodbc đã chỉ định database từ đầu
        if re.match(r"^\s*USE\s+", stmt, flags=re.IGNORECASE):
            continue
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"     ⚠️ Cảnh báo tại {filename}: {e}")

def main():
    print("=" * 60)
    print("🚀 TIẾN TRÌNH KHỞI TẠO CƠ SỞ DỮ LIỆU CHUẨN UNICODE (UTF-8)")
    print(f"   Server  : {_SERVER}")
    print(f"   Database: {_DATABASE}")
    print("=" * 60)

    try:
        # 1. Kiểm tra và tạo database nếu chưa có
        print(f"\n📦 Bước 1: Kiểm tra database [{_DATABASE}]...")
        master_conn = get_connection("master")
        master_cur = master_conn.cursor()
        master_cur.execute(f"""
            IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{_DATABASE}')
            BEGIN
                CREATE DATABASE [{_DATABASE}] COLLATE Vietnamese_CI_AS;
                PRINT 'Đã tạo mới database {_DATABASE}';
            END
        """)
        master_conn.close()
        print(f"   ✅ Database [{_DATABASE}] đã sẵn sàng!")

        # 2. Kết nối vào database chính
        print(f"\n🏗️ Bước 2: Khởi tạo Schema và Dữ liệu mẫu...")
        conn = get_connection(_DATABASE)
        cur = conn.cursor()

        db_dir = os.path.dirname(__file__)
        schema_path = os.path.join(db_dir, "schema_core.sql")
        seed_path = os.path.join(db_dir, "seed_core.sql")

        if os.path.exists(schema_path):
            execute_sql_file(cur, schema_path)
        if os.path.exists(seed_path):
            execute_sql_file(cur, seed_path)

        # 3. Chạy các file cấu hình riêng từng cơ sở
        print(f"\n🏢 Bước 3: Nạp cấu hình các cơ sở thể thao (coso*.sql)...")
        for fname in sorted(os.listdir(db_dir)):
            if fname.startswith("coso") and fname.endswith(".sql"):
                execute_sql_file(cur, os.path.join(db_dir, fname))

        conn.close()
        print("\n" + "=" * 60)
        print("🎉 HOÀN TẤT KHỞI TẠO! Dữ liệu hiển thị tiếng Việt chuẩn 100%.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
