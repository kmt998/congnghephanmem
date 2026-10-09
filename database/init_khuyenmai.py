# -*- coding: utf-8 -*-
"""
database/init_khuyenmai.py
Khởi tạo bảng KhuyenMai và nạp dữ liệu mẫu ban đầu.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.db import get_db

def init_khuyenmai_table():
    db = get_db()
    cur = db.cursor()

    # 1. Tạo bảng KhuyenMai nếu chưa tồn tại
    cur.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='KhuyenMai' AND xtype='U')
    CREATE TABLE KhuyenMai (
        KhuyenMaiId INT IDENTITY(1,1) PRIMARY KEY,
        MaCode VARCHAR(50) NOT NULL UNIQUE,
        TieuDe NVARCHAR(255) NOT NULL,
        MoTa NVARCHAR(1000) NULL,
        GiamPhanTram INT DEFAULT 0,
        GiamToiDa INT DEFAULT 0,
        Badge NVARCHAR(100) NULL,
        CoSoId INT NULL,
        NgayBatDau DATETIME NULL,
        NgayKetThuc DATETIME NULL,
        TrangThai NVARCHAR(50) DEFAULT 'HoatDong',
        NgayTao DATETIME DEFAULT GETDATE(),
        CONSTRAINT FK_KhuyenMai_CoSo FOREIGN KEY (CoSoId) REFERENCES CoSo(CoSoId)
    );
    """)
    db.commit()

    # 2. Chèn dữ liệu mẫu nếu bảng trống
    cur.execute("SELECT COUNT(*) FROM KhuyenMai")
    cnt = cur.fetchone()[0]
    if cnt == 0:
        cur.execute("""
            INSERT INTO KhuyenMai (MaCode, TieuDe, MoTa, GiamPhanTram, GiamToiDa, Badge, CoSoId, NgayKetThuc, TrangThai)
            VALUES 
            ('CHAOBANMOI', N'Giảm 20% Lần Đặt Sân Đầu Tiên', N'Dành riêng cho tài khoản đăng ký mới trên hệ thống. Giảm trực tiếp 20% tổng hóa đơn thuê sân/bàn tại bất kỳ cơ sở nào trong chuỗi.', 20, 100000, N'Hội Viên Mới', NULL, '2026-12-31 23:59:59', 'HoatDong'),
            ('GIOVANG30', N'Giảm 30% Khung Giờ Ban Ngày', N'Áp dụng cho các ca tập từ 08:00 đến 16:00 các ngày trong tuần (T2 - T6). Tự động giảm khi thanh toán đặt bàn.', 30, 150000, N'Giờ Vàng Giá Sốc', NULL, '2026-12-31 23:59:59', 'HoatDong'),
            ('COMBODUNGCU', N'Đặt Từ 2 Giờ — Mượn Dụng Cụ 0Đ', N'Khi đặt sân hoặc bàn chơi từ 2 giờ trở lên, quý khách được mượn miễn phí 2 vợt thi đấu cao cấp và 1 hộp bóng tiêu chuẩn.', 15, 50000, N'Combo Tiết Kiệm', NULL, '2026-12-31 23:59:59', 'HoatDong'),
            ('HLVPRO5', N'Khóa Kèm HLV 5 Buổi Tặng 1', N'Đăng ký lộ trình 5 buổi học kèm Huấn luyện viên được tặng thêm 1 buổi tập chiến thuật hoàn toàn miễn phí.', 20, 200000, N'Đào Tạo Kèm 1-1', NULL, '2026-12-31 23:59:59', 'HoatDong'),
            ('SPORTPASSVIP', N'Thẻ SportPass Đa Năng 10 Môn', N'Chỉ cần 1 thẻ duy nhất tập luyện linh hoạt tại cả 10 cơ sở: Bơi lội, Gym, Bóng bàn, Cầu lông, Tennis... Giảm thêm 10% các dịch vụ.', 10, 300000, N'Hội Viên Toàn Chuỗi', NULL, '2026-12-31 23:59:59', 'HoatDong')
        """)
        db.commit()
        print("Da chen 5 ma khuyen mai mau thanh cong!")
    else:
        print(f"Bang KhuyenMai da co {cnt} ban ghi.")

    cur.execute("SELECT KhuyenMaiId, MaCode, TieuDe, GiamPhanTram, TrangThai FROM KhuyenMai")
    rows = cur.fetchall()
    for r in rows:
        print(f"ID={r[0]} | Code={r[1]} | TieuDe={r[2]} | Giam={r[3]}% | TrangThai={r[4]}")

    db.close()

if __name__ == "__main__":
    init_khuyenmai_table()
