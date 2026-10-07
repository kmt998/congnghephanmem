"""
run.py — Lệnh chạy nhanh ứng dụng Flask cho toàn nhóm
Chạy: py run.py
"""

import sys
import os

# Đảm bảo PYTHONPATH nhận diện được thư mục gốc
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from webtong.app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  TRUNG TAM THE THAO DA NANG - CHUOI 10 CO SO")
    print("  * Web tong:        http://localhost:5000")
    print("  * Co so Bong Ban:  http://localhost:5000/coso/8")
    print("  * Dat ban bong ban:http://localhost:5000/coso/8/dat-lich")
    print("  * Dang nhap:       http://localhost:5000/auth/dang-nhap")
    print("=" * 65 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
