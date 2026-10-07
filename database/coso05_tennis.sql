-- ============================================================================
-- database/coso05_tennis.sql
-- CoSoId: 5 | Môn: Tennis | Kiểu đặt lịch: SAN
-- Thành viên phụ trách: TV05 (Tennis)
-- ============================================================================

USE TrungTamTheThao;
GO

-- 1. Tài nguyên của cơ sở Tennis (TaiNguyen: loại 'San', CoSoId = 5)
-- Cần ít nhất 3 dòng theo checklist mục 10
IF NOT EXISTS (SELECT 1 FROM TaiNguyen WHERE CoSoId = 5)
BEGIN
    INSERT INTO TaiNguyen (CoSoId, TenTaiNguyen, Loai, SucChua, GiaMoiGio, TrangThai)
    VALUES
        (5, N'Sân Tennis A1 (Hard Court)',   'San', 4, 80000,  'Hoat dong'),
        (5, N'Sân Tennis A2 (Clay Court)',   'San', 4, 70000,  'Hoat dong'),
        (5, N'Sân Tennis B1 (Grass Court)',  'San', 4, 90000,  'Hoat dong'),
        (5, N'Sân Tennis B2 (Indoor VIP)',   'San', 4, 120000, 'Hoat dong');
END
GO

-- 2. Bảng riêng môn Tennis: Tennis_San
-- Bắt buộc có CoSoId và TaiNguyenId theo quy ước mục 3
IF OBJECT_ID('dbo.Tennis_San', 'U') IS NULL
BEGIN
    CREATE TABLE Tennis_San (
        TennisSanId   INT IDENTITY(1,1) PRIMARY KEY,
        TaiNguyenId   INT NOT NULL UNIQUE REFERENCES TaiNguyen(TaiNguyenId),
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        LoaiMatSan    VARCHAR(30) NOT NULL,    -- 'Hard' | 'Clay' | 'Grass' | 'Indoor'
        CoMaiChe      BIT NOT NULL DEFAULT 0,
        CoDenDem      BIT NOT NULL DEFAULT 1,
        GiaCaoDiem    INT NULL                 -- Khung giờ 17h-22h
    );

    -- Seed thuộc tính chi tiết cho từng sân
    INSERT INTO Tennis_San (TaiNguyenId, CoSoId, LoaiMatSan, CoMaiChe, CoDenDem, GiaCaoDiem)
    SELECT TaiNguyenId, 5,
           CASE
               WHEN TenTaiNguyen LIKE '%Hard%'   THEN 'Hard'
               WHEN TenTaiNguyen LIKE '%Clay%'   THEN 'Clay'
               WHEN TenTaiNguyen LIKE '%Grass%'  THEN 'Grass'
               ELSE 'Indoor'
           END,
           CASE WHEN TenTaiNguyen LIKE '%Indoor%' THEN 1 ELSE 0 END,
           1,
           GiaMoiGio + 20000
    FROM TaiNguyen WHERE CoSoId = 5;
END
GO

-- 3. Bảng riêng môn Tennis: Tennis_HLV
IF OBJECT_ID('dbo.Tennis_HLV', 'U') IS NULL
BEGIN
    CREATE TABLE Tennis_HLV (
        HlvId         INT IDENTITY(1,1) PRIMARY KEY,
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        HoTen         NVARCHAR(100) NOT NULL,
        ChungChi      NVARCHAR(100),           -- 'VTF Level 2', 'ITF Level 1'
        KinhNghiemNam INT NOT NULL DEFAULT 0,
        GiaMoiGio     INT NOT NULL,
        HinhAnh       VARCHAR(255),
        SoDienThoai   VARCHAR(15)
    );

    INSERT INTO Tennis_HLV (CoSoId, HoTen, ChungChi, KinhNghiemNam, GiaMoiGio, SoDienThoai)
    VALUES
        (5, N'Nguyễn Minh Khoa', N'VTF Cấp Quốc Gia', 12, 150000, '0901234561'),
        (5, N'Trần Thị Lan Anh', N'VTF Cấp Tỉnh',      8, 120000, '0901234562'),
        (5, N'Lê Văn Hùng',      N'ITF Level 1',        5, 100000, '0901234563');
END
GO

-- 4. Bảng riêng môn Tennis: Tennis_DichVu (Vợt, bóng, nước, khăn)
IF OBJECT_ID('dbo.Tennis_DichVu', 'U') IS NULL
BEGIN
    CREATE TABLE Tennis_DichVu (
        DichVuId      INT IDENTITY(1,1) PRIMARY KEY,
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        TenDichVu     NVARCHAR(100) NOT NULL,
        DonGia        INT NOT NULL,
        DonViTinh     NVARCHAR(30) NOT NULL DEFAULT N'cái'
    );

    INSERT INTO Tennis_DichVu (CoSoId, TenDichVu, DonGia, DonViTinh)
    VALUES
        (5, N'Bóng tennis Wilson (hộp 3 quả)', 30000, N'hộp'),
        (5, N'Thuê vợt Head / Wilson',         20000, N'cây'),
        (5, N'Khăn lạnh ướp đá',               15000, N'cái'),
        (5, N'Nước khoáng điện giải',          25000, N'chai');
END
GO

-- Seed Tài khoản Quản lý cho cơ sở Tennis (CoSoId = 5)
-- Mật khẩu: quanly123 -> SHA-256('quanly123') = '3a557c6...
IF NOT EXISTS (SELECT 1 FROM TaiKhoan WHERE TenDangNhap = 'quanly_tennis')
BEGIN
    INSERT INTO TaiKhoan (TenDangNhap, MatKhauHash, HoTen, Email, VaiTro, CoSoId)
    VALUES ('quanly_tennis', 'd79b9a528e142dd23dfb0f9c2d1b8c084f74d0818318ec7ec1368923a1a5b481', N'Nguyễn Quản Lý Tennis', 'quanly@tennis.vn', 'QuanLy', 5);
END
GO

-- Seed Gói hội viên cho cơ sở Tennis
IF NOT EXISTS (SELECT 1 FROM GoiHoiVien WHERE CoSoId = 5)
BEGIN
    INSERT INTO GoiHoiVien (CoSoId, TenGoi, SoNgay, Gia)
    VALUES
        (5, N'Gói Hội Viên Tháng', 30,  299000),
        (5, N'Gói Hội Viên Quý',   90,  699000),
        (5, N'Gói VIP Thường Niên',365, 1999000);
END
GO

PRINT N'[coso05_tennis.sql] ✅ Hoàn thành bảng và dữ liệu mẫu cơ sở 5 (Tennis)!';
GO
