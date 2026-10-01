# TTCS_T926_K9S5_N5_Project
Nền tảng điều hành thi công công trình - TTCS Khối 9 Nhóm 5

## Issue #15 — bảo vệ cây hạng mục

- `PATCH /api/v1/projects/{project}/work-items/{workItem}`: body JSON `{"parent_id": ...}`; dùng `null` để chuyển thành hạng mục gốc. Trả 422 nếu cha là chính hạng mục, hậu duệ, không tồn tại hoặc thuộc dự án khác.
- `DELETE /api/v1/projects/{project}/work-items/{workItem}`: trả 409 nếu đã có công việc hoặc còn hạng mục con; xoá hạng mục lá trống trả 204.
- Thông báo nghiệp vụ dùng tên hạng mục. Yêu cầu bị từ chối không thay đổi dữ liệu.
- Kiểm tra tổ tiên dùng CTE đệ quy có tham số; transaction khoá dự án trước khi đổi cây để tránh hai thao tác đổi cha đồng thời tạo vòng lặp. Mọi chức năng thay đổi cây bổ sung sau này cần dùng cùng quy ước khoá dự án. Khoá ngoại không cho xoá dây chuyền công việc.

### Phạm vi tích hợp

Nhánh `main` tại thời điểm triển khai chưa có T-08/T-09: bổ sung migration tối thiểu cho `projects`, `work_items`, `tasks` cùng model/factory để API hoạt động. Không triển khai màn hình cây của #14. Bảng `jobs` hiện hữu là hàng đợi Laravel, không phải công việc thi công.

API dùng HTTP Basic với tài khoản người dùng. Quyền truy cập dự án đi qua bảng `project_members`; các route sửa cây hiện cho phép vai trò `admin`, `project_manager` và `team_lead`. Middleware từ chối `403` nếu người dùng không thuộc dự án, vai trò không được phép hoặc route chưa khai vai trò. HTTP Basic phải dùng HTTPS ngoài máy phát triển.

Laravel Boost được cài theo chỉ dẫn bootstrap ban đầu của `AGENTS.md`; chỉ là dependency phát triển.

### Chạy và kiểm tra

Cần PHP 8.4+ (theo composer.lock), Composer và Node.js tương thích Vite 8.

```sh
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate
npm install --ignore-scripts
npm run build
php artisan test
php vendor/bin/pint --dirty --format agent
```

PowerShell dùng `Copy-Item .env.example .env` thay cho `cp` nếu cần. SQLite là cấu hình mặc định; dùng database riêng khi thử dữ liệu mẫu. Test tự động dùng SQLite in-memory. Migration mới đã được kiểm tra tiến/lùi; PostgreSQL và tình huống cạnh tranh thực tế cần kiểm tra thêm trên môi trường triển khai.

### Thử bằng curl

Chỉ trên môi trường local/testing và database thử nghiệm:

```sh
php artisan db:seed --class=WorkItemDemoSeeder
php artisan serve
```

Seeder in ra email, mật khẩu và các ID của dữ liệu mẫu. Thay các giá trị trong dấu `<...>` bên dưới bằng kết quả đó. Dùng `curl.exe` trên PowerShell để tránh alias:

```sh
curl -i -u "<email>:password" -X PATCH -H "Content-Type: application/json" -H "Accept: application/json" -d '{"parent_id":<leaf>}' "http://127.0.0.1:8000/api/v1/projects/<project>/work-items/<root>"
curl -i -u "<email>:password" -X DELETE -H "Accept: application/json" "http://127.0.0.1:8000/api/v1/projects/<project>/work-items/<child>"
```

Lệnh đầu trả 422 kèm tên «Phần móng» và «Lắp dựng»; lệnh sau trả 409 kèm tên «Cốt thép». Seeder chỉ chạy khi được gọi rõ ràng, không được nối vào `DatabaseSeeder` và không chạy trên production.
