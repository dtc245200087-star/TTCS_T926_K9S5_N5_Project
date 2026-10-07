```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">

    <title>Quản lý công việc</title>

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
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        .brand {
            font-size: 20px;
            font-weight: bold;
        }

        .back-btn {
            text-decoration: none;
            color: white;
            background: #374151;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            transition: 0.2s;
        }

        .back-btn:hover {
            background: #4b5563;
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

        .page-title h1 {
            margin: 0 0 8px;
            font-size: 28px;
        }

        .page-title p {
            margin: 0;
            color: #6b7280;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
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

        .main-card {
            background: white;
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
            overflow: hidden;
        }

        .card-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-header h2 {
            margin: 0;
            font-size: 19px;
        }

        .card-header p {
            margin: 5px 0 0;
            color: #6b7280;
            font-size: 13px;
        }

        .project {
            padding: 22px;
        }

        .project-header {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            padding: 15px 18px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 15px;
        }

        .work-item {
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            margin-bottom: 15px;
            overflow: hidden;
        }

        .work-item-header {
            padding: 15px 18px;
            background: #f8fafc;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e5e7eb;
        }

        .work-item-name {
            font-weight: bold;
            font-size: 16px;
        }

        .category-badge {
            display: inline-block;
            margin-left: 8px;
            padding: 4px 9px;
            border-radius: 20px;
            background: #dbeafe;
            color: #1d4ed8;
            font-size: 11px;
            font-weight: bold;
        }

        .task-list {
            padding: 10px 15px 5px;
        }

        .task {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 13px 12px;
            margin-bottom: 8px;
            background: #fafafa;
            border: 1px solid #eeeeee;
            border-radius: 8px;
        }

        .task-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .task-icon {
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #eff6ff;
            border-radius: 7px;
            font-size: 14px;
        }

        .task-name {
            font-weight: 600;
        }

        .task-actions {
            display: flex;
            align-items: center;
            gap: 7px;
        }

        .task-duration {
            padding: 6px 10px;
            border-radius: 6px;
            background: #f3f4f6;
            color: #4b5563;
            font-size: 13px;
            margin-right: 5px;
        }

        button {
            font-family: inherit;
        }

        .edit-task-button,
        .delete-task-button {
            border: none;
            padding: 7px 11px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
        }

        .edit-task-button {
            background: #fef3c7;
            color: #92400e;
        }

        .edit-task-button:hover {
            background: #fde68a;
        }

        .delete-task-button {
            background: #fee2e2;
            color: #b91c1c;
        }

        .delete-task-button:hover {
            background: #fecaca;
        }

        .add-task-button {
            margin: 8px 15px 15px;
            background: #2563eb;
            color: white;
            border: none;
            padding: 9px 14px;
            border-radius: 7px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
        }

        .add-task-button:hover {
            background: #1d4ed8;
        }

        .empty {
            color: #9ca3af;
            padding: 15px;
            font-size: 13px;
        }

        .form-card {
            display: none;
            margin: 20px 22px 22px;
            padding: 22px;
            border: 1px solid #dbeafe;
            border-radius: 10px;
            background: #f8fbff;
        }

        .form-card h3 {
            margin: 0 0 20px;
            font-size: 18px;
        }

        .form-group {
            margin-bottom: 17px;
        }

        label {
            display: block;
            margin-bottom: 7px;
            font-weight: 600;
            font-size: 14px;
        }

        input {
            width: 100%;
            padding: 11px 13px;
            border: 1px solid #d1d5db;
            border-radius: 7px;
            font-size: 14px;
            background: white;
        }

        input:focus {
            outline: none;
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
        }

        .duration-note {
            margin-top: 6px;
            font-size: 12px;
            color: #6b7280;
        }

        .duration-error {
            display: none;
            margin-top: 6px;
            color: #dc2626;
            font-size: 13px;
        }

        .form-actions {
            display: flex;
            gap: 10px;
        }

        .submit-button,
        .cancel-button {
            border: none;
            padding: 10px 18px;
            border-radius: 7px;
            cursor: pointer;
            font-weight: 600;
        }

        .submit-button {
            background: #2563eb;
            color: white;
        }

        .submit-button:hover {
            background: #1d4ed8;
        }

        .cancel-button {
            background: #e5e7eb;
            color: #374151;
        }

        .cancel-button:hover {
            background: #d1d5db;
        }

        .message {
            margin-top: 15px;
            padding: 11px;
            border-radius: 7px;
            display: none;
            font-size: 14px;
        }

        .success {
            display: block;
            background: #dcfce7;
            color: #166534;
        }

        .error-message {
            display: block;
            background: #fee2e2;
            color: #991b1b;
        }

        @media (max-width: 700px) {
            .stats {
                grid-template-columns: 1fr;
            }

            .page-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }

            .task {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }

            .task-actions {
                width: 100%;
                flex-wrap: wrap;
            }
        }
    </style>
</head>

<body>

<header class="topbar">
    <div class="brand">🏗 SITEPRO BUILD</div>

    <a href="/" class="back-btn">
        ← Quay lại
    </a>
</header>

<div class="container">

    <div class="page-header">
        <div class="page-title">
            <h1>📋 Quản lý công việc</h1>
            <p>Quản lý các công việc được gắn với từng hạng mục của dự án.</p>
        </div>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-label">Tổng số công việc</div>
            <div class="stat-value" id="totalTasks">0</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Số hạng mục</div>
            <div class="stat-value" id="totalWorkItems">0</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Tổng thời lượng</div>
            <div class="stat-value">
                <span id="totalDuration">0</span>
                <span style="font-size:15px;font-weight:normal;color:#6b7280;">
                    ngày
                </span>
            </div>
        </div>
    </div>

    <div class="main-card">

        <div class="card-header">
            <div>
                <h2>🌳 Danh sách công việc</h2>
                <p>Công việc được phân theo từng hạng mục công trình</p>
            </div>
        </div>

        <div id="projectTree">
            <div class="empty">
                Đang tải dữ liệu...
            </div>
        </div>

        <div id="taskFormCard" class="form-card">

            <h3 id="formTitle">Thêm công việc</h3>

            <form id="taskForm">

                <div class="form-group">
                    <label for="taskName">
                        Tên công việc
                    </label>

                    <input
                        type="text"
                        id="taskName"
                        maxlength="255"
                        required
                        placeholder="Ví dụ: Đào móng công trình"
                    >
                </div>

                <div class="form-group">

                    <label for="taskDuration">
                        Thời lượng (ngày)
                    </label>

                    <input
                        type="number"
                        id="taskDuration"
                        min="1"
                        step="1"
                        required
                        placeholder="Ví dụ: 5"
                    >

                    <div class="duration-note">
                        Thời lượng phải là số nguyên dương, lớn hơn 0.
                    </div>

                    <div id="durationError" class="duration-error">
                        Thời lượng phải lớn hơn 0.
                    </div>

                </div>

                <div class="form-actions">

                    <button
                        type="submit"
                        class="submit-button"
                        id="submitButton"
                    >
                        Thêm công việc
                    </button>

                    <button
                        type="button"
                        class="cancel-button"
                        id="cancelButton"
                    >
                        Hủy
                    </button>

                </div>

            </form>

            <div id="message" class="message"></div>

        </div>

    </div>

</div>

<script>

    const projectId = 1;

    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        .getAttribute('content');

    const projectTree = document.getElementById('projectTree');
    const taskFormCard = document.getElementById('taskFormCard');
    const taskForm = document.getElementById('taskForm');
    const taskName = document.getElementById('taskName');
    const taskDuration = document.getElementById('taskDuration');
    const durationError = document.getElementById('durationError');
    const submitButton = document.getElementById('submitButton');
    const cancelButton = document.getElementById('cancelButton');
    const message = document.getElementById('message');

    let selectedWorkItemId = null;

    async function loadWorkItems() {

        try {

            const response = await fetch(
                `/api/v1/projects/${projectId}/work-items`,
                {
                    headers: {
                        'Accept': 'application/json'
                    }
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || 'Không thể tải cây hạng mục.'
                );
            }

            renderWorkItems(data);

        } catch (error) {

            projectTree.innerHTML = `
                <div class="empty">
                    ${error.message}
                </div>
            `;
        }
    }

    function renderWorkItems(workItems) {

        let totalTasks = 0;
        let totalDuration = 0;

        workItems.forEach(workItem => {

            if (workItem.tasks) {

                totalTasks += workItem.tasks.length;

                workItem.tasks.forEach(task => {
                    totalDuration += Number(task.duration) || 0;
                });
            }
        });

        document.getElementById('totalTasks').textContent = totalTasks;
        document.getElementById('totalWorkItems').textContent = workItems.length;
        document.getElementById('totalDuration').textContent = totalDuration;

        if (workItems.length === 0) {

            projectTree.innerHTML = `
                <div class="empty">
                    Chưa có hạng mục nào.
                </div>
            `;

            return;
        }

        let html = `
            <div class="project">

                <div class="project-header">
                    🏗 Dự án xây dựng mẫu
                </div>
        `;

        workItems.forEach(workItem => {

            html += `
                <div class="work-item">

                    <div class="work-item-header">

                        <div class="work-item-name">
                            📁 ${escapeHtml(workItem.name)}
                            <span class="category-badge">
                                HẠNG MỤC
                            </span>
                        </div>

                    </div>

                    <div class="task-list">
            `;

            if (workItem.tasks && workItem.tasks.length > 0) {

                workItem.tasks.forEach(task => {

                    html += `
                        <div class="task">

                            <div class="task-info">

                                <div class="task-icon">
                                    ✓
                                </div>

                                <span class="task-name">
                                    ${escapeHtml(task.name)}
                                </span>

                            </div>

                            <div class="task-actions">

                                <span class="task-duration">
                                    ⏱ ${task.duration} ngày
                                </span>

                                <button
                                    type="button"
                                    class="edit-task-button"
                                    onclick="openEditTaskForm(
                                        ${workItem.id},
                                        ${task.id},
                                        '${escapeJs(task.name)}',
                                        ${task.duration}
                                    )"
                                >
                                    Sửa
                                </button>

                                <button
                                    type="button"
                                    class="delete-task-button"
                                    onclick="deleteTask(
                                        ${workItem.id},
                                        ${task.id}
                                    )"
                                >
                                    Xóa
                                </button>

                            </div>

                        </div>
                    `;
                });

            } else {

                html += `
                    <div class="empty">
                        Chưa có công việc trong hạng mục này.
                    </div>
                `;
            }

            html += `
                    </div>

                    <button
                        type="button"
                        class="add-task-button"
                        onclick="openTaskForm(${workItem.id})"
                    >
                        + Thêm công việc
                    </button>

                </div>
            `;
        });

        html += `
            </div>
        `;

        projectTree.innerHTML = html;
    }

    function openTaskForm(workItemId) {

        selectedWorkItemId = workItemId;

        taskForm.reset();

        durationError.style.display = 'none';

        message.className = 'message';
        message.textContent = '';

        taskFormCard.style.display = 'block';

        document.getElementById('formTitle').textContent =
            'Thêm công việc';

        submitButton.textContent = 'Thêm công việc';

        delete taskForm.dataset.editingTaskId;

        taskName.focus();
    }

    function openEditTaskForm(
        workItemId,
        taskId,
        name,
        duration
    ) {

        selectedWorkItemId = workItemId;

        taskForm.reset();

        taskName.value = name;
        taskDuration.value = duration;

        durationError.style.display = 'none';

        message.className = 'message';
        message.textContent = '';

        taskFormCard.style.display = 'block';

        document.getElementById('formTitle').textContent =
            'Sửa công việc';

        submitButton.textContent = 'Lưu thay đổi';

        taskForm.dataset.editingTaskId = taskId;

        taskName.focus();
    }

    cancelButton.addEventListener('click', function () {

        taskForm.reset();

        taskFormCard.style.display = 'none';

        durationError.style.display = 'none';

        message.className = 'message';
        message.textContent = '';

        selectedWorkItemId = null;

        delete taskForm.dataset.editingTaskId;

        document.getElementById('formTitle').textContent =
            'Thêm công việc';

        submitButton.textContent = 'Thêm công việc';
    });

    taskDuration.addEventListener('input', function () {

        const value = Number(this.value);

        if (
            this.value !== '' &&
            (!Number.isInteger(value) || value <= 0)
        ) {

            durationError.style.display = 'block';

            this.setCustomValidity(
                'Thời lượng phải lớn hơn 0.'
            );

        } else {

            durationError.style.display = 'none';

            this.setCustomValidity('');
        }
    });

    taskForm.addEventListener('submit', async function (event) {

        event.preventDefault();

        const name = taskName.value.trim();
        const duration = Number(taskDuration.value);
        const editingTaskId = taskForm.dataset.editingTaskId;

        if (
            !Number.isInteger(duration) ||
            duration <= 0
        ) {

            durationError.style.display = 'block';

            taskDuration.focus();

            return;
        }

        if (!selectedWorkItemId) {
            return;
        }

        submitButton.disabled = true;

        submitButton.textContent = editingTaskId
            ? 'Đang lưu...'
            : 'Đang thêm...';

        try {

            let url;
            let method;

            if (editingTaskId) {

                url =
                    `/api/v1/projects/${projectId}/work-items/${selectedWorkItemId}/tasks/${editingTaskId}`;

                method = 'PATCH';

            } else {

                url =
                    `/api/v1/projects/${projectId}/work-items/${selectedWorkItemId}/tasks`;

                method = 'POST';
            }

            const response = await fetch(url, {

                method: method,

                headers: {

                    'Content-Type': 'application/json',

                    'Accept': 'application/json',

                    'X-CSRF-TOKEN': csrfToken
                },

                body: JSON.stringify({

                    name: name,

                    duration: duration
                })
            });

            const data = await response.json();

            if (!response.ok) {

                throw new Error(
                    data.message ||
                    (
                        editingTaskId
                            ? 'Không thể sửa công việc.'
                            : 'Không thể thêm công việc.'
                    )
                );
            }

            message.className = 'message success';

            message.textContent = editingTaskId
                ? 'Sửa công việc thành công!'
                : 'Thêm công việc thành công!';

            taskForm.reset();

            taskFormCard.style.display = 'none';

            durationError.style.display = 'none';

            delete taskForm.dataset.editingTaskId;

            await loadWorkItems();

        } catch (error) {

            message.className = 'message error-message';

            message.textContent = error.message;
        }

        submitButton.disabled = false;

        submitButton.textContent = 'Thêm công việc';
    });

    function escapeHtml(value) {

        const div = document.createElement('div');

        div.textContent = value;

        return div.innerHTML;
    }

    function escapeJs(value) {

        return String(value)
            .replace(/\\/g, '\\\\')
            .replace(/'/g, "\\'");
    }

    async function deleteTask(workItemId, taskId) {

        const confirmed = confirm(
            'Bạn có chắc muốn xóa công việc này không?'
        );

        if (!confirmed) {
            return;
        }

        try {

            const response = await fetch(
                `/api/v1/projects/${projectId}/work-items/${workItemId}/tasks/${taskId}`,
                {
                    method: 'DELETE',

                    headers: {
                        'Accept': 'application/json',
                        'X-CSRF-TOKEN': csrfToken
                    }
                }
            );

            const data = await response.json();

            if (!response.ok) {

                throw new Error(
                    data.message ||
                    'Không thể xóa công việc.'
                );
            }

            alert('Xóa công việc thành công!');

            await loadWorkItems();

        } catch (error) {

            alert(error.message);
        }
    }

    loadWorkItems();

</script>

</body>
</html>
```
