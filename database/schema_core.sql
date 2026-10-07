-- ============================================================================
-- database/schema_core.sql
-- Database: TrungTamTheThao
-- BẢNG LÕI HỆ THỐNG CHUỖI 10 CƠ SỞ (Đều có CoSoId)
-- Thiết kế IF OBJECT_ID(...) IS NULL CREATE TABLE để chạy lại nhiều lần an toàn
-- ============================================================================

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'TrungTamTheThao')
BEGIN
    CREATE DATABASE TrungTamTheThao;
END
GO

USE TrungTamTheThao;
GO

-- ── 1. Bảng CoSo (10 cơ sở thể thao thành viên) ──────────────────────────────
IF OBJECT_ID('dbo.CoSo', 'U') IS NULL
BEGIN
    CREATE TABLE CoSo (
        CoSoId        INT PRIMARY KEY,
        TenCoSo       NVARCHAR(100) NOT NULL,
        MonTheThao    NVARCHAR(50)  NOT NULL,
        DiaChi        NVARCHAR(200),
        GioMoCua      TIME,
        GioDongCua    TIME,
        KieuDatLich   VARCHAR(20)   NOT NULL  -- 'SAN' | 'LOP' | 'THE'
    );
END
GO

-- ── 2. Bảng TaiKhoan (Tài khoản người dùng tập trung) ─────────────────────────
IF OBJECT_ID('dbo.TaiKhoan', 'U') IS NULL
BEGIN
    CREATE TABLE TaiKhoan (
        TaiKhoanId    INT IDENTITY(1,1) PRIMARY KEY,
        TenDangNhap   VARCHAR(50) UNIQUE NOT NULL,
        MatKhauHash   VARCHAR(255) NOT NULL,
        HoTen         NVARCHAR(100),
        Email         VARCHAR(100),
        VaiTro        VARCHAR(20) NOT NULL,      -- 'Admin' | 'QuanLy' | 'HLV' | 'HoiVien'
        CoSoId        INT NULL REFERENCES CoSo(CoSoId)  -- Admin và HoiVien: NULL
    );
END
GO

-- ── 3. Bảng GoiHoiVien (Gói thẻ tập theo từng cơ sở) ──────────────────────────
IF OBJECT_ID('dbo.GoiHoiVien', 'U') IS NULL
BEGIN
    CREATE TABLE GoiHoiVien (
        GoiId         INT IDENTITY(1,1) PRIMARY KEY,
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        TenGoi        NVARCHAR(100) NOT NULL,
        SoNgay        INT NOT NULL,
        Gia           INT NOT NULL
    );
END
GO

-- ── 4. Bảng TheHoiVien (Thẻ hội viên đã đăng ký) ─────────────────────────────
IF OBJECT_ID('dbo.TheHoiVien', 'U') IS NULL
BEGIN
    CREATE TABLE TheHoiVien (
        TheId         INT IDENTITY(1,1) PRIMARY KEY,
        TaiKhoanId    INT NOT NULL REFERENCES TaiKhoan(TaiKhoanId),
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        GoiId         INT NOT NULL REFERENCES GoiHoiVien(GoiId),
        NgayBatDau    DATE DEFAULT GETDATE(),
        NgayHetHan    DATE,
        TrangThai     VARCHAR(20) DEFAULT 'ConHan'  -- 'ConHan' | 'HetHan' | 'Khoa'
    );
END
ELSE IF COL_LENGTH('dbo.TheHoiVien', 'CoSoId') IS NULL
BEGIN
    ALTER TABLE dbo.TheHoiVien ADD CoSoId INT NULL REFERENCES CoSo(CoSoId);
END
GO

-- ── 5. Bảng TaiNguyen (Sân bãi, bàn tập, hồ bơi, làn, phòng tập) ─────────────
IF OBJECT_ID('dbo.TaiNguyen', 'U') IS NULL
BEGIN
    CREATE TABLE TaiNguyen (
        TaiNguyenId   INT IDENTITY(1,1) PRIMARY KEY,
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        TenTaiNguyen  NVARCHAR(100) NOT NULL,
        Loai          VARCHAR(30) NOT NULL,        -- 'San' | 'Lan' | 'Phong' | 'Ban' | 'Lop'
        SucChua       INT DEFAULT 4,
        GiaMoiGio     INT NOT NULL,
        TrangThai     VARCHAR(20) DEFAULT 'Hoat dong'  -- 'Hoat dong' | 'Bao tri'
    );
END
GO

-- ── 6. Bảng DatLich (Đơn giữ chỗ và đặt sân trực tuyến) ───────────────────────
IF OBJECT_ID('dbo.DatLich', 'U') IS NULL
BEGIN
    CREATE TABLE DatLich (
        DatLichId     INT IDENTITY(1,1) PRIMARY KEY,
        TaiKhoanId    INT NOT NULL REFERENCES TaiKhoan(TaiKhoanId),
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        TaiNguyenId   INT NULL REFERENCES TaiNguyen(TaiNguyenId),
        BatDau        DATETIME NOT NULL,
        KetThuc       DATETIME NOT NULL,
        SoNguoi       INT DEFAULT 1,
        TongTien      INT NOT NULL,
        TrangThai     VARCHAR(20) DEFAULT 'ChoThanhToan',  -- 'ChoThanhToan' | 'DaThanhToan' | 'Huy' | 'HoanThanh'
        MaQR          VARCHAR(100),
        NgayTao       DATETIME DEFAULT GETDATE()
    );
END
GO

-- ── 7. Bảng HoaDon (Hóa đơn thanh toán) ──────────────────────────────────────
IF OBJECT_ID('dbo.HoaDon', 'U') IS NULL
BEGIN
    CREATE TABLE HoaDon (
        HoaDonId      INT IDENTITY(1,1) PRIMARY KEY,
        TaiKhoanId    INT NOT NULL REFERENCES TaiKhoan(TaiKhoanId),
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        DatLichId     INT NULL REFERENCES DatLich(DatLichId),
        TheId         INT NULL REFERENCES TheHoiVien(TheId),
        SoTien        INT NOT NULL,
        PhuongThuc    VARCHAR(30) DEFAULT 'ChuyenKhoan', -- 'TienMat' | 'ChuyenKhoan' | 'The'
        TrangThai     VARCHAR(20) DEFAULT 'DaThanhToan',  -- 'DaThanhToan' | 'ChoXuLy' | 'Huy'
        NgayTao       DATETIME DEFAULT GETDATE()
    );
END
GO

-- ── 8. Bảng DanhGia (Đánh giá trải nghiệm dịch vụ) ───────────────────────────
IF OBJECT_ID('dbo.DanhGia', 'U') IS NULL
BEGIN
    CREATE TABLE DanhGia (
        DanhGiaId     INT IDENTITY(1,1) PRIMARY KEY,
        TaiKhoanId    INT NOT NULL REFERENCES TaiKhoan(TaiKhoanId),
        CoSoId        INT NOT NULL REFERENCES CoSo(CoSoId),
        SoSao         TINYINT CHECK (SoSao BETWEEN 1 AND 5),
        NoiDung       NVARCHAR(500),
        NgayTao       DATETIME DEFAULT GETDATE()
    );
END
GO

PRINT N'[schema_core.sql] ✅ Đã khởi tạo hoàn tất 8 bảng lõi hệ thống TrungTamTheThao!';
GO
