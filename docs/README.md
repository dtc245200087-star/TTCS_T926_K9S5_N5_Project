# Điều hành thi công: đăng nhập và phân quyền

Ứng dụng gồm API Flask, giao diện React/Vite và SQLite lưu tài khoản. Các API nghiệp vụ yêu cầu đăng nhập. Máy chủ đọc lại tài khoản và vai trò từ SQLite trên mỗi yêu cầu, nên khi quản trị viên khóa tài khoản hoặc đổi vai trò thì quyền mới áp dụng ngay.

## Vai trò

| Vai trò | Xem dữ liệu | Tạo công trình | Ghi nhật ký | Quản lý tài khoản |
| --- | --- | --- | --- | --- |
| `admin` — Quản trị viên | Có | Có | Có | Có |
| `manager` — Quản lý công trình | Có | Có | Có | Không |
| `engineer` — Kỹ sư | Có | Không | Có | Không |
| `viewer` — Chỉ xem | Có | Không | Không | Không |

## Chạy bằng Docker Compose

1. Tại thư mục dự án, sao chép `.env.example` thành `.env`.
2. Đổi `SECRET_KEY` thành giá trị ngẫu nhiên riêng và đặt `INITIAL_ADMIN_PASSWORD` thành mật khẩu quản trị mạnh, tối thiểu 12 ký tự.
3. Chạy `docker compose up --build`.
4. Mở `http://localhost:5173` và đăng nhập bằng tên trong `INITIAL_ADMIN_USERNAME` cùng mật khẩu vừa đặt.

SQLite nằm trong volume `backend_data`, nên tài khoản không mất khi dựng lại container. Biến `INITIAL_ADMIN_PASSWORD` chỉ dùng khi cơ sở dữ liệu chưa có tài khoản; đổi biến này sau đó không đổi mật khẩu đã lưu. Hãy dùng HTTPS và đặt `COOKIE_SECURE=true` khi triển khai qua HTTPS.

## Chạy trực tiếp trên Windows PowerShell

Mở hai cửa sổ PowerShell tại thư mục dự án. Trong cửa sổ API, đặt thông tin khởi tạo trước khi chạy backend:

```powershell
$bytes = New-Object byte[] 48
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$env:SECRET_KEY = [Convert]::ToBase64String($bytes)
$env:INITIAL_ADMIN_USERNAME = 'admin'
$env:INITIAL_ADMIN_PASSWORD = Read-Host 'Nhập mật khẩu quản trị (ít nhất 12 ký tự)'
Set-Location .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Trong cửa sổ thứ hai:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Mở `http://localhost:5173`. Cơ sở dữ liệu tài khoản cục bộ được tạo tại `backend/instance/users.db`.

## API xác thực và quản trị

- `GET /api/auth/csrf` — lấy token CSRF trước khi đăng nhập.
- `POST /api/auth/login` — đăng nhập bằng `username` và `password`.
- `GET /api/auth/me` — tài khoản hiện tại và token CSRF.
- `POST /api/auth/logout` — đăng xuất.
- `POST /api/auth/change-password` — đổi mật khẩu; mật khẩu mới tối thiểu 12 ký tự.
- `GET /api/auth/users`, `POST /api/auth/users`, `PATCH /api/auth/users/<id>` — chỉ quản trị viên.

API trả `401` nếu chưa đăng nhập, `403` nếu tài khoản không đủ quyền và yêu cầu `X-CSRF-Token` trên mọi yêu cầu thay đổi dữ liệu. Cookie phiên là HttpOnly, SameSite=Lax; mật khẩu được băm trước khi ghi SQLite. Quản trị viên cuối cùng không thể bị khóa/hạ quyền, và người dùng không thể tự khóa hoặc tự hạ quyền.

## Cập nhật tiến độ thực tế

Trong mục **Công việc**, quản trị viên, quản lý công trình và kỹ sư có thể cập nhật ngày bắt đầu thực tế, ngày kết thúc thực tế và phần trăm hoàn thành (0–100). Các giá trị thực tế được lưu riêng, không ghi đè trạng thái hay hạn kế hoạch. Ngày kết thúc không được trước ngày bắt đầu; máy chủ và SQLite cùng kiểm tra các ràng buộc này.

- `PATCH /api/cong-viec/<id>` — cập nhật `ngay_bat_dau_thuc_te`, `ngay_ket_thuc_thuc_te` (ngày `YYYY-MM-DD` hoặc `null`) và `phan_tram_hoan_thanh` (số nguyên 0–100). Chỉ vai trò `admin`, `manager`, `engineer` được cập nhật.
- `GET /api/cong-viec` — trả thêm các trường tiến độ thực tế để hiển thị trong bảng.

Các cột tiến độ thực tế được tự động thêm vào cơ sở dữ liệu hiện có khi backend khởi động.
