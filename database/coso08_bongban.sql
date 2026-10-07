-- ============================================================================
-- database/coso08_bongban.sql
-- CoSoId: 8 | Môn: Bóng bàn | Kiểu đặt lịch: SAN
-- Thành viên phụ trách: Cơ sở 08 (Bóng Bàn)
-- ============================================================================

USE TrungTamTheThao;
GO

-- 1. Tài nguyên của cơ sở Bóng bàn (TaiNguyen: loại 'Ban', CoSoId = 8)
-- Ít nhất 3 dòng theo checklist mục 10
IF NOT EXISTS (SELECT 1 FROM TaiNguyen WHERE CoSoId = 8)
BEGIN
    INSERT INTO TaiNguyen (CoSoId, TenTaiNguyen, Loai, SucChua, GiaMoiGio, TrangThai)
    VALUES
        (8, N'Bàn 01 — DHS Rainbow Pro (Thi đấu ITTF)', 'Ban', 4, 60000, 'Hoat dong'),
        (8, N'Bàn 02 — Butterfly Octet 25 (Cao cấp)',   'Ban', 4, 55000, 'Hoat dong'),
        (8, N'Bàn 03 — Double Fish 233 (Tập luyện A)',  'Ban', 4, 45000, 'Hoat dong'),
        (8, N'Bàn 04 — Double Fish 233 (Tập luyện B)',  'Ban', 4, 45000, 'Hoat dong'),
        (8, N'Bàn 05 — Robot Bắn Bóng PongBot AI',       'Ban', 2, 70000, 'Hoat dong'),
        (8, N'Bàn 06 — Phòng VIP Đơn Lập Khép Kín',     'Ban', 4, 90000, 'Hoat dong');
END
GO

-- 2. Bảng riêng môn Bóng bàn: BongBan_Ban
-- Bắt buộc có CoSoId và TaiNguyenId theo quy ước mục 3
IF OBJECT_ID('dbo.BongBan_Ban', 'U') IS NULL
BEGIN
    CREATE TABLE BongBan_Ban (
        BongBanId     INT IDENTITY(1,1) PRIMARY KEY,
        TaiNguyenId   INT NOT NULL UNIQUE REFERENCES TaiNguyen(TaiNguyenId),
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        ThuongHieu    VARCHAR(50) NOT NULL,    -- 'DHS' | 'Butterfly' | 'Double Fish' | 'PongBot'
        DoDayMatBan   VARCHAR(20) NOT NULL,    -- '25mm' | '18mm'
        CoRobotAI     BIT NOT NULL DEFAULT 0,
        CoPhongRieng  BIT NOT NULL DEFAULT 0,
        GiaCaoDiem    INT NULL                 -- Phụ thu khung giờ 17h-22h
    );

    -- Seed thuộc tính chi tiết
    INSERT INTO BongBan_Ban (TaiNguyenId, CoSoId, ThuongHieu, DoDayMatBan, CoRobotAI, CoPhongRieng, GiaCaoDiem)
    SELECT TaiNguyenId, 8,
           CASE
               WHEN TenTaiNguyen LIKE '%DHS%'       THEN 'DHS'
               WHEN TenTaiNguyen LIKE '%Butterfly%' THEN 'Butterfly'
               WHEN TenTaiNguyen LIKE '%Robot%'     THEN 'PongBot'
               ELSE 'Double Fish'
           END,
           '25mm',
           CASE WHEN TenTaiNguyen LIKE '%Robot%' THEN 1 ELSE 0 END,
           CASE WHEN TenTaiNguyen LIKE '%VIP%'   THEN 1 ELSE 0 END,
           GiaMoiGio + 10000
    FROM TaiNguyen WHERE CoSoId = 8;
END
GO

-- 3. Bảng riêng môn Bóng bàn: BongBan_HLV
IF OBJECT_ID('dbo.BongBan_HLV', 'U') IS NULL
BEGIN
    CREATE TABLE BongBan_HLV (
        HlvId         INT IDENTITY(1,1) PRIMARY KEY,
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        HoTen         NVARCHAR(100) NOT NULL,
        DanhHieu      NVARCHAR(100),           -- 'Kiện tướng quốc gia', 'ITTF Level 1'
        KinhNghiemNam INT NOT NULL DEFAULT 0,
        GiaMoiGio     INT NOT NULL,
        SoDienThoai   VARCHAR(15)
    );

    INSERT INTO BongBan_HLV (CoSoId, HoTen, DanhHieu, KinhNghiemNam, GiaMoiGio, SoDienThoai)
    VALUES
        (8, N'Nguyễn Tiến Đạt', N'Kiện Tướng Quốc Gia',        10, 120000, '0912345801'),
        (8, N'Trần Hải Yến',    N'Cựu VĐV Đội Tuyển Trẻ',       7, 100000, '0912345802'),
        (8, N'Vũ Đình Phong',   N'HLV Chứng Chỉ ITTF Level 1',  5,  80000, '0912345803');
END
GO

-- 4. Bảng riêng môn Bóng bàn: BongBan_DichVu
IF OBJECT_ID('dbo.BongBan_DichVu', 'U') IS NULL
BEGIN
    CREATE TABLE BongBan_DichVu (
        DichVuId      INT IDENTITY(1,1) PRIMARY KEY,
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        TenDichVu     NVARCHAR(100) NOT NULL,
        DonGia        INT NOT NULL,
        DonViTinh     NVARCHAR(30) NOT NULL DEFAULT N'cái'
    );

    INSERT INTO BongBan_DichVu (CoSoId, TenDichVu, DonGia, DonViTinh)
    VALUES
        (8, N'Thuê vợt Butterfly Timo Boll',        15000, N'cây/buổi'),
        (8, N'Hộp bóng DHS D40+ 3 sao (6 quả)',     40000, N'hộp'),
        (8, N'Thuê rổ bóng tập 100 quả',            30000, N'rổ/buổi'),
        (8, N'Khăn lạnh ướp đá cao cấp',            10000, N'cái'),
        (8, N'Nước Pocari Sweat điện giải',         20000, N'chai');
END
GO

-- Seed Tài khoản Quản lý cho cơ sở Bóng Bàn (CoSoId = 8)
-- Mật khẩu: quanly123 -> SHA-256('quanly123') = 'd79b9a528e142dd23dfb0f9c2d1b8c084f74d0818318ec7ec1368923a1a5b481'
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly_bongban')
BEGIN
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly_bongban', 'd79b9a528e142dd23dfb0f9c2d1b8c084f74d0818318ec7ec1368923a1a5b481', N'Trần Quản Lý Bóng Bàn', 'quanly@bongban.vn', 'QuanLy', 8);
END
GO

-- Seed Gói hội viên cho cơ sở Bóng Bàn
IF NOT EXISTS (SELECT 1 FROM GoiHoiVien WHERE CoSoId = 8)
BEGIN
    INSERT INTO GoiHoiVien (CoSoId, TenGoi, SoNgay, Gia)
    VALUES
        (8, N'Gói Hội Viên Bàn Tháng', 30,  250000),
        (8, N'Gói Hội Viên Bàn Quý',   90,  600000),
        (8, N'Gói VIP Đỉnh Cao Năm',   365, 1800000);
END
GO

PRINT N'[coso08_bongban.sql] ✅ Hoàn thành bảng và dữ liệu mẫu cơ sở 8 (Bóng Bàn)!';
GO
