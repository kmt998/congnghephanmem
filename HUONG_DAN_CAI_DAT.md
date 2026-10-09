# 🚀 HƯỚNG DẪN KHỞI CHẠY DỰ ÁN DÀNH CHO THÀNH VIÊN NHÓM

Tài liệu này giúp các thành viên trong nhóm 10 người clone repo từ GitHub về máy cá nhân và dựng toàn bộ hệ thống (Web Flask + Database SQL Server 2022) một cách nhanh chóng, không bị lỗi thiếu cơ sở dữ liệu hay lỗi đăng nhập.

---

## ⚡ CÁCH 1: DÙNG DOCKER COMPOSE (KHUYÊN DÙNG — NHANH NHẤT)

Nếu máy bạn đã cài sẵn **Docker Desktop**:

### Bước 1: Clone repo và mở terminal tại thư mục dự án
```bash
git clone <URL_REPO_CUA_NHOM>
cd congnghephanmem
```

### Bước 2: Tạo file `.env` từ file mẫu `.env.example`
- **Trên Windows (cmd / PowerShell):**
  ```powershell
  copy .env.example .env
  ```
- **Trên macOS / Linux / Git Bash:**
  ```bash
  cp .env.example .env
  ```

*(File `.env` mặc định đã điền sẵn cấu hình kết nối SQL Server Docker: `DB_SERVER=localhost,1433`, tài khoản `sa`, mật khẩu `SportChain@2026`).*

### Bước 3: Khởi động SQL Server và tự động tạo Database
Chạy một lệnh duy nhất:
```bash
docker compose up -d
```
*(Hoặc `docker-compose up -d` nếu bạn dùng phiên bản docker compose cũ)*

> 💡 **Hệ thống tự động làm gì?**
> - Kéo image **SQL Server 2022** chính thức của Microsoft và bật cổng `1433`.
> - Chờ SQL Server sẵn sàng (`healthy`).
> - Service `db-init` tự động chạy script `database/init.sh` để:
>   1. Tạo Database `TrungTamTheThao` (nếu chưa có).
>   2. Chạy `database/schema_core.sql` để tạo 8 bảng lõi (`CoSo`, `TaiKhoan`, `GoiHoiVien`, `TheHoiVien`, `TaiNguyen`, `DatLich`, `HoaDon`, `DanhGia`).
>   3. Chạy `database/seed_core.sql` để nạp dữ liệu mẫu 10 cơ sở thể thao và tài khoản test.
>   4. Chạy toàn bộ các file `database/coso*.sql` của các thành viên.

Bạn có thể kiểm tra tiến trình khởi tạo DB bằng lệnh:
```bash
docker compose logs -f db-init
```
Khi thấy dòng `===> KHOI TAO DATABASE HOAN TAT THANH CONG! <===` là DB đã sẵn sàng!

### Bước 4: Cài đặt thư viện Python
Tạo môi trường ảo (khuyến khích) và cài các gói cần thiết:
```bash
# Tạo môi trường ảo (tùy chọn)
python -m venv venv
# Kích hoạt trên Windows:
venv\Scripts\activate
# Hoặc trên Linux/macOS:
# source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### Bước 5: Chạy ứng dụng Flask
```bash
python run.py
```
Mở trình duyệt truy cập: **[http://localhost:5000](http://localhost:5000)**

---

## 🛠️ CÁCH 2: CHẠY THỦ CÔNG (NẾU MÁY KHÔNG CÓ DOCKER)

Nếu máy bạn đã cài sẵn **SQL Server cục bộ** (SQL Server Express, Developer) và **SSMS (SQL Server Management Studio)**:

### Bước 1: Chạy các file SQL trong thư mục `database/`
Mở **SSMS**, kết nối vào SQL Server của bạn và thực hiện lần lượt:
1. Mở file `database/schema_core.sql` ➜ Nhấn **Execute** (F5).  
   *(File sẽ tự tạo Database `TrungTamTheThao` và 8 bảng lõi nếu chưa có).*
2. Mở file `database/seed_core.sql` ➜ Nhấn **Execute** (F5).  
   *(File sẽ chèn 10 cơ sở mẫu và tài khoản test).*
3. Mở các file `database/coso*.sql` (nếu có môn thể thao riêng của bạn) ➜ Nhấn **Execute** (F5).

### Bước 2: Cấu hình file `.env`
Tạo file `.env` (bằng cách copy từ `.env.example`), mở file `.env` bằng VS Code / Notepad và sửa cấu hình kết nối trỏ về SQL Server máy bạn:
```env
# Nếu dùng Windows Authentication (không cần user/password):
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=TrungTamTheThao
DB_USER=
DB_PASSWORD=
DB_DRIVER=ODBC Driver 17 for SQL Server

JWT_SECRET=sportchain-jwt-secret-2026-trungtamthethao
SECRET_KEY=sportchain-secret-key-2026-nhom-cnpm
```

### Bước 3: Cài đặt thư viện và chạy Web
```bash
pip install -r requirements.txt
python run.py
```

---

## 👥 DANH SÁCH TÀI KHOẢN DÙNG THỬ (TEST CREDENTIALS)

Dữ liệu đã được nạp sẵn các tài khoản sau để bạn test chức năng phân quyền:

| Phân loại | Tên đăng nhập | Mật khẩu | Phạm vi quyền hạn | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Quản trị tối cao toàn chuỗi 10 cơ sở | Xem/quản lý toàn bộ hệ thống |
| **Quản lý CS 1** | `quanly01` | `123456` | Quản lý Cơ sở 1  | Chỉ quản lý CS 1 |
| **Quản lý CS 2** | `quanly02` | `123456` | Quản lý Cơ sở 2  | Chỉ quản lý CS 2 |
| **Quản lý CS 3** | `quanly03` | `123456` | Quản lý Cơ sở 3  | Chỉ quản lý CS 3 |
| **Quản lý CS 4** | `quanly04` | `123456` | Quản lý Cơ sở 4  | Chỉ quản lý CS 4 |
| **Quản lý CS 5** | `quanly05` | `123456` | Quản lý Cơ sở 5  | Chỉ quản lý CS 5 |
| **Quản lý CS 6** | `quanly06` | `123456` | Quản lý Cơ sở 6  | Chỉ quản lý CS 6 |
| **Quản lý CS 7** | `quanly07` | `123456` | Quản lý Cơ sở 7  | Chỉ quản lý CS 7 |
| **Quản lý CS 8** | `quanly08` | `123456` | Quản lý Cơ sở 8  | Chỉ quản lý CS 8 |
| **Quản lý CS 9** | `quanly09` | `123456` | Quản lý Cơ sở 9  | Chỉ quản lý CS 9 |
| **Quản lý CS 10** | `quanly10` | `123456` | Quản lý Cơ sở 10  | Chỉ quản lý CS 10 |
| **Hội viên** | `hoivien01` | `123456` | Khách hàng thành viên | Đặt lịch, mua gói tập, xem hóa đơn |

---

## 📌 QUY ƯỚC QUAN TRỌNG KHI CODE MODULE CỦA BẠN

1. **Thư mục module của bạn:** Làm việc trong `modules/cosoXX_tenmon/`.
2. **File SQL riêng:** Đặt file tạo bảng hoặc seed dữ liệu riêng của cơ sở bạn vào `database/cosoXX_tenmon.sql`. Khi ai đó chạy `docker compose up -d` hoặc chạy lại `database/init.sh`, file của bạn sẽ tự động được chạy cùng hệ thống.
3. **Tuyệt đối không sửa:** Các file lõi trong `core/` (như `core/db.py`, `core/auth.py`) và `webtong/app.py` để tránh xung đột git.
4. **Không commit file `.env` lên GitHub:** File `.env` chứa mật khẩu cá nhân, đã được ghi trong `.gitignore`. Chỉ commit các file code và `.env.example`.
