```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Quản lý nhân sự - SitePro Build</title>

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

        .table-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .table-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
        }

        .table-header h2 {
            margin: 0 0 5px;
            font-size: 19px;
        }

        .table-header p {
            margin: 0;
            color: #6b7280;
            font-size: 13px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th,
        td {
            padding: 15px 20px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        th {
            background: #f9fafb;
            color: #6b7280;
            font-size: 13px;
        }

        td {
            font-size: 14px;
        }

        .employee {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #dbeafe;
            color: #1d4ed8;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        .employee-name {
            font-weight: 600;
        }

        .employee-email {
            margin-top: 4px;
            color: #6b7280;
            font-size: 12px;
        }

        .role {
            display: inline-block;
            padding: 5px 9px;
            border-radius: 6px;
            background: #eff6ff;
            color: #1d4ed8;
            font-size: 12px;
            font-weight: 600;
        }

        .active {
            background: #dcfce7;
            color: #166534;
        }

        .status {
            padding: 5px 9px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }

        .actions button {
            border: none;
            padding: 7px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            margin-right: 5px;
        }

        .edit {
            background: #fef3c7;
            color: #92400e;
        }

        .delete {
            background: #fee2e2;
            color: #b91c1c;
        }

        @media (max-width: 800px) {
            .stats {
                grid-template-columns: 1fr;
            }

            .page-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }

            .table-card {
                overflow-x: auto;
            }

            table {
                min-width: 900px;
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

            <h1>👥 Quản lý nhân sự</h1>

            <p>
                Quản lý thành viên và vai trò tham gia dự án.
            </p>

        </div>

        <button class="add-btn">
            + Thêm nhân sự
        </button>

    </div>


    <div class="stats">

        <div class="stat-card">

            <div class="stat-label">
                Tổng nhân sự
            </div>

            <div class="stat-value">
                12
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Đang làm việc
            </div>

            <div class="stat-value">
                10
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Vai trò
            </div>

            <div class="stat-value">
                5
            </div>

        </div>

    </div>


    <div class="table-card">

        <div class="table-header">

            <h2>📋 Danh sách nhân sự</h2>

            <p>
                Thành viên đang tham gia quản lý và thi công dự án.
            </p>

        </div>


        <table>

            <thead>

                <tr>

                    <th>
                        Nhân sự
                    </th>

                    <th>
                        Vai trò
                    </th>

                    <th>
                        Số điện thoại
                    </th>

                    <th>
                        Hạng mục phụ trách
                    </th>

                    <th>
                        Trạng thái
                    </th>

                    <th>
                        Thao tác
                    </th>

                </tr>

            </thead>


            <tbody>

                <tr>

                    <td>

                        <div class="employee">

                            <div class="avatar">
                                NA
                            </div>

                            <div>

                                <div class="employee-name">
                                    Nguyễn Văn An
                                </div>

                                <div class="employee-email">
                                    nguyenvanan@example.com
                                </div>

                            </div>

                        </div>

                    </td>

                    <td>
                        <span class="role">
                            Quản lý dự án
                        </span>
                    </td>

                    <td>
                        0901 234 567
                    </td>

                    <td>
                        Toàn bộ công trình
                    </td>

                    <td>
                        <span class="status active">
                            Đang làm việc
                        </span>
                    </td>

                    <td class="actions">

                        <button class="edit">
                            Sửa
                        </button>

                        <button class="delete">
                            Xóa
                        </button>

                    </td>

                </tr>


                <tr>

                    <td>

                        <div class="employee">

                            <div class="avatar">
                                TB
                            </div>

                            <div>

                                <div class="employee-name">
                                    Trần Văn Bình
                                </div>

                                <div class="employee-email">
                                    tranvanbinh@example.com
                                </div>

                            </div>

                        </div>

                    </td>

                    <td>
                        <span class="role">
                            Kỹ sư
                        </span>
                    </td>

                    <td>
                        0902 345 678
                    </td>

                    <td>
                        Phần móng
                    </td>

                    <td>
                        <span class="status active">
                            Đang làm việc
                        </span>
                    </td>

                    <td class="actions">

                        <button class="edit">
                            Sửa
                        </button>

                        <button class="delete">
                            Xóa
                        </button>

                    </td>

                </tr>


                <tr>

                    <td>

                        <div class="employee">

                            <div class="avatar">
                                LC
                            </div>

                            <div>

                                <div class="employee-name">
                                    Lê Văn Cường
                                </div>

                                <div class="employee-email">
                                    lecuong@example.com
                                </div>

                            </div>

                        </div>

                    </td>

                    <td>
                        <span class="role">
                            Đội trưởng
                        </span>
                    </td>

                    <td>
                        0903 456 789
                    </td>

                    <td>
                        Phần thân
                    </td>

                    <td>
                        <span class="status active">
                            Đang làm việc
                        </span>
                    </td>

                    <td class="actions">

                        <button class="edit">
                            Sửa
                        </button>

                        <button class="delete">
                            Xóa
                        </button>

                    </td>

                </tr>


                <tr>

                    <td>

                        <div class="employee">

                            <div class="avatar">
                                PD
                            </div>

                            <div>

                                <div class="employee-name">
                                    Phạm Văn Dũng
                                </div>

                                <div class="employee-email">
                                    phamvandung@example.com
                                </div>

                            </div>

                        </div>

                    </td>

                    <td>
                        <span class="role">
                            Công nhân
                        </span>
                    </td>

                    <td>
                        0904 567 890
                    </td>

                    <td>
                        Đổ bê tông
                    </td>

                    <td>
                        <span class="status active">
                            Đang làm việc
                        </span>
                    </td>

                    <td class="actions">

                        <button class="edit">
                            Sửa
                        </button>

                        <button class="delete">
                            Xóa
                        </button>

                    </td>

                </tr>

            </tbody>

        </table>

    </div>

</div>

</body>
</html>
```
