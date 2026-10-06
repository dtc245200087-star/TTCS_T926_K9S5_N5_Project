# Nền tảng điều hành thi công công trình

Dự án mẫu gồm:
- Backend: Python Flask + SQLAlchemy
- Frontend: React + Vite
- Database: PostgreSQL
- Docker Compose

## 1. Cách chạy nhanh bằng Docker

Yêu cầu:
- Docker Desktop đã cài và đang chạy.
- Visual Studio Code (khuyến nghị).

Mở Terminal tại thư mục `DieuHanhThiCong`:

```bash
docker compose up --build
```

Sau khi chạy xong:

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000/api/health
- PostgreSQL: localhost:5432

Để dừng:

```bash
docker compose down
```

Muốn xóa luôn dữ liệu database:

```bash
docker compose down -v
```

## 2. Cấu trúc

```text
backend/
  app/
    models/
    routes/
    services/
  migrations/
  requirements.txt
  run.py

frontend/
  src/
  public/
  package.json

database/
  init/

docs/
docker-compose.yml
.env
.env.example
.gitignore
README.md
```

## 3. API chính

GET `/api/health`

GET `/api/dashboard`

GET `/api/cong-trinh`

POST `/api/cong-trinh`

PUT `/api/cong-trinh/<id>`

DELETE `/api/cong-trinh/<id>`

GET `/api/cong-viec`

POST `/api/cong-viec`

## 4. Chạy không dùng Docker

### Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

Cần PostgreSQL đang chạy và đặt biến `DATABASE_URL`.

Chạy:

```bash
python run.py
```

### Frontend

Mở terminal khác:

```bash
cd frontend
npm install
npm run dev
```

Truy cập:

http://localhost:5173

## 5. Gợi ý mở rộng đồ án

Có thể phát triển tiếp:
- Đăng nhập và phân quyền Admin / Chỉ huy trưởng / Kỹ sư / Công nhân.
- Quản lý vật tư.
- Quản lý thiết bị máy móc.
- Nhật ký thi công.
- Quản lý hồ sơ, bản vẽ.
- Cảnh báo công việc trễ hạn.
- Biểu đồ Gantt.
- Báo cáo PDF/Excel.
- Thông báo realtime.
- Upload hình ảnh hiện trường.
