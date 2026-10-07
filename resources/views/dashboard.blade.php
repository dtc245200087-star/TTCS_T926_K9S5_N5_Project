<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Điều hành thi công</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: #f3f4f6;
            color: #1f2937;
        }

        .app {
            display: flex;
            min-height: 100vh;
        }

        .sidebar {
            width: 250px;
            background: #111827;
            color: white;
            padding: 22px 16px;
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
        }

        .brand {
            padding: 8px 12px 24px;
            border-bottom: 1px solid #374151;
            margin-bottom: 18px;
        }

        .brand-title {
            font-size: 21px;
            font-weight: 800;
            letter-spacing: .5px;
        }

        .brand-subtitle {
            margin-top: 5px;
            font-size: 12px;
            color: #9ca3af;
        }

        .menu-title {
            padding: 8px 12px;
            color: #6b7280;
            font-size: 11px;
            text-transform: uppercase;
            font-weight: bold;
        }

        .menu {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .menu a {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 11px 12px;
            border-radius: 8px;
            color: #d1d5db;
            text-decoration: none;
            font-size: 14px;
            transition: .2s;
        }

        .menu a:hover,
        .menu a.active {
            background: #374151;
            color: white;
        }

        .menu-icon {
            width: 22px;
            text-align: center;
            font-size: 16px;
        }

        .sidebar-bottom {
            position: absolute;
            left: 16px;
            right: 16px;
            bottom: 18px;
        }

        .logout {
            width: 100%;
            border: none;
            background: #7f1d1d;
            color: #fecaca;
            padding: 11px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }

        .logout:hover {
            background: #991b1b;
        }

        .main {
            margin-left: 250px;
            width: calc(100% - 250px);
            min-height: 100vh;
        }

        .topbar {
            height: 70px;
            background: white;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
        }

        .page-title {
            font-size: 20px;
            font-weight: 700;
        }

        .page-subtitle {
            margin-top: 3px;
            color: #6b7280;
            font-size: 13px;
        }

        .user-box {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .avatar {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: #374151;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        .user-name {
            font-size: 14px;
            font-weight: bold;
        }

        .user-role {
            font-size: 12px;
            color: #6b7280;
            margin-top: 2px;
        }

        .content {
            padding: 28px 30px;
        }

        .welcome {
            background: linear-gradient(135deg, #1f2937, #374151);
            color: white;
            border-radius: 14px;
            padding: 25px 28px;
            margin-bottom: 24px;
        }

        .welcome h1 {
            margin: 0 0 8px;
            font-size: 25px;
        }

        .welcome p {
            margin: 0;
            color: #d1d5db;
            font-size: 14px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-bottom: 24px;
        }

        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e5e7eb;
        }

        .stat-label {
            color: #6b7280;
            font-size: 13px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 8px;
        }

        .stat-note {
            margin-top: 6px;
            font-size: 12px;
            color: #6b7280;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }

        .card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }

        .card-title {
            font-size: 17px;
            font-weight: 700;
        }

        .view-all {
            color: #2563eb;
            text-decoration: none;
            font-size: 13px;
        }

        .project-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .project-name {
            font-weight: 700;
        }

        .project-percent {
            font-weight: 700;
        }

        .progress {
            width: 100%;
            height: 9px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 64%;
            background: #2563eb;
            border-radius: 10px;
        }

        .project-meta {
            display: flex;
            justify-content: space-between;
            margin-top: 9px;
            color: #6b7280;
            font-size: 12px;
        }

        .task-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 13px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .task-row:last-child {
            border-bottom: none;
        }

        .task-name {
            font-size: 14px;
            font-weight: 600;
        }

        .task-meta {
            margin-top: 4px;
            color: #6b7280;
            font-size: 12px;
        }

        .status {
            padding: 5px 9px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
        }

        .status-doing {
            background: #dbeafe;
            color: #1d4ed8;
        }

        .status-done {
            background: #dcfce7;
            color: #15803d;
        }

        .status-warning {
            background: #fef3c7;
            color: #b45309;
        }

        .alert {
            display: flex;
            gap: 12px;
            padding: 13px;
            border-radius: 8px;
            margin-bottom: 10px;
            background: #f9fafb;
        }

        .alert-icon {
            font-size: 18px;
        }

        .alert-title {
            font-size: 13px;
            font-weight: bold;
        }

        .alert-text {
            font-size: 12px;
            color: #6b7280;
            margin-top: 3px;
        }

        .quick-actions {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .quick-action {
            padding: 14px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            text-decoration: none;
            color: #1f2937;
            background: #fafafa;
            font-size: 13px;
            font-weight: 600;
        }

        .quick-action:hover {
            background: #f3f4f6;
        }

        @media (max-width: 1000px) {
            .stats {
                grid-template-columns: repeat(2, 1fr);
            }

            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 700px) {
            .sidebar {
                width: 210px;
            }

            .main {
                margin-left: 210px;
                width: calc(100% - 210px);
            }

            .content {
                padding: 20px;
            }

            .stats {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>

<div class="app">

    <aside class="sidebar">

        <div class="brand">
            <div class="brand-title">🏗 SITEPRO BUILD</div>
            <div class="brand-subtitle">Nền tảng điều hành thi công</div>
        </div>

        <div class="menu-title">Điều hành</div>

        <nav class="menu">

            <a href="/" class="active">
                <span class="menu-icon">📊</span>
                <span>Tổng quan</span>
            </a>

            <a href="/projects">
                <span class="menu-icon">🏢</span>
                <span>Dự án</span>
            </a>

            <a href="/work-items">
                <span class="menu-icon">📋</span>
                <span>Công việc</span>
            </a>

            <a href="/work-items/tree">
                <span class="menu-icon">🌳</span>
                <span>Cây hạng mục</span>
            </a>

            <a href="/materials">
                <span class="menu-icon">📦</span>
                <span>Vật tư</span>
            </a>

            <a href="/personnel">
                <span class="menu-icon">👷</span>
                <span>Nhân sự</span>
            </a>

            <a href="/safety">
                <span class="menu-icon">⚠️</span>
                <span>An toàn</span>
            </a>

            <a href="/diaries">
                <span class="menu-icon">📖</span>
                <span>Nhật ký</span>
            </a>

        </nav>

        <div class="sidebar-bottom">

            <div class="menu">
                <a href="#">
                    <span class="menu-icon">👤</span>
                    <span>Tài khoản</span>
                </a>
            </div>

            <form action="/logout" method="POST">
                @csrf
                <button type="submit" class="logout">
                    🚪 Đăng xuất
                </button>
            </form>

        </div>

    </aside>

    <main class="main">

        <header class="topbar">

            <div>
                <div class="page-title">Tổng quan điều hành</div>
                <div class="page-subtitle">
                    Theo dõi tiến độ và tình trạng công trình
                </div>
            </div>

            <div class="user-box">
                <div class="avatar">
                    {{ strtoupper(substr(auth()->user()->name ?? 'U', 0, 1)) }}
                </div>

                <div>
                    <div class="user-name">
                        {{ auth()->user()->name ?? 'Người dùng' }}
                    </div>

                    <div class="user-role">
                        Người dùng hệ thống
                    </div>
                </div>
            </div>

        </header>

        <section class="content">

            <div class="welcome">
                <h1>Chào mừng trở lại 👋</h1>
                <p>
                    Đây là trung tâm điều hành dự án và theo dõi hoạt động thi công.
                </p>
            </div>

            <div class="stats">

                <div class="stat-card">
                    <div class="stat-label">Dự án đang thực hiện</div>
                    <div class="stat-value">01</div>
                    <div class="stat-note">Dự án hiện tại</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Tổng công việc</div>
                    <div class="stat-value">24</div>
                    <div class="stat-note">Trong dự án</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Đã hoàn thành</div>
                    <div class="stat-value">15</div>
                    <div class="stat-note">62.5% tổng công việc</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Cần xử lý</div>
                    <div class="stat-value">03</div>
                    <div class="stat-note">Công việc cần chú ý</div>
                </div>

            </div>

            <div class="dashboard-grid">

                <div>

                    <div class="card">

                        <div class="card-header">
                            <div class="card-title">Tiến độ dự án</div>
                            <a href="/work-items" class="view-all">Chi tiết →</a>
                        </div>

                        <div class="project-info">
                            <span class="project-name">
                                Công trình xây dựng mẫu
                            </span>

                            <span class="project-percent">
                                64%
                            </span>
                        </div>

                        <div class="progress">
                            <div class="progress-bar"></div>
                        </div>

                        <div class="project-meta">
                            <span>Đã thực hiện: 15/24 công việc</span>
                            <span>Đang triển khai</span>
                        </div>

                    </div>

                    <br>

                    <div class="card">

                        <div class="card-header">
                            <div class="card-title">Công việc gần đây</div>
                            <a href="/work-items" class="view-all">Xem tất cả →</a>
                        </div>

                        <div class="task-row">
                            <div>
                                <div class="task-name">
                                    Chuẩn bị mặt bằng
                                </div>
                                <div class="task-meta">
                                    Hạng mục móng · 5 ngày
                                </div>
                            </div>

                            <span class="status status-done">
                                Hoàn thành
                            </span>
                        </div>

                        <div class="task-row">
                            <div>
                                <div class="task-name">
                                    Thi công móng
                                </div>
                                <div class="task-meta">
                                    Hạng mục kết cấu · 12 ngày
                                </div>
                            </div>

                            <span class="status status-doing">
                                Đang làm
                            </span>
                        </div>

                        <div class="task-row">
                            <div>
                                <div class="task-name">
                                    Lắp đặt hệ thống điện
                                </div>
                                <div class="task-meta">
                                    Hạng mục MEP · 8 ngày
                                </div>
                            </div>

                            <span class="status status-warning">
                                Chờ xử lý
                            </span>
                        </div>

                    </div>

                </div>

                <div>

                    <div class="card">

                        <div class="card-header">
                            <div class="card-title">Cảnh báo</div>
                        </div>

                        <div class="alert">
                            <div class="alert-icon">⚠️</div>
                            <div>
                                <div class="alert-title">
                                    Công việc sắp trễ hạn
                                </div>
                                <div class="alert-text">
                                    3 công việc cần được kiểm tra.
                                </div>
                            </div>
                        </div>

                        <div class="alert">
                            <div class="alert-icon">📅</div>
                            <div>
                                <div class="alert-title">
                                    Lịch thi công
                                </div>
                                <div class="alert-text">
                                    Có công việc cần thực hiện hôm nay.
                                </div>
                            </div>
                        </div>

                        <div class="alert">
                            <div class="alert-icon">🦺</div>
                            <div>
                                <div class="alert-title">
                                    An toàn công trường
                                </div>
                                <div class="alert-text">
                                    Chưa có cảnh báo mới.
                                </div>
                            </div>
                        </div>

                    </div>

                    <br>

                    <div class="card">

                        <div class="card-header">
                            <div class="card-title">Thao tác nhanh</div>
                        </div>

                        <div class="quick-actions">

                            <a href="/work-items" class="quick-action">
                                📋 Quản lý công việc
                            </a>

                            <a href="/work-items/tree" class="quick-action">
                                🌳 Cây hạng mục
                            </a>

                            <a href="#" class="quick-action">
                                📦 Vật tư
                            </a>

                            <a href="#" class="quick-action">
                                📖 Nhật ký
                            </a>

                        </div>

                    </div>

                </div>

            </div>

        </section>

    </main>

</div>

</body>
</html>

