<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>An toàn công trường - SITEPRO BUILD</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, Helvetica, sans-serif;
            background: #f4f6f8;
            color: #1f2937;
        }

        .layout {
            display: flex;
            min-height: 100vh;
        }

        /* SIDEBAR */
        .sidebar {
            width: 250px;
            background: #111827;
            color: white;
            padding: 24px 16px;
        }

        .logo {
            font-size: 21px;
            font-weight: bold;
            margin-bottom: 35px;
            padding-left: 10px;
        }

        .menu-title {
            font-size: 12px;
            color: #9ca3af;
            margin: 20px 10px 10px;
            text-transform: uppercase;
        }

        .menu a {
            display: block;
            color: #d1d5db;
            text-decoration: none;
            padding: 12px 14px;
            border-radius: 8px;
            margin-bottom: 5px;
            font-size: 14px;
        }

        .menu a:hover {
            background: #1f2937;
            color: white;
        }

        .menu a.active {
            background: #f59e0b;
            color: #111827;
            font-weight: bold;
        }

        /* MAIN */
        .main {
            flex: 1;
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

        .topbar h2 {
            font-size: 21px;
        }

        .user {
            color: #4b5563;
            font-size: 14px;
        }

        .content {
            padding: 30px;
        }

        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        .page-header h1 {
            font-size: 27px;
            margin-bottom: 7px;
        }

        .page-header p {
            color: #6b7280;
            font-size: 14px;
        }

        .btn {
            border: none;
            background: #f59e0b;
            color: #111827;
            padding: 11px 17px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }

        .btn:hover {
            background: #d97706;
            color: white;
        }

        /* STATS */
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e5e7eb;
        }

        .stat-title {
            color: #6b7280;
            font-size: 13px;
            margin-bottom: 10px;
        }

        .stat-number {
            font-size: 29px;
            font-weight: bold;
        }

        .stat-note {
            margin-top: 7px;
            font-size: 12px;
            color: #6b7280;
        }

        /* CONTENT GRID */
        .grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }

        .card {
            background: white;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            padding: 22px;
            margin-bottom: 20px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }

        .card-header h3 {
            font-size: 17px;
        }

        .card-header span {
            font-size: 12px;
            color: #6b7280;
        }

        /* SAFETY INCIDENT */
        .incident {
            border: 1px solid #e5e7eb;
            border-radius: 9px;
            padding: 15px;
            margin-bottom: 12px;
        }

        .incident:last-child {
            margin-bottom: 0;
        }

        .incident-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .incident-title {
            font-weight: bold;
            font-size: 14px;
        }

        .badge {
            padding: 5px 9px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
        }

        .badge.warning {
            background: #fef3c7;
            color: #92400e;
        }

        .badge.danger {
            background: #fee2e2;
            color: #991b1b;
        }

        .badge.safe {
            background: #dcfce7;
            color: #166534;
        }

        .incident p {
            color: #6b7280;
            font-size: 13px;
            line-height: 1.5;
        }

        /* CHECKLIST */
        .check-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 13px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .check-item:last-child {
            border-bottom: none;
        }

        .check-name {
            font-size: 13px;
        }

        .check-status {
            font-size: 12px;
            font-weight: bold;
        }

        .done {
            color: #16a34a;
        }

        .pending {
            color: #d97706;
        }

        /* RESPONSIVE */
        @media (max-width: 1000px) {
            .stats {
                grid-template-columns: repeat(2, 1fr);
            }

            .grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 700px) {
            .sidebar {
                display: none;
            }

            .content {
                padding: 20px;
            }

            .stats {
                grid-template-columns: 1fr;
            }

            .page-header {
                display: block;
            }

            .btn {
                margin-top: 15px;
            }
        }
    </style>
</head>

<body>

<div class="layout">

    <!-- SIDEBAR -->
    <aside class="sidebar">

        <div class="logo">
            🏗 SITEPRO BUILD
        </div>

        <div class="menu-title">Quản lý</div>

        <div class="menu">
            <a href="/">📊 Tổng quan</a>
            <a href="/projects">🏢 Dự án</a>
            <a href="/work-items">📋 Công việc</a>
            <a href="/work-items/tree">🌳 Cây hạng mục</a>
            <a href="/materials">📦 Vật tư</a>
            <a href="/personnel">👥 Nhân sự</a>
            <a href="/safety" class="active">🦺 An toàn</a>
            <a href="/diaries">📖 Nhật ký</a>
        </div>

    </aside>

    <!-- MAIN -->
    <main class="main">

        <header class="topbar">
            <h2>🦺 An toàn công trường</h2>

            <div class="user">
                Xin chào, <strong>{{ auth()->user()->name ?? 'Người dùng' }}</strong>
            </div>
        </header>

        <section class="content">

            <!-- PAGE HEADER -->
            <div class="page-header">
                <div>
                    <h1>An toàn lao động</h1>
                    <p>Theo dõi tình trạng an toàn và các vấn đề phát sinh tại công trường.</p>
                </div>

                <button class="btn">
                    + Ghi nhận sự cố
                </button>
            </div>

            <!-- STATS -->
            <div class="stats">

                <div class="stat-card">
                    <div class="stat-title">Tổng kiểm tra</div>
                    <div class="stat-number">24</div>
                    <div class="stat-note">Trong tháng này</div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">Đạt yêu cầu</div>
                    <div class="stat-number">21</div>
                    <div class="stat-note">87,5% tổng số kiểm tra</div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">Cảnh báo</div>
                    <div class="stat-number">3</div>
                    <div class="stat-note">Cần xử lý</div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">Sự cố nghiêm trọng</div>
                    <div class="stat-number">0</div>
                    <div class="stat-note">Trong tháng này</div>
                </div>

            </div>

            <!-- CONTENT -->
            <div class="grid">

                <!-- LEFT -->
                <div>

                    <div class="card">

                        <div class="card-header">
                            <h3>⚠️ Vấn đề an toàn gần đây</h3>
                            <span>3 vấn đề</span>
                        </div>

                        <div class="incident">

                            <div class="incident-top">
                                <div class="incident-title">
                                    Thiếu dây an toàn tại khu vực tầng 3
                                </div>

                                <span class="badge danger">
                                    Nguy hiểm
                                </span>
                            </div>

                            <p>
                                Phát hiện 2 công nhân chưa sử dụng dây an toàn
                                khi làm việc trên cao. Cần xử lý ngay.
                            </p>

                        </div>

                        <div class="incident">

                            <div class="incident-top">
                                <div class="incident-title">
                                    Biển cảnh báo chưa đầy đủ
                                </div>

                                <span class="badge warning">
                                    Cảnh báo
                                </span>
                            </div>

                            <p>
                                Khu vực tập kết vật tư cần bổ sung biển cảnh báo
                                và phân cách an toàn.
                            </p>

                        </div>

                        <div class="incident">

                            <div class="incident-top">
                                <div class="incident-title">
                                    Kiểm tra hệ thống điện
                                </div>

                                <span class="badge safe">
                                    Đã xử lý
                                </span>
                            </div>

                            <p>
                                Hệ thống điện tại khu vực tầng 2 đã được kiểm tra
                                và không phát hiện vấn đề.
                            </p>

                        </div>

                    </div>

                </div>

                <!-- RIGHT -->
                <div>

                    <div class="card">

                        <div class="card-header">
                            <h3>✅ Checklist hôm nay</h3>
                            <span>07/10/2026</span>
                        </div>

                        <div class="check-item">
                            <span class="check-name">
                                Kiểm tra mũ bảo hộ
                            </span>

                            <span class="check-status done">
                                ✓ Đạt
                            </span>
                        </div>

                        <div class="check-item">
                            <span class="check-name">
                                Kiểm tra dây an toàn
                            </span>

                            <span class="check-status pending">
                                ⚠ Cần kiểm tra
                            </span>
                        </div>

                        <div class="check-item">
                            <span class="check-name">
                                Kiểm tra giàn giáo
                            </span>

                            <span class="check-status done">
                                ✓ Đạt
                            </span>
                        </div>

                        <div class="check-item">
                            <span class="check-name">
                                Kiểm tra hệ thống điện
                            </span>

                            <span class="check-status done">
                                ✓ Đạt
                            </span>
                        </div>

                        <div class="check-item">
                            <span class="check-name">
                                Kiểm tra lối thoát hiểm
                            </span>

                            <span class="check-status pending">
                                ⚠ Chưa kiểm tra
                            </span>
                        </div>

                    </div>

                </div>

            </div>

        </section>

    </main>

</div>

</body>
</html>