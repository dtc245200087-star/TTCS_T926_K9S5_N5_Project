<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nhật ký công trường - SITEPRO BUILD</title>

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

        /* FILTER */
        .filter {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 18px;
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }

        .filter input,
        .filter select {
            border: 1px solid #d1d5db;
            border-radius: 7px;
            padding: 10px 12px;
            outline: none;
        }

        .filter input {
            width: 260px;
        }

        /* DIARY */
        .diary {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 15px;
        }

        .diary-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }

        .diary-date {
            font-size: 13px;
            color: #6b7280;
            margin-bottom: 6px;
        }

        .diary-title {
            font-size: 17px;
            font-weight: bold;
        }

        .badge {
            padding: 6px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
        }

        .badge.good {
            background: #dcfce7;
            color: #166534;
        }

        .badge.warning {
            background: #fef3c7;
            color: #92400e;
        }

        .diary-content {
            color: #4b5563;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 15px;
        }

        .diary-info {
            display: flex;
            gap: 25px;
            padding-top: 14px;
            border-top: 1px solid #f0f0f0;
            font-size: 13px;
            color: #6b7280;
        }

        .diary-info strong {
            color: #374151;
        }

        /* RESPONSIVE */
        @media (max-width: 700px) {
            .sidebar {
                display: none;
            }

            .content {
                padding: 20px;
            }

            .page-header {
                display: block;
            }

            .btn {
                margin-top: 15px;
            }

            .filter {
                flex-direction: column;
            }

            .filter input {
                width: 100%;
            }

            .diary-info {
                flex-direction: column;
                gap: 8px;
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
            <a href="/safety">🦺 An toàn</a>
            <a href="/diaries" class="active">📖 Nhật ký</a>
        </div>

    </aside>

    <!-- MAIN -->
    <main class="main">

        <header class="topbar">
            <h2>📖 Nhật ký công trường</h2>

            <div class="user">
                Xin chào,
                <strong>{{ auth()->user()->name ?? 'Người dùng' }}</strong>
            </div>
        </header>

        <section class="content">

            <!-- HEADER -->
            <div class="page-header">
                <div>
                    <h1>Nhật ký công trường</h1>
                    <p>Ghi nhận tình hình thi công và hoạt động tại công trường.</p>
                </div>

                <button class="btn">
                    + Tạo nhật ký
                </button>
            </div>

            <!-- FILTER -->
            <div class="filter">

                <input
                    type="text"
                    placeholder="🔍 Tìm kiếm nhật ký..."
                >

                <select>
                    <option>Tất cả hạng mục</option>
                    <option>Phần móng</option>
                    <option>Phần thân</option>
                    <option>Phần hoàn thiện</option>
                </select>

                <select>
                    <option>Tất cả trạng thái</option>
                    <option>Hoàn thành</option>
                    <option>Có vấn đề</option>
                </select>

            </div>

            <!-- DIARY 1 -->
            <div class="diary">

                <div class="diary-top">

                    <div>
                        <div class="diary-date">
                            📅 07/10/2026
                        </div>

                        <div class="diary-title">
                            Thi công phần thân tầng 2
                        </div>
                    </div>

                    <span class="badge good">
                        Hoàn thành
                    </span>

                </div>

                <div class="diary-content">
                    Hôm nay đội thi công thực hiện lắp dựng cột và dầm
                    tầng 2. Công việc diễn ra đúng tiến độ, điều kiện thời tiết
                    thuận lợi và không phát sinh vấn đề nghiêm trọng.
                </div>

                <div class="diary-info">
                    <span>👤 Người ghi: <strong>Nguyễn Văn An</strong></span>
                    <span>🏗 Hạng mục: <strong>Phần thân</strong></span>
                    <span>👷 Nhân công: <strong>12 người</strong></span>
                </div>

            </div>

            <!-- DIARY 2 -->
            <div class="diary">

                <div class="diary-top">

                    <div>
                        <div class="diary-date">
                            📅 06/10/2026
                        </div>

                        <div class="diary-title">
                            Đổ bê tông móng
                        </div>
                    </div>

                    <span class="badge good">
                        Hoàn thành
                    </span>

                </div>

                <div class="diary-content">
                    Đã hoàn thành công tác đổ bê tông móng khu vực A.
                    Chất lượng bê tông được kiểm tra và đảm bảo yêu cầu.
                    Công tác vệ sinh sau thi công đã hoàn tất.
                </div>

                <div class="diary-info">
                    <span>👤 Người ghi: <strong>Trần Văn Bình</strong></span>
                    <span>🏗 Hạng mục: <strong>Phần móng</strong></span>
                    <span>👷 Nhân công: <strong>18 người</strong></span>
                </div>

            </div>

            <!-- DIARY 3 -->
            <div class="diary">

                <div class="diary-top">

                    <div>
                        <div class="diary-date">
                            📅 05/10/2026
                        </div>

                        <div class="diary-title">
                            Công tác chuẩn bị vật tư
                        </div>
                    </div>

                    <span class="badge warning">
                        Có vấn đề
                    </span>

                </div>

                <div class="diary-content">
                    Một số vật tư phục vụ thi công phần thân chưa được
                    chuyển đến công trường đúng thời gian dự kiến. Đã liên hệ
                    bộ phận vật tư để xử lý và bổ sung.
                </div>

                <div class="diary-info">
                    <span>👤 Người ghi: <strong>Lê Văn Cường</strong></span>
                    <span>🏗 Hạng mục: <strong>Phần thân</strong></span>
                    <span>👷 Nhân công: <strong>8 người</strong></span>
                </div>

            </div>

        </section>

    </main>

</div>

</body>
</html>