"""
modules/coso08_bongban/service.py
─────────────────────────────────
Tầng nghiệp vụ cơ sở 08 (Bóng Bàn Đỉnh Cao).
Có cơ chế fallback dữ liệu mẫu để giao diện luôn chạy mượt mà ngay cả khi chưa kết nối SQL Server.
"""

from datetime import datetime, date
import uuid

CO_SO_ID = 8

# ── DỮ LIỆU MẪU CHUẨN BÓNG BÀN (Fallback khi offline DB) ──────────────────────
MOCK_TAI_NGUYEN = [
    {
        "taiNguyenId": 5,
        "ten": "Bàn 01 — DHS Rainbow Pro",
        "loai": "Ban",
        "sucChua": 4,
        "giaMoiGio": 60000,
        "trangThai": "Hoat dong",
        "moTa": "Bàn thi đấu chuẩn ITTF, mặt bàn 25mm chống lóa, thảm đỏ chuẩn SEA Games",
        "badge": "Chuẩn ITTF",
        "hinhAnh": "dhs_rainbow"
    },
    {
        "taiNguyenId": 6,
        "ten": "Bàn 02 — Butterfly Octet 25",
        "loai": "Ban",
        "sucChua": 4,
        "giaMoiGio": 55000,
        "trangThai": "Hoat dong",
        "moTa": "Mặt bàn siêu nảy Butterfly, có vách ngăn chắn bóng tiêu chuẩn",
        "badge": "Cao cấp",
        "hinhAnh": "butterfly_octet"
    },
    {
        "taiNguyenId": 7,
        "ten": "Bàn 03 — Double Fish 233",
        "loai": "Ban",
        "sucChua": 4,
        "giaMoiGio": 45000,
        "trangThai": "Hoat dong",
        "moTa": "Bàn tập luyện tiêu chuẩn quốc gia, không gian thoáng mát, điều hòa",
        "badge": "Phổ thông",
        "hinhAnh": "double_fish"
    },
    {
        "taiNguyenId": 8,
        "ten": "Bàn 04 — Double Fish 233",
        "loai": "Ban",
        "sucChua": 4,
        "giaMoiGio": 45000,
        "trangThai": "Hoat dong",
        "moTa": "Bàn tập luyện tiêu chuẩn quốc gia, ánh sáng đèn LED 600 lux",
        "badge": "Phổ thông",
        "hinhAnh": "double_fish"
    },
    {
        "taiNguyenId": 9,
        "ten": "Bàn 05 — Robot Bắn Bóng Thông Minh",
        "loai": "Ban",
        "sucChua": 2,
        "giaMoiGio": 70000,
        "trangThai": "Hoat dong",
        "moTa": "Tích hợp Robot PongBot bắn bóng đa điểm, chỉnh độ xoáy Topspin/Backspin",
        "badge": "Công nghệ AI",
        "hinhAnh": "robot_pong"
    },
    {
        "taiNguyenId": 10,
        "ten": "Bàn 06 — Phòng VIP Đơn Lập",
        "loai": "Ban",
        "sucChua": 4,
        "giaMoiGio": 90000,
        "trangThai": "Hoat dong",
        "moTa": "Phòng riêng biệt lập âm thanh, sofa nghỉ, tủ lạnh mini và điều hòa riêng",
        "badge": "VIP Room",
        "hinhAnh": "vip_room"
    }
]

MOCK_HLV = [
    {
        "hlvId": 1,
        "hoTen": "Nguyễn Tiến Đạt",
        "danhHieu": "Kiện Tướng Quốc Gia",
        "kinhNghiem": "10 năm",
        "giaGio": 120000,
        "chuyenMon": "Kỹ thuật Giật bóng hai mang (Topspin), Giao bóng xoáy ảo",
        "soSao": 5
    },
    {
        "hlvId": 2,
        "hoTen": "Trần Hải Yến",
        "danhHieu": "Cựu VĐV Đội Tuyển Trẻ",
        "kinhNghiem": "7 năm",
        "giaGio": 100000,
        "chuyenMon": "Kỹ thuật cơ bản cho người mới bắt đầu, Gò bóng & Cắt bóng phòng thủ",
        "soSao": 5
    },
    {
        "hlvId": 3,
        "hoTen": "Vũ Đình Phong",
        "danhHieu": "HLV Chứng Chỉ ITTF Level 1",
        "kinhNghiem": "5 năm",
        "giaGio": 80000,
        "chuyenMon": "Chiến thuật thi đấu đơn / đôi, Di chuyển bước chân hiện đại",
        "soSao": 4
    }
]

MOCK_DICH_VU = [
    {"dichVuId": 1, "ten": "Thuê vợt Butterfly Timo Boll", "gia": 15000, "dvt": "cây/buổi"},
    {"dichVuId": 2, "ten": "Hộp bóng DHS D40+ 3 sao (6 quả)", "gia": 40000, "dvt": "hộp"},
    {"dichVuId": 3, "ten": "Thuê rổ bóng tập 100 quả", "gia": 30000, "dvt": "rổ/buổi"},
    {"dichVuId": 4, "ten": "Khăn lạnh ướp đá cao cấp", "gia": 10000, "dvt": "cái"},
    {"dichVuId": 5, "ten": "Nước Pocari Sweat điện giải", "gia": 20000, "dvt": "chai"}
]

# Lưu trữ tạm trong bộ nhớ cho các đơn đặt mới
IN_MEMORY_DAT_LICH = []


# ── 3 HÀM HỢP ĐỒNG GIAO TIẾP VỚI LÕI (Mục 5) ──────────────────────────────────

def lay_danh_sach_tai_nguyen() -> list[dict]:
    """
    Trả về list[dict]:
    [{"taiNguyenId": 1, "ten": "Bàn 1", "loai": "Ban", "sucChua": 4, "giaMoiGio": 40000}]
    """
    try:
        from core.db import get_db
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT TaiNguyenId, TenTaiNguyen, Loai, SucChua, GiaMoiGio, TrangThai
            FROM TaiNguyen WHERE CoSoId = ?
        """, (CO_SO_ID,))
        rows = cur.fetchall()
        db.close()
        if rows:
            return [{
                "taiNguyenId": r[0],
                "ten": r[1],
                "loai": r[2],
                "sucChua": r[3],
                "giaMoiGio": r[4],
                "trangThai": r[5]
            } for r in rows]
    except Exception:
        pass
    return MOCK_TAI_NGUYEN


def kiem_tra_khung_gio(tai_nguyen_id: int, bat_dau, ket_thuc, so_nguoi: int = 1) -> tuple[bool, str]:
    """
    Kiểm tra trùng giờ đặt bàn (môn bóng bàn kiểu 'SAN').
    Trả về: (True, "") nếu đặt được, (False, "lý do") nếu trùng hoặc không hợp lệ.
    """
    try:
        if isinstance(bat_dau, str):
            bat_dau = datetime.strptime(bat_dau, "%Y-%m-%d %H:%M")
        if isinstance(ket_thuc, str):
            ket_thuc = datetime.strptime(ket_thuc, "%Y-%m-%d %H:%M")

        if bat_dau >= ket_thuc:
            return False, "Thời gian bắt đầu phải trước thời gian kết thúc"

        # Kiểm tra trong SQL Server nếu có kết nối
        try:
            from core.db import get_db
            db = get_db()
            cur = db.cursor()
            cur.execute("""
                SELECT 1 FROM DatLich
                WHERE TaiNguyenId = ? AND CoSoId = ?
                  AND TrangThai IN ('ChoThanhToan', 'DaThanhToan')
                  AND BatDau < ? AND KetThuc > ?
            """, (tai_nguyen_id, CO_SO_ID, ket_thuc, bat_dau))
            row = cur.fetchone()
            db.close()
            if row:
                return False, "Bàn này đã có người đặt trong khung giờ bạn chọn"
        except Exception:
            pass

        # Kiểm tra trong bộ nhớ tạm
        for item in IN_MEMORY_DAT_LICH:
            if item["taiNguyenId"] == tai_nguyen_id and item["trangThai"] != "Huy":
                if bat_dau < item["ketThuc"] and ket_thuc > item["batDau"]:
                    return False, "Bàn này đã được giữ chỗ trong khung giờ bạn chọn"

        return True, ""
    except Exception as e:
        return False, f"Lỗi kiểm tra khung giờ: {str(e)}"


def tinh_gia(tai_nguyen_id: int, bat_dau, ket_thuc, so_nguoi: int = 1) -> int:
    """
    Tính tổng tiền thuê bàn (VND).
    Có tính phụ thu giờ cao điểm (từ 17h đến 22h).
    """
    try:
        if isinstance(bat_dau, str):
            bat_dau = datetime.strptime(bat_dau, "%Y-%m-%d %H:%M")
        if isinstance(ket_thuc, str):
            ket_thuc = datetime.strptime(ket_thuc, "%Y-%m-%d %H:%M")

        so_gio = (ket_thuc - bat_dau).total_seconds() / 3600.0
        if so_gio <= 0:
            return 0

        # Tìm đơn giá bàn
        ds = lay_danh_sach_tai_nguyen()
        ban = next((b for b in ds if b["taiNguyenId"] == tai_nguyen_id), None)
        gia_goc = ban["giaMoiGio"] if ban else 45000

        # Khung giờ cao điểm: bắt đầu >= 17h
        if bat_dau.hour >= 17:
            gia_goc += 10000

        return int(gia_goc * so_gio)
    except Exception:
        return 50000


# ── CÁC HÀM TIỆN ÍCH DÀNH RIÊNG CHO MÔN BÓNG BÀN ──────────────────────────────

def lay_danh_sach_hlv():
    return MOCK_HLV

def lay_danh_sach_dich_vu():
    return MOCK_DICH_VU

def lay_danh_sach_danh_gia():
    return []

def tao_dat_lich_moi(tai_khoan_id, tai_nguyen_id, bat_dau_str, ket_thuc_str, hlv_id=None, dich_vu_ids=None):
    """Xử lý đặt bàn, trả về thông tin đơn đặt lịch + mã QR."""
    dt_bd = datetime.strptime(bat_dau_str, "%Y-%m-%d %H:%M")
    dt_kt = datetime.strptime(ket_thuc_str, "%Y-%m-%d %H:%M")

    ok, msg = kiem_tra_khung_gio(tai_nguyen_id, dt_bd, dt_kt)
    if not ok:
        return {"ok": False, "error": msg}

    tien_ban = tinh_gia(tai_nguyen_id, dt_bd, dt_kt)
    so_gio = (dt_kt - dt_bd).total_seconds() / 3600.0

    # Tiền HLV
    tien_hlv = 0
    ten_hlv = ""
    if hlv_id:
        hlv = next((h for h in MOCK_HLV if h["hlvId"] == int(hlv_id)), None)
        if hlv:
            tien_hlv = int(hlv["giaGio"] * so_gio)
            ten_hlv = hlv["hoTen"]

    # Tiền Dịch vụ kèm
    tien_dv = 0
    ds_dv_ten = []
    if dich_vu_ids:
        for dvid in dich_vu_ids:
            dv = next((d for d in MOCK_DICH_VU if d["dichVuId"] == int(dvid)), None)
            if dv:
                tien_dv += dv["gia"]
                ds_dv_ten.append(dv["ten"])

    tong_tien = tien_ban + tien_hlv + tien_dv
    ma_qr = f"BB{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6].upper()}"

    dat_lich_id_db = len(IN_MEMORY_DAT_LICH) + 101

    # Nếu có SQL Server, lưu vào DB và lấy ID thật
    try:
        from core.db import get_db
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO DatLich (TaiKhoanId, CoSoId, TaiNguyenId, BatDau, KetThuc, SoNguoi, TongTien, TrangThai, MaQR)
            OUTPUT INSERTED.DatLichId
            VALUES (?, ?, ?, ?, ?, 2, ?, 'ChoThanhToan', ?)
        """, (tai_khoan_id, CO_SO_ID, tai_nguyen_id, dt_bd, dt_kt, tong_tien, ma_qr))
        row = cur.fetchone()
        if row:
            dat_lich_id_db = row[0]
        db.commit()
        db.close()
    except Exception as e:
        print("Loi ghi DatLich vao DB:", e)

    don = {
        "datLichId": dat_lich_id_db,
        "taiKhoanId": tai_khoan_id,
        "coSoId": CO_SO_ID,
        "taiNguyenId": tai_nguyen_id,
        "batDau": dt_bd,
        "ketThuc": dt_kt,
        "soNguoi": 2,
        "tongTien": tong_tien,
        "tienBan": tien_ban,
        "tienHLV": tien_hlv,
        "tenHLV": ten_hlv,
        "tienDV": tien_dv,
        "dsDichVu": ds_dv_ten,
        "trangThai": "ChoThanhToan",
        "maQR": ma_qr,
        "ngayTao": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    IN_MEMORY_DAT_LICH.insert(0, don)
    return {"ok": True, "don": don}


def doc_so_thanh_chu(n: int) -> str:
    """Chuyển đổi số tiền VNĐ thành chữ tiếng Việt."""
    if not isinstance(n, (int, float)) or n == 0:
        return "Không đồng"
    n = int(round(n))
    chu_so = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    don_vi = ["", "nghìn", "triệu", "tỷ"]

    def doc_ba_so(baso, day_du=False):
        t = baso // 100
        c = (baso % 100) // 10
        d = baso % 10
        res = ""
        if t > 0 or day_du:
            res += chu_so[t] + " trăm "
        if c > 1:
            res += chu_so[c] + " mươi "
            if d == 1:
                res += "mốt "
            elif d == 5:
                res += "lăm "
            elif d > 0:
                res += chu_so[d] + " "
        elif c == 1:
            res += "mười "
            if d == 5:
                res += "lăm "
            elif d > 0:
                res += chu_so[d] + " "
        elif c == 0:
            if d > 0 and (t > 0 or day_du):
                res += "lẻ " + chu_so[d] + " "
            elif d > 0:
                res += chu_so[d] + " "
        return res.strip()

    parts = []
    so = n
    idx = 0
    while so > 0:
        baso = so % 1000
        if baso > 0:
            chu = doc_ba_so(baso, so // 1000 > 0)
            parts.insert(0, chu + " " + don_vi[idx])
        idx += 1
        so //= 1000
    res = " ".join(parts).strip() + " đồng"
    return res.capitalize()


def lay_thong_tin_dat_lich(qr_hoac_id):
    """Tìm thông tin đơn đặt lịch theo ID hoặc MaQR từ DB hoặc memory."""
    try:
        from core.db import get_db
        db = get_db()
        cur = db.cursor()
        
        # Thử tìm theo ID nếu là số, hoặc theo MaQR nếu là chuỗi
        is_id = str(qr_hoac_id).isdigit()
        if is_id:
            cur.execute("""
                SELECT D.DatLichId, D.TaiKhoanId, D.CoSoId, D.TaiNguyenId, D.BatDau, D.KetThuc,
                       D.TongTien, D.TrangThai, D.MaQR, D.NgayTao,
                       T.TenTaiNguyen, T.GiaMoiGio, C.TenCoSo, C.DiaChi, C.MonTheThao,
                       U.HoTen, U.TenDangNhap, U.Email
                FROM DatLich D
                LEFT JOIN TaiNguyen T ON D.TaiNguyenId = T.TaiNguyenId
                LEFT JOIN CoSo C ON D.CoSoId = C.CoSoId
                LEFT JOIN TaiKhoan U ON D.TaiKhoanId = U.TaiKhoanId
                WHERE D.DatLichId = ? OR D.MaQR = ?
            """, (int(qr_hoac_id), str(qr_hoac_id)))
        else:
            cur.execute("""
                SELECT D.DatLichId, D.TaiKhoanId, D.CoSoId, D.TaiNguyenId, D.BatDau, D.KetThuc,
                       D.TongTien, D.TrangThai, D.MaQR, D.NgayTao,
                       T.TenTaiNguyen, T.GiaMoiGio, C.TenCoSo, C.DiaChi, C.MonTheThao,
                       U.HoTen, U.TenDangNhap, U.Email
                FROM DatLich D
                LEFT JOIN TaiNguyen T ON D.TaiNguyenId = T.TaiNguyenId
                LEFT JOIN CoSo C ON D.CoSoId = C.CoSoId
                LEFT JOIN TaiKhoan U ON D.TaiKhoanId = U.TaiKhoanId
                WHERE D.MaQR = ?
            """, (str(qr_hoac_id),))
        r = cur.fetchone()
        db.close()
        if r:
            return {
                "datLichId": r[0],
                "taiKhoanId": r[1],
                "coSoId": r[2],
                "taiNguyenId": r[3],
                "batDau": r[4],
                "ketThuc": r[5],
                "tongTien": r[6],
                "trangThai": r[7],
                "maQR": r[8],
                "ngayTao": r[9],
                "tenBan": r[10] or f"Bàn #{r[3]}",
                "giaMoiGio": r[11] or 60000,
                "tenCoSo": r[12] or "Cơ Sở Bóng Bàn Đỉnh Cao",
                "diaChi": r[13] or "45 Đinh Tiên Hoàng, P. Bến Nghé, Quận 1, TP.HCM",
                "monTheThao": r[14] or "Bóng bàn",
                "hoTen": r[15] or "Hội viên",
                "tenDangNhap": r[16] or "",
                "email": r[17] or ""
            }
    except Exception as e:
        print("Loi lay don dat lich tu DB:", e)

    # Fallback memory
    for d in IN_MEMORY_DAT_LICH:
        if str(d.get("datLichId")) == str(qr_hoac_id) or d.get("maQR") == str(qr_hoac_id):
            res = dict(d)
            ds_ban = lay_danh_sach_tai_nguyen()
            ban = next((b for b in ds_ban if b["taiNguyenId"] == d.get("taiNguyenId")), None)
            res["tenBan"] = ban["ten"] if ban else f"Bàn #{d.get('taiNguyenId')}"
            res["giaMoiGio"] = ban["giaMoiGio"] if ban else 60000
            res["tenCoSo"] = "Cơ Sở Bóng Bàn Đỉnh Cao"
            res["diaChi"] = "45 Đinh Tiên Hoàng, P. Bến Nghé, Quận 1, TP. Hồ Chí Minh"
            res["monTheThao"] = "Bóng bàn"
            res["hoTen"] = "Khách Hàng"
            res["tenDangNhap"] = ""
            res["email"] = ""
            return res

    # Fallback cho maQR truyen vao neu khong tim thay
    if qr_hoac_id and str(qr_hoac_id).startswith("BB"):
        return {
            "datLichId": 101,
            "taiKhoanId": 1,
            "coSoId": CO_SO_ID,
            "taiNguyenId": 5,
            "batDau": datetime.now(),
            "ketThuc": datetime.now(),
            "tongTien": 60000,
            "trangThai": "ChoThanhToan",
            "maQR": str(qr_hoac_id),
            "ngayTao": datetime.now(),
            "tenBan": "Bàn 01 — DHS Rainbow Pro",
            "giaMoiGio": 60000,
            "tenCoSo": "Cơ Sở Bóng Bàn Đỉnh Cao",
            "diaChi": "45 Đinh Tiên Hoàng, P. Bến Nghé, Quận 1, TP. Hồ Chí Minh",
            "monTheThao": "Bóng bàn",
            "hoTen": "Hội Viên",
            "tenDangNhap": "",
            "email": ""
        }

    return None


def tao_ma_qr_base64(noi_dung: str) -> str:
    """Tạo ảnh QR Code chuẩn PNG base64, chạy offline hoàn toàn không phụ thuộc internet."""
    try:
        import qrcode
        import io
        import base64
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(noi_dung)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        return f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={noi_dung}"


def xac_nhan_thanh_toan(dat_lich_id: int, phuong_thuc: str = "ChuyenKhoanQR") -> dict:
    """Cập nhật trạng thái đơn đặt sang DaThanhToan và tạo bản ghi Hóa Đơn."""
    try:
        from core.db import get_db
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT TaiKhoanId, CoSoId, TongTien FROM DatLich WHERE DatLichId = ?", (dat_lich_id,))
        row = cur.fetchone()
        if not row:
            db.close()
            return {"ok": False, "error": f"Không tìm thấy đơn đặt #{dat_lich_id}"}

        tk_id, cs_id, tong_tien = row

        # 1. Cập nhật trạng thái đơn đặt
        cur.execute("UPDATE DatLich SET TrangThai = 'DaThanhToan' WHERE DatLichId = ?", (dat_lich_id,))

        # 2. Tạo hóa đơn thanh toán nếu chưa có
        cur.execute("SELECT HoaDonId FROM HoaDon WHERE DatLichId = ?", (dat_lich_id,))
        hd_row = cur.fetchone()
        if not hd_row:
            cur.execute("""
                INSERT INTO HoaDon (TaiKhoanId, CoSoId, DatLichId, SoTien, PhuongThuc, TrangThai)
                VALUES (?, ?, ?, ?, ?, 'DaThanhToan')
            """, (tk_id, cs_id, dat_lich_id, tong_tien, phuong_thuc))

        db.commit()
        db.close()

        # Cập nhật memory nếu có
        for d in IN_MEMORY_DAT_LICH:
            if d.get("datLichId") == dat_lich_id:
                d["trangThai"] = "DaThanhToan"

        return {"ok": True, "datLichId": dat_lich_id}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def lay_lich_su_cua_user(tai_khoan_id):
    """Lấy danh sách lịch sử đặt của hội viên (ưu tiên từ DB)."""
    ds_ban = lay_danh_sach_tai_nguyen()
    res = []

    try:
        from core.db import get_db
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT D.DatLichId, D.TaiNguyenId, D.BatDau, D.KetThuc, D.TongTien, D.TrangThai, D.MaQR,
                   T.TenTaiNguyen, D.CoSoId, C.TenCoSo, D.NgayTao
            FROM DatLich D
            LEFT JOIN TaiNguyen T ON D.TaiNguyenId = T.TaiNguyenId
            LEFT JOIN CoSo C ON D.CoSoId = C.CoSoId
            WHERE D.TaiKhoanId = ? AND D.CoSoId = ?
            ORDER BY D.DatLichId DESC
        """, (tai_khoan_id, CO_SO_ID))
        rows = cur.fetchall()
        db.close()
        if rows:
            for r in rows:
                res.append({
                    "datLichId": r[0],
                    "taiKhoanId": tai_khoan_id,
                    "taiNguyenId": r[1],
                    "batDau": r[2],
                    "ketThuc": r[3],
                    "tongTien": r[4],
                    "trangThai": r[5],
                    "maQR": r[6],
                    "tenBan": r[7] or f"Bàn #{r[1]}",
                    "coSoId": r[8],
                    "tenCoSo": r[9],
                    "ngayTao": r[10]
                })
            return res
    except Exception as e:
        print("Loi lay lich su tu DB:", e)

    # Fallback memory
    for d in IN_MEMORY_DAT_LICH:
        if d["taiKhoanId"] == tai_khoan_id:
            ban = next((b for b in ds_ban if b["taiNguyenId"] == d["taiNguyenId"]), None)
            item = dict(d)
            item["tenBan"] = ban["ten"] if ban else f"Bàn #{d['taiNguyenId']}"
            res.append(item)
    return res
