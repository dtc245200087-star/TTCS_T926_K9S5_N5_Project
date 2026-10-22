import React, { useCallback, useEffect, useState } from "react";
import { CalendarDays, FolderPlus, Link2, Plus, Trash2, Unlink, X } from "lucide-react";
import { apiFetch } from "../api.js";

const API = "/api";
const RELATIONSHIP_LABELS = {
  FS: "FS — kết thúc → bắt đầu",
  SS: "SS — bắt đầu → bắt đầu",
  FF: "FF — kết thúc → kết thúc",
  SF: "SF — bắt đầu → kết thúc",
};

function flattenCategories(categories, result = []) {
  for (const category of categories) {
    result.push(category);
    flattenCategories(category.children, result);
  }
  return result;
}

export default function CategoryTree({ canManage }) {
  const [categories, setCategories] = useState([]);
  const [unassignedTasks, setUnassignedTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [categoryForm, setCategoryForm] = useState({ name: "", parent_id: "", planned_start_date: "" });

  const loadData = useCallback(async () => {
    setError("");
    try {
      const [categoryResponse, taskResponse] = await Promise.all([
        apiFetch(`${API}/categories`),
        apiFetch(`${API}/categories/unassigned-tasks`),
      ]);
      const [categoryData, taskData] = await Promise.all([
        categoryResponse.json(),
        taskResponse.json(),
      ]);
      if (!categoryResponse.ok) throw new Error(categoryData.message || "Không thể tải cây hạng mục.");
      if (!taskResponse.ok) throw new Error(taskData.message || "Không thể tải công việc chưa gán.");
      setCategories(categoryData);
      setUnassignedTasks(taskData);
    } catch (loadError) {
      setError(loadError.message || "Không thể kết nối máy chủ.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  async function createCategory(event) {
    event.preventDefault();
    setError("");
    try {
      const response = await apiFetch(`${API}/categories`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...categoryForm,
          parent_id: categoryForm.parent_id ? Number(categoryForm.parent_id) : null,
        }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể tạo hạng mục.");
      setCategoryForm({ name: "", parent_id: "", planned_start_date: "" });
      setShowCreate(false);
      await loadData();
    } catch (saveError) {
      setError(saveError.message || "Không thể kết nối máy chủ.");
    }
  }

  async function deleteCategory(category) {
    if (!window.confirm(`Xóa hạng mục "${category.name}"? Hãy gỡ hạng mục con trước.`)) return;
    setError("");
    try {
      const response = await apiFetch(`${API}/categories/${category.id}`, { method: "DELETE" });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể xóa hạng mục.");
      await loadData();
    } catch (deleteError) {
      setError(deleteError.message || "Không thể kết nối máy chủ.");
    }
  }

  const allCategories = flattenCategories(categories);
  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Cây hạng mục</h1>
          <p>Gán công việc, thiết lập quan hệ phụ thuộc và theo dõi mốc bàn giao.</p>
        </div>
        {canManage && <button className="btn btn-primary" onClick={() => setShowCreate(true)}><FolderPlus size={16}/> Thêm hạng mục</button>}
      </div>
      {error && <div className="alert" role="alert">{error}</div>}
      {loading ? <div className="loading">Đang tải cây hạng mục...</div> :
        categories.length === 0 ? (
          <section className="panel empty category-empty">
            <FolderPlus size={30}/>
            <h2>Chưa có hạng mục</h2>
            <p>{canManage ? "Tạo hạng mục đầu tiên để bắt đầu theo dõi công việc và mốc bàn giao." : "Ban quản lý chưa tạo hạng mục nào."}</p>
          </section>
        ) : (
          <div className="category-tree">
            {categories.map(category => (
              <CategoryNode
                key={category.id}
                category={category}
                canManage={canManage}
                unassignedTasks={unassignedTasks}
                allCategories={allCategories}
                onSetMilestone={setSelectedCategory}
                onDelete={deleteCategory}
                onRefresh={loadData}
              />
            ))}
          </div>
        )}

      {showCreate && <div className="modal-bg" onMouseDown={event => {
        if (event.target === event.currentTarget) setShowCreate(false);
      }}>
        <form className="modal milestone-form" onSubmit={createCategory} aria-labelledby="category-create-title">
          <div className="modal-head">
            <h2 id="category-create-title">Tạo hạng mục</h2>
            <button type="button" aria-label="Đóng" onClick={() => setShowCreate(false)}><X size={18}/></button>
          </div>
          <label>Tên hạng mục
            <input maxLength="120" required value={categoryForm.name} onChange={event => setCategoryForm({ ...categoryForm, name: event.target.value })}/>
          </label>
          <label>Hạng mục cha
            <select value={categoryForm.parent_id} onChange={event => setCategoryForm({ ...categoryForm, parent_id: event.target.value })}>
              <option value="">Không có (hạng mục gốc)</option>
              {allCategories.map(parent => <option value={parent.id} key={parent.id}>{parent.name}</option>)}
            </select>
          </label>
          <label>Ngày bắt đầu kế hoạch
            <input type="date" required value={categoryForm.planned_start_date} onChange={event => setCategoryForm({ ...categoryForm, planned_start_date: event.target.value })}/>
          </label>
          {error && <div className="alert" role="alert">{error}</div>}
          <div className="milestone-form-actions">
            <button className="btn btn-primary">Tạo hạng mục</button>
            <button className="btn" type="button" onClick={() => setShowCreate(false)}>Hủy</button>
          </div>
        </form>
      </div>}

      {selectedCategory && <MilestoneFormModal
        category={selectedCategory}
        onClose={() => setSelectedCategory(null)}
        onSaved={loadData}
      />}
    </div>
  );
}

function CategoryNode({ category, canManage, unassignedTasks, allCategories, onSetMilestone, onDelete, onRefresh }) {
  const [selectedTask, setSelectedTask] = useState("");
  const [taskId, setTaskId] = useState("");
  const [predecessorId, setPredecessorId] = useState("");
  const [relationshipType, setRelationshipType] = useState("FS");
  const [error, setError] = useState("");
  const categoryTasks = category.tasks || [];

  async function assignTask(event) {
    event.preventDefault();
    setError("");
    try {
      const response = await apiFetch(`${API}/categories/${category.id}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: Number(selectedTask) }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể gán công việc.");
      setSelectedTask("");
      await onRefresh();
    } catch (saveError) {
      setError(saveError.message || "Không thể kết nối máy chủ.");
    }
  }

  async function addDependency(event) {
    event.preventDefault();
    setError("");
    try {
      const response = await apiFetch(`${API}/categories/${category.id}/dependencies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_id: Number(taskId),
          depends_on_task_id: Number(predecessorId),
          relationship_type: relationshipType,
        }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể thêm quan hệ phụ thuộc.");
      setTaskId("");
      setPredecessorId("");
      setRelationshipType("FS");
      await onRefresh();
    } catch (saveError) {
      setError(saveError.message || "Không thể kết nối máy chủ.");
    }
  }

  async function removeDependency(dependency) {
    setError("");
    try {
      const response = await apiFetch(
        `${API}/categories/${category.id}/dependencies/${dependency.task_id}/${dependency.depends_on_task_id}`,
        { method: "DELETE" },
      );
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể xóa quan hệ phụ thuộc.");
      await onRefresh();
    } catch (removeError) {
      setError(removeError.message || "Không thể kết nối máy chủ.");
    }
  }

  async function unassignTask(task) {
    setError("");
    try {
      const response = await apiFetch(`${API}/categories/tasks/${task.id}`, { method: "DELETE" });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể gỡ công việc.");
      await onRefresh();
    } catch (removeError) {
      setError(removeError.message || "Không thể kết nối máy chủ.");
    }
  }

  const taskNames = Object.fromEntries(categoryTasks.map(task => [task.id, task.task_name]));
  return (
    <section className="category-node">
      <div className="category-node-head">
        <div>
          <h2>{category.name}</h2>
          <p><CalendarDays size={13}/> Bắt đầu kế hoạch {category.planned_start_date}</p>
        </div>
        <div className="category-actions">
          {category.milestone && <span className="category-deadline">Bàn giao: {category.milestone.deadline}</span>}
          {canManage && <button className="btn btn-primary" onClick={() => onSetMilestone(category)}>
            {category.milestone ? "Sửa mốc bàn giao" : "Đặt mốc bàn giao"}
          </button>}
          {canManage && <button className="icon-action danger" aria-label={`Xóa ${category.name}`} onClick={() => onDelete(category)}><Trash2 size={16}/></button>}
        </div>
      </div>

      {error && <div className="alert" role="alert">{error}</div>}
      <div className="category-task-list">
        {categoryTasks.length ? categoryTasks.map(task => (
          <div className="category-task-row" key={task.id}>
            <span>{task.task_name}</span>
            <small>ES {task.es ?? "—"} · EF {task.ef ?? "—"}</small>
            {canManage && <button className="icon-action" aria-label={`Gỡ ${task.task_name}`} onClick={() => unassignTask(task)}><Unlink size={15}/></button>}
          </div>
        )) : <p className="muted">Chưa có công việc được gán trực tiếp.</p>}
      </div>

      {canManage && <div className="category-management">
        <form className="category-inline-form" onSubmit={assignTask}>
          <label>Gán công việc
            <select required value={selectedTask} onChange={event => setSelectedTask(event.target.value)}>
              <option value="">Chọn công việc chưa gán</option>
              {unassignedTasks.map(task => <option key={task.id} value={task.id}>{task.task_name}</option>)}
            </select>
          </label>
          <button className="btn btn-primary" disabled={!selectedTask}><Plus size={14}/> Gán</button>
        </form>
        {categoryTasks.length > 1 && <form className="category-inline-form dependency-form" onSubmit={addDependency}>
          <label>Công việc
            <select required value={taskId} onChange={event => setTaskId(event.target.value)}>
              <option value="">Chọn công việc</option>
              {categoryTasks.map(task => <option value={task.id} key={task.id}>{task.task_name}</option>)}
            </select>
          </label>
          <label>Phụ thuộc vào
            <select required value={predecessorId} onChange={event => setPredecessorId(event.target.value)}>
              <option value="">Chọn công việc trước</option>
              {categoryTasks.filter(task => String(task.id) !== taskId).map(task => <option value={task.id} key={task.id}>{task.task_name}</option>)}
            </select>
          </label>
          <label>Loại quan hệ
            <select value={relationshipType} onChange={event => setRelationshipType(event.target.value)}>
              {Object.entries(RELATIONSHIP_LABELS).map(([type, label]) => (
                <option value={type} key={type}>{label}</option>
              ))}
            </select>
          </label>
          <button className="btn btn-primary" disabled={!taskId || !predecessorId}><Link2 size={14}/> Tạo liên kết</button>
        </form>}
        {category.dependencies?.length > 0 && <ul className="dependency-list">
          {category.dependencies.map(dependency => (
            <li key={`${dependency.task_id}-${dependency.depends_on_task_id}`}>
              <span>
                {taskNames[dependency.depends_on_task_id]} → {taskNames[dependency.task_id]}
                {" "}({RELATIONSHIP_LABELS[dependency.relationship_type] || dependency.relationship_type})
              </span>
              <button className="icon-action" aria-label="Xóa quan hệ phụ thuộc" onClick={() => removeDependency(dependency)}><X size={14}/></button>
            </li>
          ))}
        </ul>}
      </div>}

      {category.children?.length > 0 && <div className="category-children">
        {category.children.map(child => (
          <CategoryNode
            key={child.id}
            category={child}
            canManage={canManage}
            unassignedTasks={unassignedTasks}
            allCategories={allCategories}
            onSetMilestone={onSetMilestone}
            onDelete={onDelete}
            onRefresh={onRefresh}
          />
        ))}
      </div>}
    </section>
  );
}

function MilestoneFormModal({ category, onClose, onSaved }) {
  const [deadline, setDeadline] = useState(category.milestone?.deadline || "");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function save(event) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      const existing = category.milestone;
      const response = await apiFetch(
        existing ? `${API}/milestones/${existing.id}` : `${API}/milestones`,
        {
          method: existing ? "PATCH" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(existing ? { deadline } : { category_id: category.id, deadline }),
        },
      );
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể lưu mốc bàn giao.");
      await onSaved();
      onClose();
    } catch (saveError) {
      setError(saveError.message || "Không thể kết nối máy chủ.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal-bg" onMouseDown={event => {
      if (event.target === event.currentTarget && !saving) onClose();
    }}>
      <form className="modal milestone-form" onSubmit={save} aria-labelledby="milestone-form-title">
        <div className="modal-head">
          <div><h2 id="milestone-form-title">{category.milestone ? "Cập nhật mốc bàn giao" : "Đặt mốc bàn giao"}</h2><p>{category.name}</p></div>
          <button type="button" aria-label="Đóng" disabled={saving} onClick={onClose}><X size={18}/></button>
        </div>
        <label>Ngày bắt buộc bàn giao
          <input type="date" required value={deadline} onChange={event => setDeadline(event.target.value)}/>
        </label>
        {error && <div className="alert" role="alert">{error}</div>}
        <div className="milestone-form-actions">
          <button className="btn btn-primary" disabled={saving}>{saving ? "Đang lưu..." : "Lưu mốc"}</button>
          {category.milestone && <button className="btn btn-danger" type="button" disabled={saving} onClick={async () => {
            setError("");
            setSaving(true);
            try {
              const response = await apiFetch(`${API}/milestones/${category.milestone.id}`, { method: "DELETE" });
              const result = await response.json();
              if (!response.ok) throw new Error(result.message || "Không thể xóa mốc bàn giao.");
              await onSaved();
              onClose();
            } catch (deleteError) {
              setError(deleteError.message || "Không thể kết nối máy chủ.");
            } finally {
              setSaving(false);
            }
          }}>Xóa mốc</button>}
          <button className="btn" type="button" disabled={saving} onClick={onClose}>Hủy</button>
        </div>
      </form>
    </div>
  );
}
