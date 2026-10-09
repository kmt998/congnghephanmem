#!/bin/bash
set -e

# ==============================================================================
# database/init.sh
# Tự động khởi tạo cơ sở dữ liệu TrungTamTheThao trong Docker / Linux
# ==============================================================================

DB_SERVER="${DB_SERVER:-sqlserver}"
DB_USER="${DB_USER:-sa}"
DB_PASSWORD="${DB_PASSWORD:-SportChain@2026}"
DB_NAME="${DB_NAME:-TrungTamTheThao}"

echo "=========================================================="
echo "🚀 [db-init] BẮT ĐẦU TIẾN TRÌNH KHỞI TẠO CƠ SỞ DỮ LIỆU"
echo "   Server  : $DB_SERVER"
echo "   Database: $DB_NAME"
echo "   User    : $DB_USER"
echo "=========================================================="

# 1. Tìm đường dẫn sqlcmd trong container mssql
if [ -f "/opt/mssql-tools18/bin/sqlcmd" ]; then
    SQLCMD="/opt/mssql-tools18/bin/sqlcmd"
elif [ -f "/opt/mssql-tools/bin/sqlcmd" ]; then
    SQLCMD="/opt/mssql-tools/bin/sqlcmd"
elif command -v sqlcmd >/dev/null 2>&1; then
    SQLCMD="sqlcmd"
else
    echo "❌ [db-init] Không tìm thấy công cụ sqlcmd trong môi trường!"
    exit 1
fi

echo "ℹ️  [db-init] Sử dụng sqlcmd tại: $SQLCMD"

# Hàm thực thi lệnh sqlcmd tiện ích (tự động bật -C TrustServerCertificate và -f 65001 UTF-8)
run_sqlcmd() {
    "$SQLCMD" -S "$DB_SERVER" -U "$DB_USER" -P "$DB_PASSWORD" -C -f 65001 "$@"
}

# 2. Đợi SQL Server sẵn sàng tiếp nhận kết nối
echo "⏳ [db-init] Đang chờ SQL Server sẵn sàng tiếp nhận truy vấn..."
MAX_TRIES=30
COUNT=0
until run_sqlcmd -Q "SELECT 1" >/dev/null 2>&1; do
    COUNT=$((COUNT + 1))
    if [ $COUNT -ge $MAX_TRIES ]; then
        echo "❌ [db-init] Hết thời gian chờ kết nối SQL Server ($MAX_TRIES lần)."
        exit 1
    fi
    echo "   -> Đang thử lại ($COUNT/$MAX_TRIES)..."
    sleep 2
done

echo "✅ [db-init] Kết nối SQL Server thành công!"

# 3. Tạo Database nếu chưa tồn tại
echo "📦 [db-init] Kiểm tra và tạo database [$DB_NAME]..."
run_sqlcmd -Q "IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'$DB_NAME') BEGIN CREATE DATABASE [$DB_NAME]; PRINT N'Đã tạo mới database $DB_NAME'; END ELSE BEGIN PRINT N'Database $DB_NAME đã tồn tại'; END"

# 4. Chạy file schema_core.sql (Các bảng lõi)
if [ -f "/database/schema_core.sql" ]; then
    echo "🏗️  [db-init] Thực thi /database/schema_core.sql..."
    run_sqlcmd -d "$DB_NAME" -i "/database/schema_core.sql"
else
    echo "⚠️  [db-init] Không tìm thấy /database/schema_core.sql"
fi

# 5. Chạy file seed_core.sql (Dữ liệu mẫu 10 cơ sở + tài khoản test)
if [ -f "/database/seed_core.sql" ]; then
    echo "🌱 [db-init] Thực thi /database/seed_core.sql..."
    run_sqlcmd -d "$DB_NAME" -i "/database/seed_core.sql"
else
    echo "⚠️  [db-init] Không tìm thấy /database/seed_core.sql"
fi

# 6. Chạy tất cả các file riêng của từng cơ sở (/database/coso*.sql)
echo "🏢 [db-init] Chạy các file cấu hình riêng từng cơ sở (/database/coso*.sql)..."
for sql_file in /database/coso*.sql; do
    if [ -f "$sql_file" ]; then
        filename=$(basename "$sql_file")
        echo "   -> Thực thi: $filename"
        run_sqlcmd -d "$DB_NAME" -i "$sql_file" || {
            echo "   ⚠️ Cảnh báo: $filename có lỗi nhưng tiếp tục các file khác."
        }
    fi
done

echo "=========================================================="
echo "🎉 [db-init] HOÀN TẤT KHỞI TẠO TOÀN BỘ CƠ SỞ DỮ LIỆU!"
echo "   Hệ thống sẵn sàng cho ứng dụng Flask kết nối."
echo "=========================================================="
