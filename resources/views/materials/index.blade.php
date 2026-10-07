<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Quản lý vật tư - SitePro Build</title>

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
            font-size: 13px;
            color: #6b7280;
        }

        td {
            font-size: 14px;
        }

        .material-name {
            font-weight: 600;
        }

        .category {
            color: #2563eb;
            background: #eff6ff;
            padding: 5px 9px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }

        .quantity {
            font-weight: bold;
        }

        .unit {
            color: #6b7280;
        }

        .normal {
            color: #166534;
            background: #dcfce7;
        }

        .low {
            color: #92400e;
            background: #fef3c7;
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
                min-width: 850px;
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

            <h1>📦 Quản lý vật tư</h1>

            <p>
                Theo dõi vật tư, số lượng và tình trạng sử dụng trong công trình.
            </p>

        </div>

        <button class="add-btn">
            + Thêm vật tư
        </button>

    </div>


    <div class="stats">

        <div class="stat-card">

            <div class="stat-label">
                Tổng loại vật tư
            </div>

            <div class="stat-value">
                6
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Đủ số lượng
            </div>

            <div class="stat-value">
                4
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Sắp hết
            </div>

            <div class="stat-value">
                2
            </div>

        </div>

    </div>


    <div class="table-card">

        <div class="table-header">

            <h2>📋 Danh sách vật tư</h2>

            <p>
                Danh sách vật tư đang được sử dụng trong dự án.
            </p>

        </div>


        <table>

            <thead>

                <tr>

                    <th>
                        Tên vật tư
                    </th>

                    <th>
                        Loại
                    </th>

                    <th>
                        Số lượng
                    </th>

                    <th>
                        Đơn vị
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

                    <td class="material-name">
                        Xi măng PCB40
                    </td>

                    <td>
                        <span class="category">
                            Vật liệu xây dựng
                        </span>
                    </td>

                    <td class="quantity">
                        250
                    </td>

                    <td class="unit">
                        Bao
                    </td>

                    <td>
                        <span class="status normal">
                            Đủ
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

                    <td class="material-name">
                        Thép Φ16
                    </td>

                    <td>
                        <span class="category">
                            Sắt thép
                        </span>
                    </td>

                    <td class="quantity">
                        3.5
                    </td>

                    <td class="unit">
                        Tấn
                    </td>

                    <td>
                        <span class="status normal">
                            Đủ
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

                    <td class="material-name">
                        Cát xây dựng
                    </td>

                    <td>
                        <span class="category">
                            Vật liệu xây dựng
                        </span>
                    </td>

                    <td class="quantity">
                        18
                    </td>

                    <td class="unit">
                        m³
                    </td>

                    <td>
                        <span class="status low">
                            Sắp hết
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

                    <td class="material-name">
                        Đá 1x2
                    </td>

                    <td>
                        <span class="category">
                            Vật liệu xây dựng
                        </span>
                    </td>

                    <td class="quantity">
                        25
                    </td>

                    <td class="unit">
                        m³
                    </td>

                    <td>
                        <span class="status normal">
                            Đủ
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

                    <td class="material-name">
                        Gạch xây
                    </td>

                    <td>
                        <span class="category">
                            Gạch
                        </span>
                    </td>

                    <td class="quantity">
                        1.200
                    </td>

                    <td class="unit">
                        Viên
                    </td>

                    <td>
                        <span class="status normal">
                            Đủ
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

                    <td class="material-name">
                        Sơn nội thất
                    </td>

                    <td>
                        <span class="category">
                            Sơn
                        </span>
                    </td>

                    <td class="quantity">
                        12
                    </td>

                    <td class="unit">
                        Thùng
                    </td>

                    <td>
                        <span class="status low">
                            Sắp hết
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

