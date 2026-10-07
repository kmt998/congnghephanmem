# 🏟️ Hệ Thống Quản Lý Trung Tâm Thể Thao Đa Năng (Chuỗi 10 Cơ Sở)

> Đồ án môn học Công Nghệ Phần Mềm — Phiên bản chuẩn Quy ước chung v1.0.

---

## 🛠️ Công Nghệ Chung
- **Backend:** Python Flask 3.x (Mỗi cơ sở thể thao là một Blueprint độc lập)
- **Database:** Microsoft SQL Server (1 database chung tên `TrungTamTheThao`)
- **Xác thực:** JWT Token (Dùng chung 1 trang đăng nhập `/auth/dang-nhap`)
- **Giao diện:** Dùng chung `core/templates/layout.html` và `core/static/css/main.css`, các cơ sở chỉ kế thừa layout.

---

## 📂 Cấu Trúc Repository Chuẩn

```text
webtong/
  app.py                         # File chạy chính của web tổng
core/
  auth.py                        # JWT, hash mật khẩu, decorator phân quyền
  auth_routes.py                 # Blueprint đăng nhập / đăng ký dùng chung
  db.py                          # Kết nối SQL Server
  registry.py                    # Khai báo & mount các cơ sở thể thao
  templates/
    layout.html                  # Layout base dùng chung toàn hệ thống
    trang_chu.html               # Trang chủ web tổng
    auth/                        # Giao diện đăng nhập / đăng ký
  static/
    css/main.css                 # CSS Design System dùng chung
    js/main.js                   # JavaScript dùng chung
modules/
  coso01_boiloi/
  coso02_gym/
  ...
  coso08_bongban/                # Cơ sở 08: Bóng Bàn (Đã hoàn thiện giao diện & nghiệp vụ)
    __init__.py                  # Hợp đồng module chuẩn 3 hàm lõi
    routes.py                    # Routes: /coso/8/..., /api/coso/8/...
    service.py                   # Tầng nghiệp vụ, mock data, tính giá
    templates/                   # Giao diện riêng kế thừa layout.html
    static/
  coso10_pickleball/
database/
  schema_core.sql                # 8 bảng lõi dùng chung (KHÔNG SỬA)
  coso01_boiloi.sql
  ...
  coso08_bongban.sql             # Bảng riêng & seed data cơ sở Bóng Bàn
requirements.txt                 # Thư viện cần thiết
run.py                           # Lệnh chạy nhanh web
```

---


## 🚀 Hướng Dẫn Cài Đặt & Chạy Thử

### 1. Cài đặt thư viện:
```bash
py -m pip install -r requirements.txt
```

### 2. Chạy ứng dụng web:
```bash
py run.py
```

- **Web tổng:** [http://localhost:5000](http://localhost:5000)
- **Cơ sở 08 (Bóng Bàn):** [http://localhost:5000/coso/8](http://localhost:5000/coso/8)
- **Đặt bàn bóng bàn:** [http://localhost:5000/coso/8/dat-lich](http://localhost:5000/coso/8/dat-lich)
- **Đăng nhập:** [http://localhost:5000/auth/dang-nhap](http://localhost:5000/auth/dang-nhap) (Tài khoản mẫu: `admin` / `admin123`)

---

## 🌿 Quy Trình Git & Làm Việc Nhóm

1. **Nhánh `main`:** Chỉ trưởng nhóm được phép merge.
2. **Nhánh riêng của bạn:** Tạo nhánh mới từ `main` trước khi code:
   ```bash
   git checkout -b feature/coso08-bongban
   ```
3. Mỗi ngày trước khi code:
   ```bash
   git pull origin main
   ```
4. Khi làm xong, commit và đẩy lên nhánh của mình, sau đó tạo **Pull Request** trên GitHub.
