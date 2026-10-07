-- ============================================================================
-- database/seed_core.sql
-- DỮ LIỆU MẪU LÕI: 10 Cơ Sở Thể Thao + Tài Khoản Test (Admin, 10 Quản Lý, Hội Viên)
-- Kiểm tra tồn tại trước khi INSERT (chạy nhiều lần an toàn, không bị trùng lặp)
-- ============================================================================

USE TrungTamTheThao;
GO

-- ── 1. Seed 10 Cơ Sở Thể Thao ────────────────────────────────────────────────
MERGE INTO CoSo AS Target
USING (VALUES
    (1,  N'Cơ sở Bơi Lội Lam Sơn',       N'Bơi lội',        N'242 Trần Bình Trọng, Quận 5, TP.HCM',      '06:00', '21:00', 'THE'),
    (2,  N'Cơ sở Gym Thể Hình FitPro',   N'Gym / Thể hình', N'56 Nguyễn Thị Thập, Quận 7, TP.HCM',       '05:30', '22:00', 'THE'),
    (3,  N'Cơ sở Cầu Lông Thành Phát',   N'Cầu lông',       N'18A Phan Văn Trị, Gò Vấp, TP.HCM',         '06:00', '22:30', 'SAN'),
    (4,  N'Cơ sở Bóng Đá Mini Chảo Lửa', N'Bóng đá mini',   N'30 Phan Thúc Duyện, Tân Bình, TP.HCM',     '06:00', '23:00', 'SAN'),
    (5,  N'Cơ sở Tennis SportChain Q7',  N'Tennis',         N'123 Nguyễn Văn Linh, Quận 7, TP.HCM',      '06:00', '22:00', 'SAN'),
    (6,  N'Cơ sở Yoga Tĩnh Tâm',         N'Yoga',           N'88 Lê Văn Sỹ, Phú Nhuận, TP.HCM',          '06:00', '20:30', 'LOP'),
    (7,  N'Cơ sở Bóng Rổ HoopZone',      N'Bóng rổ',        N'102 Sư Vạn Hạnh, Quận 10, TP.HCM',         '07:00', '22:00', 'SAN'),
    (8,  N'Cơ sở Bóng Bàn Đỉnh Cao',     N'Bóng bàn',       N'45 Đinh Tiên Hoàng, Quận 1, TP.HCM',       '07:30', '21:30', 'SAN'),
    (9,  N'Cơ sở Võ Thuật Tân Võ Đạo',   N'Võ thuật',       N'15 Võ Văn Tần, Quận 3, TP.HCM',            '06:30', '21:00', 'LOP'),
    (10, N'Cơ sở Pickleball D-Sport',    N'Pickleball',     N'99 Mai Chí Thọ, TP. Thủ Đức, TP.HCM',      '06:00', '22:00', 'SAN')
) AS Source (CoSoId, TenCoSo, MonTheThao, DiaChi, GioMoCua, GioDongCua, KieuDatLich)
ON Target.CoSoId = Source.CoSoId
WHEN MATCHED THEN
    UPDATE SET TenCoSo     = Source.TenCoSo,
               MonTheThao  = Source.MonTheThao,
               DiaChi      = Source.DiaChi,
               GioMoCua    = Source.GioMoCua,
               GioDongCua  = Source.GioDongCua,
               KieuDatLich = Source.KieuDatLich
WHEN NOT MATCHED THEN
    INSERT (CoSoId, TenCoSo, MonTheThao, DiaChi, GioMoCua, GioDongCua, KieuDatLich)
    VALUES (Source.CoSoId, Source.TenCoSo, Source.MonTheThao, Source.DiaChi, Source.GioMoCua, Source.GioDongCua, Source.KieuDatLich);
GO

-- ── 2. Seed Tài Khoản Admin Hệ Thống (Mật khẩu: admin123) ───────────────────
-- SHA-256('admin123') = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'admin')
BEGIN
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES (
        'admin',
        '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
        N'Quản Trị Viên Hệ Thống',
        'admin@trungtamthethao.vn',
        'Admin',
        NULL
    );
END
GO

-- ── 3. Seed 10 Tài Khoản Quản Lý (Mỗi cơ sở 1 Quản lý, Mật khẩu: 123456) ────
-- SHA-256('123456') = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
DECLARE @PassHash VARCHAR(255) = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92';

-- CS01: Bơi Lội
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly01')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly01', @PassHash, N'Quản Lý Bơi Lội', 'quanly01@trungtamthethao.vn', 'QuanLy', 1);

-- CS02: Gym
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly02')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly02', @PassHash, N'Quản Lý Gym', 'quanly02@trungtamthethao.vn', 'QuanLy', 2);

-- CS03: Cầu Lông
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly03')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly03', @PassHash, N'Quản Lý Cầu Lông', 'quanly03@trungtamthethao.vn', 'QuanLy', 3);

-- CS04: Bóng Đá
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly04')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly04', @PassHash, N'Quản Lý Bóng Đá', 'quanly04@trungtamthethao.vn', 'QuanLy', 4);

-- CS05: Tennis
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly05')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly05', @PassHash, N'Quản Lý Tennis', 'quanly05@trungtamthethao.vn', 'QuanLy', 5);

-- CS06: Yoga
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly06')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly06', @PassHash, N'Quản Lý Yoga', 'quanly06@trungtamthethao.vn', 'QuanLy', 6);

-- CS07: Bóng Rổ
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly07')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly07', @PassHash, N'Quản Lý Bóng Rổ', 'quanly07@trungtamthethao.vn', 'QuanLy', 7);

-- CS08: Bóng Bàn
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly08')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly08', @PassHash, N'Quản Lý Bóng Bàn', 'quanly08@trungtamthethao.vn', 'QuanLy', 8);

-- CS09: Võ Thuật
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly09')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly09', @PassHash, N'Quản Lý Võ Thuật', 'quanly09@trungtamthethao.vn', 'QuanLy', 9);

-- CS10: Pickleball
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly10')
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly10', @PassHash, N'Quản Lý Pickleball', 'quanly10@trungtamthethao.vn', 'QuanLy', 10);
GO

-- ── 4. Seed 1 Tài Khoản Hội Viên Thử Nghiệm (Mật khẩu: 123456) ─────────────────
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'hoivien01')
BEGIN
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES (
        'hoivien01',
        '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
        N'Hội Viên Thử Nghiệm',
        'hoivien01@gmail.com',
        'HoiVien',
        NULL
    );
END
GO

PRINT N'[seed_core.sql] ✅ Đã nạp dữ liệu mẫu 10 cơ sở + 1 Admin + 10 Quản lý + 1 Hội viên!';
GO
