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
4. Mở `http://localhost:5174` và đăng nhập bằng tên trong `INITIAL_ADMIN_USERNAME` cùng mật khẩu vừa đặt.

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

Trong mục **Công việc**, quản trị viên, quản lý công trình và kỹ sư có thể mở form bằng nút **Cập nhật**. Mục **Tiến độ và đường găng** dùng cùng dữ liệu `GET /api/cong-viec`; chọn thanh của một công việc trong cơ sở dữ liệu sẽ mở cùng form cập nhật. Tiến độ thực tế được tô màu trên thanh Gantt. Dữ liệu kế hoạch của biểu đồ (ES, EF, LS, LF, độ trễ và trạng thái đường găng) được lưu cùng công việc và không bị thay đổi khi cập nhật tiến độ thực tế. Công việc không có bản ghi tương ứng không thể sửa. Ngày kết thúc không được trước ngày bắt đầu; máy chủ và SQLite cùng kiểm tra các ràng buộc này.

- `PATCH /api/cong-viec/<id>` — cập nhật `ngay_bat_dau_thuc_te`, `ngay_ket_thuc_thuc_te` (ngày `YYYY-MM-DD` hoặc `null`) và `phan_tram_hoan_thanh` (số nguyên 0–100). Chỉ vai trò `admin`, `manager`, `engineer` được cập nhật.
- `GET /api/cong-viec` — trả các trường tiến độ thực tế và kế hoạch Gantt để cả hai mục dùng chung dữ liệu.

Các cột tiến độ thực tế và kế hoạch Gantt còn thiếu được tự động thêm vào cơ sở dữ liệu hiện có khi backend khởi động.

## Ảnh hiện trường trong nhật ký thi công

Khi tạo mục nhật ký, có thể chọn hoặc kéo thả tối đa 10 ảnh. Trình duyệt nén ảnh sang JPEG dưới 1 MB và tạo thumbnail riêng trước khi gửi từng ảnh lên API. Nhật ký được lưu độc lập trước ảnh, vì vậy lỗi mạng khi tải ảnh không làm mất nội dung; từng ảnh lỗi có thể tải lại mà không tạo bản trùng. Thumbnail được tải lười, và ảnh đầy đủ chỉ được lấy khi mở ảnh. Ảnh được lưu trong thư mục `diary_images` cạnh cơ sở dữ liệu người dùng; Docker Compose lưu thư mục này cùng volume `backend_data`.

## Projects và cây work items

Khi backend khởi động, migration phiên bản 1 tạo hai bảng `projects` và `work_items`. `work_items.project_id` tham chiếu project; `work_items.parent_id` tạo quan hệ cha-con trong cùng project. Cơ sở dữ liệu kiểm tra khóa ngoại, ngăn chu trình cha-con và có chỉ mục trên `parent_id`. Model `app.models.project_work_items.get_work_item_tree()` dùng CTE đệ quy và trả về cây lồng nhau gồm hạng mục được yêu cầu cùng tất cả cấp con.

Các bảng này được bổ sung độc lập để không làm thay đổi hoặc sao chép dữ liệu đang được các luồng hiện hữu sử dụng trong `cong_viec`, `categories` và danh sách công trình cũ. Chúng không tự đồng bộ với các bảng/luồng legacy.
Có thể hoàn tác migration bằng `app.migrations.downgrade_database(database_path, target_version=0)`. Lưu ý: hoàn tác phiên bản 1 sẽ xóa các bảng `work_items` và `projects` cùng dữ liệu của chúng; các bảng legacy không bị xóa.

## Benchmark S-13 (T-29)

Trên Windows 11 với Chrome, biểu đồ SVG hiển thị 500 thanh trong **0,101 giây**. Khi cuộn ngang, FPS đo được là **22,8 FPS ở giữa biểu đồ** và **1,2 FPS ở đoạn cuối danh sách**, cho thấy cuộn chưa mượt ở quy mô 500 công việc dù thời gian render ban đầu nhanh. Đây là trường hợp cực đoan; với khoảng 20–50 công việc dự kiến trong dự án, tiếp tục giữ SVG. Tối ưu bằng Canvas hoặc virtualize có thể xem xét trong task mở rộng sau.

## Hạng mục và mốc bàn giao

Mục **Hạng mục** cho phép quản trị viên và quản lý công trình tạo cây hạng mục, gán công việc, và khai báo chuỗi phụ thuộc giữa các công việc. Người có quyền cập nhật tiến độ cũng có thể chọn hạng mục trong form **Cập nhật tiến độ thực tế**; lựa chọn này được lưu vào `cong_viec.category_id`. Khi chuyển công việc sang hạng mục khác, các liên kết phụ thuộc cũ của công việc đó được xóa để tránh giữ lại chuỗi không còn cùng hạng mục.

Đặt ngày bắt đầu kế hoạch cho mỗi hạng mục. Các giá trị `ES`/`EF` hiện được lưu theo số ngày tính từ mốc bắt đầu này; ngày kết thúc sớm dự kiến được tính bằng ngày bắt đầu cộng `EF`. Mục **Mốc bàn giao** hiển thị cảnh báo khi ngày này sau hạn bàn giao, cùng chuỗi phụ thuộc gây chậm. Chi tiết cảnh báo chỉ trả về tên công việc, không trả mã công việc.

Chỉ vai trò `admin` và `manager` được tạo, sửa hoặc xóa hạng mục, quan hệ công việc và mốc bàn giao. Các tài khoản đã đăng nhập khác có thể xem cây, mốc và cảnh báo. Cơ sở dữ liệu hiện có tự động được bổ sung cột `category_id` cùng các bảng `categories`, `category_tasks`, `task_dependencies` và `milestones` khi backend khởi động.

Khi tạo quan hệ phụ thuộc, hệ thống kiểm tra chu trình trên đồ thị tạm có thêm quan hệ mới. Quan hệ tạo vòng không được lưu; API trả mã `422` cùng thông báo mô tả chuỗi công việc bằng tên.

## S-06 — Khai báo quan hệ phụ thuộc

Chọn **Quan hệ phụ thuộc (S-06)** ở thanh điều hướng để xem mockup mô tả các yêu cầu của màn hình khai báo quan hệ công việc. Đây là giao diện mô phỏng; phần quản lý dữ liệu phụ thuộc cần được triển khai riêng.

### Sắp xếp công việc và phát hiện vòng phụ thuộc (S-07)

Mục **Tiến độ và đường găng** tải các quan hệ phụ thuộc theo từng hạng mục và sắp xếp công việc bằng thuật toán topo không đệ quy. Bảng quan hệ liệt kê cả công việc tiên quyết và công việc kế tiếp. Nếu dữ liệu có chu trình, giao diện đánh dấu riêng công việc thuộc vòng và công việc bị vòng chặn; các công việc này không được đánh số thứ tự thực hiện.

## Bảng kết quả tiến độ

Mục **Tiến độ và đường găng** gọi `GET /api/schedule-results` một lần để lấy danh sách công việc cùng các kết quả ES, EF, LS, LF, độ trễ và trạng thái công việc găng. Kết quả được lưu trong bảng SQLite `schedule_results`; các thay đổi kế hoạch công việc hoặc quan hệ phụ thuộc đánh dấu kết quả cần tính lại. Bảng cho phép lọc công việc găng và sắp xếp theo thời điểm bắt đầu sớm nhất. Nếu quan hệ phụ thuộc tạo thành vòng, API trả `has_cycle: true` cùng thông báo thay vì cung cấp kết quả tính không hợp lệ.
