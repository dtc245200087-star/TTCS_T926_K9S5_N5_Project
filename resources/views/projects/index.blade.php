<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Quản lý dự án - SitePro Build</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            color: #1f2937;
        }

        .topbar {
            height: 70px;
            background: #111827;
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 35px;
        }

        .brand {
            font-size: 20px;
            font-weight: bold;
        }

        .back-btn {
            color: white;
            text-decoration: none;
            background: #374151;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 14px;
        }

        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }

        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        .page-header h1 {
            margin: 0 0 8px;
            font-size: 28px;
        }

        .page-header p {
            margin: 0;
            color: #6b7280;
        }

        .add-btn {
            border: none;
            background: #2563eb;
            color: white;
            padding: 11px 18px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }

        .add-btn:hover {
            background: #1d4ed8;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
        }

        .stat-label {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: bold;
        }

        .project-list {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .project-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 22px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .project-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }

        .project-icon {
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #eff6ff;
            border-radius: 10px;
            font-size: 22px;
        }

        .status {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }

        .active {
            background: #dcfce7;
            color: #166534;
        }

        .planning {
            background: #fef3c7;
            color: #92400e;
        }

        .project-card h3 {
            margin: 0 0 8px;
            font-size: 18px;
        }

        .project-card p {
            margin: 0 0 18px;
            color: #6b7280;
            font-size: 14px;
        }

        .info {
            border-top: 1px solid #e5e7eb;
            padding-top: 15px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 14px;
        }

        .info-label {
            color: #6b7280;
        }

        .progress-box {
            margin-top: 15px;
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 7px;
        }

        .progress {
            height: 8px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            background: #2563eb;
            border-radius: 10px;
        }

        .actions {
            display: flex;
            gap: 8px;
            margin-top: 18px;
        }

        .action-btn {
            flex: 1;
            padding: 9px;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-weight: 600;
        }

        .detail {
            background: #eff6ff;
            color: #1d4ed8;
        }

        .edit {
            background: #fef3c7;
            color: #92400e;
        }

        @media (max-width: 800px) {
            .stats,
            .project-list {
                grid-template-columns: 1fr;
            }

            .page-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }
        }
    </style>
</head>

<body>

<header class="topbar">
    <div class="brand">
        🏗 SITEPRO BUILD
    </div>

    <a href="/" class="back-btn">
        ← Tổng quan
    </a>
</header>

<div class="container">

    <div class="page-header">

        <div>
            <h1>📁 Quản lý dự án</h1>

            <p>
                Quản lý các dự án xây dựng và tiến độ thực hiện.
            </p>
        </div>

        <button class="add-btn">
            + Thêm dự án
        </button>

    </div>

    <div class="stats">

        <div class="stat-card">
            <div class="stat-label">
                Tổng số dự án
            </div>

            <div class="stat-value">
                2
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-label">
                Đang thực hiện
            </div>

            <div class="stat-value">
                1
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-label">
                Đang chuẩn bị
            </div>

            <div class="stat-value">
                1
            </div>
        </div>

    </div>

    <div class="project-list">

        <!-- Dự án 1 -->

        <div class="project-card">

            <div class="project-top">

                <div class="project-icon">
                    🏢
                </div>

                <span class="status active">
                    Đang thực hiện
                </span>

            </div>

            <h3>
                Công trình xây dựng A
            </h3>

            <p>
                Xây dựng khu nhà ở và các hạng mục phụ trợ.
            </p>

            <div class="info">

                <div class="info-row">
                    <span class="info-label">
                        Chủ đầu tư
                    </span>

                    <strong>
                        Công ty ABC
                    </strong>
                </div>

                <div class="info-row">
                    <span class="info-label">
                        Ngày bắt đầu
                    </span>

                    <strong>
                        01/10/2026
                    </strong>
                </div>

                <div class="info-row">
                    <span class="info-label">
                        Thành viên
                    </span>

                    <strong>
                        12 người
                    </strong>
                </div>

            </div>

            <div class="progress-box">

                <div class="progress-header">
                    <span>Tiến độ</span>
                    <strong>65%</strong>
                </div>

                <div class="progress">
                    <div
                        class="progress-bar"
                        style="width: 65%;"
                    ></div>
                </div>

            </div>

            <div class="actions">

                <button class="action-btn detail">
                    Xem chi tiết
                </button>

                <button class="action-btn edit">
                    Chỉnh sửa
                </button>

            </div>

        </div>


        <!-- Dự án 2 -->

        <div class="project-card">

            <div class="project-top">

                <div class="project-icon">
                    🏗
                </div>

                <span class="status planning">
                    Đang chuẩn bị
                </span>

            </div>

            <h3>
                Công trình xây dựng B
            </h3>

            <p>
                Dự án xây dựng khu văn phòng và nhà kho.
            </p>

            <div class="info">

                <div class="info-row">
                    <span class="info-label">
                        Chủ đầu tư
                    </span>

                    <strong>
                        Công ty XYZ
                    </strong>
                </div>

                <div class="info-row">
                    <span class="info-label">
                        Ngày bắt đầu
                    </span>

                    <strong>
                        15/11/2026
                    </strong>
                </div>

                <div class="info-row">
                    <span class="info-label">
                        Thành viên
                    </span>

                    <strong>
                        8 người
                    </strong>
                </div>

            </div>

            <div class="progress-box">

                <div class="progress-header">
                    <span>Tiến độ</span>
                    <strong>20%</strong>
                </div>

                <div class="progress">
                    <div
                        class="progress-bar"
                        style="width: 20%;"
                    ></div>
                </div>

            </div>

            <div class="actions">

                <button class="action-btn detail">
                    Xem chi tiết
                </button>

                <button class="action-btn edit">
                    Chỉnh sửa
                </button>

            </div>

        </div>

    </div>

</div>

</body>
</html>
