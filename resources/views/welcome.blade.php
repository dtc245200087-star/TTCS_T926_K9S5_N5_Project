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
            background: #f5f5f5;
            color: #222;
        }

        .container {
            max-width: 1000px;
            margin: 40px auto;
            padding: 20px;
        }

        .header {
            background: white;
            padding: 22px 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .header h1 {
            margin: 0 0 8px;
        }

        .header p {
            margin: 0;
            color: #666;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .card h2 {
            margin-top: 0;
            margin-bottom: 20px;
        }

        .project {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }

        .project-header {
            padding: 15px 18px;
            background: #f8fafc;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
            font-size: 17px;
        }

        .work-item {
            padding: 16px 18px;
            border-bottom: 1px solid #eee;
        }

        .work-item:last-child {
            border-bottom: none;
        }

        .work-item-name {
            font-weight: bold;
            margin-bottom: 12px;
        }

        .task {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 9px 12px;
            margin-bottom: 7px;
            background: #f8fafc;
            border-radius: 6px;
        }

        .task:last-child {
            margin-bottom: 0;
        }

        .task-duration {
            color: #666;
            font-size: 14px;
        }

        .add-task-button {
            margin-top: 12px;
            background: #2563eb;
            color: white;
            border: none;
            padding: 9px 15px;
            border-radius: 6px;
            cursor: pointer;
        }

        .add-task-button:hover {
            background: #1d4ed8;
        }
        .edit-task-button {
    margin-left: 10px;
    padding: 5px 10px;
    border: none;
    border-radius: 5px;
    background: #f59e0b;
    color: white;
    cursor: pointer;
    font-size: 13px;
}

.edit-task-button:hover {
    background: #d97706;
}
        .delete-task-button {
    margin-left: 10px;
    padding: 5px 10px;
    border: none;
    border-radius: 5px;
    background: #dc2626;
    color: white;
    cursor: pointer;
    font-size: 13px;
}

.delete-task-button:hover {
    background: #b91c1c;
}

        .empty {
            color: #777;
            padding: 10px 0;
            font-size: 14px;
        }

        .form-card {
            display: none;
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }

        .form-card h3 {
            margin-top: 0;
        }

        .form-group {
            margin-bottom: 16px;
        }

        label {
            display: block;
            margin-bottom: 7px;
            font-weight: bold;
        }

        input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 15px;
        }

        input:focus {
            outline: none;
            border-color: #2563eb;
        }

        .duration-note {
            margin-top: 6px;
            font-size: 13px;
            color: #666;
        }

        .duration-error {
            display: none;
            margin-top: 6px;
            color: #dc2626;
            font-size: 14px;
        }

        .form-actions {
            display: flex;
            gap: 10px;
        }

        .submit-button {
            border: none;
            background: #2563eb;
            color: white;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
        }

        .cancel-button {
            border: none;
            background: #e5e7eb;
            color: #222;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
        }

        .message {
            margin-top: 15px;
            padding: 11px;
            border-radius: 6px;
            display: none;
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
    </style>
</head>

<body>

<div class="container">

    <div class="header">
        <h1>Quản lý công việc</h1>
        <p>Cây hạng mục và các công việc trong dự án</p>
    </div>

    <div class="card">

        <h2>Cây hạng mục</h2>

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
                        placeholder="Nhập tên công việc"
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
                    Dự án xây dựng mẫu
                </div>
        `;

        workItems.forEach(workItem => {
            html += `
                <div class="work-item">
                    <div class="work-item-name">
                        ${escapeHtml(workItem.name)}
                    </div>
            `;

            if (workItem.tasks && workItem.tasks.length > 0) {
                workItem.tasks.forEach(task => {
                    html += `
                        <div class="task">
    <span>
        ${escapeHtml(task.name)}
    </span>

   <span>
    <span class="task-duration">
        ${task.duration} ngày
    </span>

    <button
        type="button"
        class="edit-task-button"
        onclick="openEditTaskForm(${workItem.id}, ${task.id}, '${escapeJs(task.name)}', ${task.duration})"
    >
        Sửa
    </button>

    <button
        type="button"
        class="delete-task-button"
        onclick="deleteTask(${workItem.id}, ${task.id})"
    >
        Xóa
    </button>
</span>
</div>
                    `;
                });
            } else {
                html += `
                    <div class="empty">
                        Chưa có công việc.
                    </div>
                `;
            }

            html += `
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

        html += `</div>`;

        projectTree.innerHTML = html;
    }

    function openTaskForm(workItemId) {
    selectedWorkItemId = workItemId;

    taskForm.reset();

    durationError.style.display = 'none';
    message.className = 'message';
    message.textContent = '';

    taskFormCard.style.display = 'block';

    document.getElementById('formTitle').textContent = 'Thêm công việc';
    submitButton.textContent = 'Thêm công việc';

    delete taskForm.dataset.editingTaskId;

    taskName.focus();
}

function openEditTaskForm(workItemId, taskId, name, duration) {
    selectedWorkItemId = workItemId;

    taskForm.reset();

    taskName.value = name;
    taskDuration.value = duration;

    durationError.style.display = 'none';
    message.className = 'message';
    message.textContent = '';

    taskFormCard.style.display = 'block';

    document.getElementById('formTitle').textContent = 'Sửa công việc';
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

    document.getElementById('formTitle').textContent = 'Thêm công việc';
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
            url = `/api/v1/projects/${projectId}/work-items/${selectedWorkItemId}/tasks/${editingTaskId}`;
            method = 'PATCH';
        } else {
            url = `/api/v1/projects/${projectId}/work-items/${selectedWorkItemId}/tasks`;
            method = 'POST';
        }

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
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
                (editingTaskId
                    ? 'Không thể sửa công việc.'
                    : 'Không thể thêm công việc.')
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
                data.message || 'Không thể xóa công việc.'
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