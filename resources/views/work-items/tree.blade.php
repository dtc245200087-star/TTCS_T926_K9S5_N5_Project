<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cây hạng mục - SitePro Build</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }

        body {
            background: #f5f7fa;
            color: #1f2937;
        }

        .header {
            background: #111827;
            color: white;
            padding: 18px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h2 {
            font-size: 20px;
        }

        .back {
            color: white;
            text-decoration: none;
            background: #374151;
            padding: 9px 15px;
            border-radius: 7px;
        }

        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }

        .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        .top h1 {
            font-size: 28px;
        }

        .add-btn {
            background: #2563eb;
            color: white;
            border: none;
            padding: 11px 18px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }

        .tree-box {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        }

        .tree {
            list-style: none;
        }

        .tree ul {
            list-style: none;
            margin-left: 28px;
            border-left: 2px solid #e5e7eb;
            padding-left: 20px;
        }

        .tree li {
            margin: 12px 0;
        }

        .item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 13px 16px;
            background: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }

        .item-name {
            font-weight: 600;
        }

        .actions button {
            border: none;
            padding: 6px 10px;
            border-radius: 6px;
            cursor: pointer;
            margin-left: 5px;
        }

        .edit {
            background: #fef3c7;
            color: #92400e;
        }

        .delete {
            background: #fee2e2;
            color: #b91c1c;
        }

        .badge {
            font-size: 12px;
            background: #dbeafe;
            color: #1d4ed8;
            padding: 4px 8px;
            border-radius: 20px;
            margin-left: 8px;
        }
    </style>
</head>

<body>

<header class="header">
    <h2>🏗 SITEPRO BUILD</h2>
    <a href="/" class="back">← Tổng quan</a>
</header>

<div class="container">

    <div class="top">
        <div>
            <h1>🌳 Cây hạng mục</h1>
            <p style="margin-top:8px;color:#6b7280;">
                Quản lý cấu trúc và các hạng mục của công trình
            </p>
        </div>

        <button class="add-btn">+ Thêm hạng mục</button>
    </div>

    <div class="tree-box">

        <ul class="tree">

            <li>
                <div class="item">
                    <span class="item-name">
                        🏗 Công trình xây dựng
                        <span class="badge">Hạng mục gốc</span>
                    </span>

                    <div class="actions">
                        <button class="edit">Sửa</button>
                        <button class="delete">Xóa</button>
                    </div>
                </div>

                <ul>

                    <li>
                        <div class="item">
                            <span class="item-name">📁 1. Phần móng</span>

                            <div class="actions">
                                <button class="edit">Sửa</button>
                                <button class="delete">Xóa</button>
                            </div>
                        </div>

                        <ul>
                            <li>
                                <div class="item">
                                    <span class="item-name">📄 1.1 Đào móng</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>

                            <li>
                                <div class="item">
                                    <span class="item-name">📄 1.2 Gia công cốt thép móng</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>

                            <li>
                                <div class="item">
                                    <span class="item-name">📄 1.3 Đổ bê tông móng</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </li>

                    <li>
                        <div class="item">
                            <span class="item-name">📁 2. Phần thân</span>

                            <div class="actions">
                                <button class="edit">Sửa</button>
                                <button class="delete">Xóa</button>
                            </div>
                        </div>

                        <ul>
                            <li>
                                <div class="item">
                                    <span class="item-name">📄 2.1 Cột</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>

                            <li>
                                <div class="item">
                                    <span class="item-name">📄 2.2 Dầm</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>

                            <li>
                                <div class="item">
                                    <span class="item-name">📄 2.3 Sàn</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </li>

                    <li>
                        <div class="item">
                            <span class="item-name">📁 3. Phần hoàn thiện</span>

                            <div class="actions">
                                <button class="edit">Sửa</button>
                                <button class="delete">Xóa</button>
                            </div>
                        </div>

                        <ul>
                            <li>
                                <div class="item">
                                    <span class="item-name">📄 3.1 Xây tường</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>

                            <li>
                                <div class="item">
                                    <span class="item-name">📄 3.2 Trát tường</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>

                            <li>
                                <div class="item">
                                    <span class="item-name">📄 3.3 Sơn</span>
                                    <div class="actions">
                                        <button class="edit">Sửa</button>
                                        <button class="delete">Xóa</button>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </li>

                </ul>
            </li>

        </ul>

    </div>

</div>

</body>
</html>