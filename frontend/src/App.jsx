import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  LayoutDashboard, Building2, ClipboardList, Users, Package,
  Truck, BookOpen, BarChart3, Settings, Bell, Search,
  Plus, MapPin, CalendarDays, CheckCircle2, Clock3, AlertTriangle,
  Menu, X, TrendingUp, UploadCloud, RotateCw
} from "lucide-react";
import { apiFetch } from "./api.js";
import { useSyncQueue } from "./hooks/useSyncQueue.js";
import SyncStatusWidget from "./components/SyncStatusWidget.jsx";
import GanttChart from "./components/GanttChart";
import CategoryTree from "./components/CategoryTree.jsx";
import MilestoneAlerts from "./components/MilestoneAlerts.jsx";
import { sortTasksByDependencies } from "./dependencies.js";
import "./milestone.css";
import "./task-progress.css";
import S06DependencyPage from "./components/S06DependencyPage.jsx";
import { useDiaryImageUploadQueue } from "./hooks/useDiaryImageUploadQueue.js";
import DiaryImageUploadStatus from "./components/DiaryImageUploadStatus.jsx";
import DiaryConflictModal from "./components/DiaryConflictModal.jsx";

const API = "/api";
const ROLE_NAMES = { admin: "Quản trị viên", manager: "Quản lý công trình", engineer: "Kỹ sư", viewer: "Chỉ xem" };

function flattenCategoryTree(categories, result = []) {
  for (const category of categories) {
    result.push(category);
    flattenCategoryTree(category.children || [], result);
  }
  return result;
}

const menu = [
  ["Tổng quan", LayoutDashboard],
  ["Công trình", Building2],
  ["Hạng mục", ClipboardList],
  ["Mốc bàn giao", CalendarDays],
  ["Công việc", ClipboardList],
  ["Quan hệ phụ thuộc (S-06)", ClipboardList],
  ["Tiến độ và đường găng", TrendingUp],
  ["Nhân sự", Users],
  ["Vật tư", Package],
  ["Thiết bị", Truck],
  ["Nhật ký thi công", BookOpen],
  ["Báo cáo", BarChart3],
  ["Cài đặt", Settings],
];

function blobFromCanvas(canvas, quality) {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      blob => blob ? resolve(blob) : reject(new Error("Không thể tạo ảnh đã nén.")),
      "image/jpeg",
      quality,
    );
  });
}

async function compressDiaryImage(file) {
  const bitmap = await createImageBitmap(file);
  let scale = Math.min(1, 2560 / Math.max(bitmap.width, bitmap.height));
  let compressedBlob;

  for (let attempt = 0; attempt < 12; attempt += 1) {
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(bitmap.width * scale));
    canvas.height = Math.max(1, Math.round(bitmap.height * scale));
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Trình duyệt không hỗ trợ xử lý ảnh.");
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    compressedBlob = await blobFromCanvas(canvas, Math.max(0.5, 0.86 - attempt * 0.06));
    if (compressedBlob.size < 1024 * 1024) break;
    scale *= 0.82;
  }
  bitmap.close();
  if (!compressedBlob || compressedBlob.size >= 1024 * 1024) {
    throw new Error("Không thể nén ảnh xuống dưới 1 MB.");
  }

  const compressedBitmap = await createImageBitmap(compressedBlob);
  const thumbnailScale = Math.min(1, 360 / Math.max(compressedBitmap.width, compressedBitmap.height));
  const thumbnailCanvas = document.createElement("canvas");
  thumbnailCanvas.width = Math.max(1, Math.round(compressedBitmap.width * thumbnailScale));
  thumbnailCanvas.height = Math.max(1, Math.round(compressedBitmap.height * thumbnailScale));
  const thumbnailContext = thumbnailCanvas.getContext("2d");
  if (!thumbnailContext) throw new Error("Không thể tạo ảnh xem trước.");
  thumbnailContext.drawImage(compressedBitmap, 0, 0, thumbnailCanvas.width, thumbnailCanvas.height);
  compressedBitmap.close();
  const thumbnailBlob = await blobFromCanvas(thumbnailCanvas, 0.72);
  if (thumbnailBlob.size > 150 * 1024) {
    throw new Error("Không thể tối ưu ảnh xem trước.");
  }
  return {compressedBlob, thumbnailBlob};
}

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function App({ user, onLogout, onPasswordChanged }) {
  const syncQueue = useSyncQueue();
  const mockDiaryImageUrls = useRef(new Set());
  const handleDiaryImageUploaded = useCallback((job, uploadedImage) => {
    if (uploadedImage.url) mockDiaryImageUrls.current.add(uploadedImage.url);
    window.dispatchEvent(new CustomEvent("diary-image-uploaded", {
      detail: {entryId: job.entryId, image: uploadedImage},
    }));
  }, []);
  const imageUploadQueue = useDiaryImageUploadQueue(handleDiaryImageUploaded);
  const [page, setPage] = useState("Tổng quan");
  const [mobile, setMobile] = useState(false);
  const [data, setData] = useState(null);
  const [taskData, setTaskData] = useState([]);
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [scheduleData, setScheduleData] = useState({ schedule_results: [], has_cycle: false, message: "" });
  const [baseline, setBaseline] = useState(null);
  const [baselineLoading, setBaselineLoading] = useState(false);
  const [baselineError, setBaselineError] = useState(null);
  const [baselineSaving, setBaselineSaving] = useState(false);
  const [baselineSuccess, setBaselineSuccess] = useState(false);
  const baselineSuccessTimer = useRef(null);
  const [tasksError, setTasksError] = useState("");
  const [selectedTask, setSelectedTask] = useState(null);
  const [progressForm, setProgressForm] = useState(null);
  const [progressError, setProgressError] = useState("");
  const [savingProgress, setSavingProgress] = useState(false);
  const canUpdateProgress = ["admin", "manager", "engineer"].includes(user.role);

  useEffect(() => {
    imageUploadQueue.resolveWaitingEntries(syncQueue.items);
  }, [syncQueue.items, imageUploadQueue.resolveWaitingEntries]);

  const loadDashboard = () =>
    apiFetch(`${API}/dashboard`).then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(setData).catch(() => setData(null));

  useEffect(() => { loadDashboard(); }, []);

  useEffect(() => () => window.clearTimeout(baselineSuccessTimer.current), []);

  useEffect(() => () => {
    for (const url of mockDiaryImageUrls.current) URL.revokeObjectURL(url);
  }, []);

  useEffect(() => {
    if (page !== "Công việc" && page !== "Tiến độ và đường găng") return;
    const loadSchedule = page === "Tiến độ và đường găng";
    let active = true;
    setTasksError("");
    if (loadSchedule) {
      setBaselineLoading(true);
      setBaselineError(null);
      apiFetch(`${API}/schedule-baseline`)
        .then(async response => {
          const result = await response.json();
          if (!response.ok) throw new Error(result.message || "Không thể tải kế hoạch gốc.");
          return result.baseline;
        })
        .then(result => { if (active) setBaseline(result); })
        .catch(error => { if (active) setBaselineError(error.message || "Không thể tải kế hoạch gốc."); })
        .finally(() => { if (active) setBaselineLoading(false); });
    }
    apiFetch(`${API}/${loadSchedule ? "schedule-results" : "cong-viec"}`)
      .then(response => {
        if (!response.ok) throw new Error("Không thể tải danh sách công việc.");
        return response.json();
      })
      .then(result => {
        if (!active) return;
        if (loadSchedule) {
          setTaskData(result.tasks);
          setScheduleData(result);
        } else {
          setTaskData(result);
        }
      })
      .catch(error => { if (active) setTasksError(error.message); });
    return () => { active = false; };
  }, [page]);

  function openProgressForm(task) {
    setSelectedTask(task);
    setProgressForm({
      ngay_bat_dau_thuc_te: task.ngay_bat_dau_thuc_te || "",
      ngay_ket_thuc_thuc_te: task.ngay_ket_thuc_thuc_te || "",
      phan_tram_hoan_thanh: String(task.phan_tram_hoan_thanh ?? 0),
      category_id: task.category_id == null ? "" : String(task.category_id),
    });
    setProgressError("");
  }

  async function saveProgress(event) {
    event.preventDefault();
    setProgressError("");
    if (
      progressForm.ngay_bat_dau_thuc_te &&
      progressForm.ngay_ket_thuc_thuc_te &&
      progressForm.ngay_ket_thuc_thuc_te < progressForm.ngay_bat_dau_thuc_te
    ) {
      setProgressError("Ngày kết thúc thực tế không được trước ngày bắt đầu thực tế.");
      return;
    }
    const completion = Number(progressForm.phan_tram_hoan_thanh);
    if (!Number.isInteger(completion) || completion < 0 || completion > 100) {
      setProgressError("Phần trăm hoàn thành phải là số nguyên từ 0 đến 100.");
      return;
    }

    setSavingProgress(true);
    try {
      const response = await apiFetch(`${API}/cong-viec/${selectedTask.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ngay_bat_dau_thuc_te: progressForm.ngay_bat_dau_thuc_te || null,
          ngay_ket_thuc_thuc_te: progressForm.ngay_ket_thuc_thuc_te || null,
          phan_tram_hoan_thanh: completion,
          ...(canManageCategories
            ? { category_id: progressForm.category_id ? Number(progressForm.category_id) : null }
            : {}),
        }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể cập nhật tiến độ.");
      setTaskData(current => current.map(task => task.id === result.id ? result : task));
      setSelectedTask(null);
      setProgressForm(null);
    } catch (error) {
      setProgressError(error.message || "Không thể kết nối máy chủ.");
    } finally {
      setSavingProgress(false);
    }
  }

  const canManageCategories = ["admin", "manager"].includes(user.role);
  const canManageBaseline = user.role === "admin" || user.role === "manager";

  async function captureScheduleBaseline() {
    setBaselineSaving(true);
    setBaselineError(null);
    setBaselineSuccess(false);
    window.clearTimeout(baselineSuccessTimer.current);
    try {
      const response = await apiFetch(`${API}/schedule-baseline`, { method: "POST" });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể chốt kế hoạch gốc.");

      setBaselineLoading(true);
      const reloadResponse = await apiFetch(`${API}/schedule-baseline`);
      const reloaded = await reloadResponse.json();
      if (!reloadResponse.ok) {
        throw new Error(reloaded.message || "Đã chốt nhưng không thể tải lại kế hoạch gốc.");
      }
      setBaseline(reloaded.baseline);
      setBaselineSuccess(true);
      baselineSuccessTimer.current = window.setTimeout(() => setBaselineSuccess(false), 2000);
    } catch (error) {
      setBaselineError(error.message || "Không thể kết nối máy chủ.");
    } finally {
      setBaselineLoading(false);
      setBaselineSaving(false);
    }
  }

  useEffect(() => {
    if (page !== "Công việc") return;
    let active = true;
    apiFetch(`${API}/categories`)
      .then(async response => {
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || "Không thể tải danh sách hạng mục.");
        if (active) setCategoryOptions(flattenCategoryTree(result));
      })
      .catch(error => {
        if (active) setTasksError(error.message || "Không thể tải danh sách hạng mục.");
      });
    return () => { active = false; };
  }, [page]);

  return (
    <div className="app">
      <aside className={mobile ? "sidebar open" : "sidebar"}>
        <div className="brand">
          <div className="brand-icon"><Building2 size={25}/></div>
          <div><b>ĐIỀU HÀNH</b><span>THI CÔNG</span></div>
          <button className="close-mobile" onClick={() => setMobile(false)}><X/></button>
        </div>
        <div className="menu-title">QUẢN LÝ HỆ THỐNG</div>
        <nav>
          {menu.map(([label, Icon]) => (
            <button key={label} className={page === label ? "nav active" : "nav"} onClick={() => {setPage(label); setMobile(false)}}>
              <Icon size={19}/><span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="user-mini"><div className="avatar">{user.full_name.slice(0, 2).toUpperCase()}</div><div><b>{user.full_name}</b><small>{ROLE_NAMES[user.role]}</small></div></div>
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <button className="mobile-menu" onClick={() => setMobile(true)}><Menu/></button>
          <div className="breadcrumb"><span>Hệ thống</span><b>/</b><strong>{page}</strong></div>
          <div className="header-actions">
            <div className="search"><Search size={18}/><input placeholder="Tìm kiếm..." /></div>
            <SyncStatusWidget {...syncQueue}/>
            <button className="icon-btn"><Bell size={19}/><i></i></button>
            <div className="avatar">{user.full_name.slice(0, 2).toUpperCase()}</div>
            <button className="logout-btn" onClick={onLogout}>Đăng xuất</button>
          </div>
        </header>

        {page === "Tổng quan" ? <Dashboard data={data}/> :
         page === "Công trình" ? <Projects data={data?.cong_trinh_data || []} refresh={loadDashboard} canManage={["admin", "manager"].includes(user.role)}/> :
         page === "Hạng mục" ? <CategoryTree canManage={["admin", "manager"].includes(user.role)}/> :
         page === "Mốc bàn giao" ? <MilestoneAlerts/> :
         page === "Tiến độ và đường găng" ? <SchedulePage tasks={taskData} scheduleResults={scheduleData.schedule_results} hasCycle={scheduleData.has_cycle} scheduleMessage={scheduleData.message} canUpdate={canUpdateProgress} onOpenProgress={openProgressForm} error={tasksError} baseline={baseline} baselineLoading={baselineLoading} baselineError={baselineError} baselineSaving={baselineSaving} baselineSuccess={baselineSuccess} canManageBaseline={canManageBaseline} onCaptureBaseline={captureScheduleBaseline}/> :
         page === "Công việc" ? <Tasks data={taskData} canUpdate={canUpdateProgress} onOpenProgress={openProgressForm} error={tasksError}/> :
         page === "Quan hệ phụ thuộc (S-06)" ? <S06DependencyPage/> :
         page === "Nhân sự" ? <SimpleTable title="Danh sách nhân sự" endpoint="/nhan-su" columns={["ho_ten","vai_tro","cong_trinh","trang_thai"]} headers={["Họ tên","Vai trò","Công trình","Trạng thái"]}/> :
         page === "Vật tư" ? <Materials/> :
         page === "Nhật ký thi công" ? <Diary canWrite={["admin", "manager", "engineer"].includes(user.role)} enqueueItems={syncQueue.enqueueItems} imageUploadQueue={imageUploadQueue}/> :
         page === "Cài đặt" ? <SettingsPage user={user} onPasswordChanged={onPasswordChanged}/> :
         <Placeholder title={page}/>}
        {selectedTask && progressForm && <ProgressFormModal
          task={selectedTask}
          form={progressForm}
          setForm={setProgressForm}
          error={progressError}
          saving={savingProgress}
          categories={categoryOptions}
          canAssignCategory={canUpdateProgress}
          onSave={saveProgress}
          onClose={() => setSelectedTask(null)}
        />}
      </main>
    </div>
  );
}

function Dashboard({data}) {
  if (!data) return <div className="content"><div className="loading">Đang kết nối máy chủ...</div></div>;
  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Tổng quan điều hành</h1>
          <p>Theo dõi tình hình thi công công trình trong thời gian thực.</p>
        </div>
        <button className="primary"><Plus size={18}/> Tạo mới</button>
      </div>
      <div className="cards">
        <Stat title="Tổng công trình" value={data.cong_trinh} icon={<Building2/>} note="Đang quản lý"/>
        <Stat title="Đang thi công" value={data.dang_thi_cong} icon={<Clock3/>} note="Cập nhật hôm nay"/>
        <Stat title="Nhân sự" value={data.nhan_su} icon={<Users/>} note="Đang làm việc"/>
        <Stat title="Cảnh báo vật tư" value={data.vat_tu_canh_bao} icon={<AlertTriangle/>} note="Cần kiểm tra"/>
      </div>
      <div className="grid-2">
        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Tiến độ công trình</h2>
              <p>Tiến độ cập nhật theo từng công trình</p>
            </div>
            <button className="text-btn">Xem tất cả</button>
          </div>
          <div className="progress-list">
            {data.cong_trinh_data && data.cong_trinh_data.map(x => (
              <div className="progress-row" key={x.id}>
                <div className="progress-info"><b>{x.ten}</b><span>{x.tien_do}%</span></div>
                <div className="bar"><i style={{width:`${x.tien_do}%`}}></i></div>
                <small><MapPin size={13}/> {x.dia_diem}</small>
              </div>
            ))}
          </div>
        </section>
        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Công việc cần xử lý</h2>
              <p>Các nhiệm vụ đang theo dõi</p>
            </div>
            <button className="text-btn">Xem tất cả</button>
          </div>
          <div className="task-list">
            {data.cong_viec_hom_nay && data.cong_viec_hom_nay.map(x => (
              <div className="task" key={x.id}>
                <div className="task-icon"><ClipboardList size={17}/></div>
                <div className="task-main"><b>{x.ten}</b><small>{x.nguoi_phu_trach} · {x.han}</small></div>
                <Status value={x.trang_thai}/>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

function Stat({title, value, icon, note}) {
  return (
    <div className="stat">
      <div className="stat-top">
        <div><p>{title}</p><strong>{value}</strong></div>
        <div className="stat-icon">{icon}</div>
      </div>
      <small>{note}</small>
    </div>
  );
}

function Status({value}) {
  if (!value) return null;
  return (
    <span className={`status ${value.includes("Hoàn") ? "done" : value.includes("Chờ") ? "wait" : "doing"}`}>
      {value}
    </span>
  );
}

function Projects({data, refresh, canManage}) {
  const [show, setShow] = useState(false);
  const [form, setForm] = useState({ten:"", dia_diem:"", tien_do:0});

  async function add() {
    const response = await apiFetch(`${API}/cong-trinh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });
    if (!response.ok) return;
    setShow(false);
    setForm({ten:"", dia_diem:"", tien_do:0});
    refresh();
  }

  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Quản lý công trình</h1>
          <p>Danh sách và tiến độ các công trình đang quản lý.</p>
        </div>
        {canManage && <button className="btn btn-primary" onClick={() => setShow(true)}>+ Thêm công trình</button>}
      </div>

      <div className="project-grid">
        {data && data.map(x => (
          <div key={x.id || x.ten} className="project-card">
            <div className="project-top">
              <h3>{x.ten}</h3>
            </div>
            <p>📍 {x.dia_diem}</p>
            <p>📊 Tiến độ: {x.tien_do}%</p>
          </div>
        ))}
      </div>

      {show && (
        <div className="modal-bg">
          <div className="modal">
            <div className="modal-head">
              <h2>Thêm công trình</h2>
              <button onClick={() => setShow(false)}>✕</button>
            </div>
            <input 
              placeholder="Tên công trình" 
              value={form.ten} 
              onChange={e => setForm({...form, ten: e.target.value})} 
            />
            <input 
              placeholder="Địa điểm" 
              value={form.dia_diem} 
              onChange={e => setForm({...form, dia_diem: e.target.value})} 
            />
            <input 
              type="number" 
              placeholder="Tiến độ (%)" 
              value={form.tien_do} 
              onChange={e => setForm({...form, tien_do: Number(e.target.value)})} 
            />
            <div style={{ display: 'flex', gap: 10, marginTop: 15 }}>
              <button className="btn btn-primary" onClick={add}>Lưu</button>
              <button className="btn" onClick={() => setShow(false)}>Hủy</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Tasks({data, canUpdate, onOpenProgress, error}) {
  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Quản lý công việc</h1>
          <p>Theo dõi kế hoạch và cập nhật riêng ngày, phần trăm hoàn thành thực tế.</p>
        </div>
      </div>
      {error && <div className="alert" role="alert">{error}</div>}
      <section className="panel table-panel">
        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>Công việc</th><th>Công trình</th><th>Người phụ trách</th>
              <th>Trạng thái kế hoạch</th><th>Hạn kế hoạch</th>
              <th>Bắt đầu thực tế</th><th>Kết thúc thực tế</th>
              <th>Hoàn thành thực tế</th>{canUpdate && <th>Thao tác</th>}
            </tr></thead>
            <tbody>
              {data.map(task => <tr key={task.id}>
                <td>{task.ten}</td><td>{task.cong_trinh}</td><td>{task.nguoi_phu_trach}</td>
                <td><Status value={task.trang_thai}/></td><td>{task.han || "—"}</td>
                <td>{task.ngay_bat_dau_thuc_te || "—"}</td>
                <td>{task.ngay_ket_thuc_thuc_te || "—"}</td>
                <td><div className="actual-progress">
                  <div className="bar"><i style={{ width: `${task.phan_tram_hoan_thanh}%` }}/></div>
                  <span>{task.phan_tram_hoan_thanh}%</span>
                </div></td>
                {canUpdate && <td><button className="btn btn-primary" onClick={() => onOpenProgress(task)}>Cập nhật</button></td>}
              </tr>)}
              {!data.length && <tr><td colSpan={canUpdate ? 9 : 8}>Chưa có công việc.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

    </div>
  );
}

function ProgressFormModal({task, form, setForm, error, saving, categories, canAssignCategory, onSave, onClose}) {
  return (
    <div className="modal-bg" onMouseDown={event => {
      if (event.target === event.currentTarget && !saving) onClose();
    }}>
      <form className="modal progress-modal" onSubmit={onSave} aria-labelledby="progress-modal-title">
        <div className="modal-head">
          <div><h2 id="progress-modal-title">Cập nhật tiến độ thực tế</h2><p>{task.ten}</p></div>
          <button type="button" aria-label="Đóng" disabled={saving} onClick={onClose}>✕</button>
        </div>
        <p className="progress-plan-note">Kế hoạch: hạn {task.han || "chưa có"} · trạng thái {task.trang_thai}. Cập nhật này không thay đổi kế hoạch.</p>
        {canAssignCategory && <label>Hạng mục
          <select value={form.category_id} onChange={event => setForm({ ...form, category_id: event.target.value })}>
            <option value="">Không gán hạng mục</option>
            {categories.map(category => <option value={category.id} key={category.id}>{category.name}</option>)}
          </select>
        </label>}
        <label>Ngày bắt đầu thực tế
          <input type="date" value={form.ngay_bat_dau_thuc_te} onChange={event => setForm({ ...form, ngay_bat_dau_thuc_te: event.target.value })}/>
        </label>
        <label>Ngày kết thúc thực tế
          <input type="date" min={form.ngay_bat_dau_thuc_te || undefined} value={form.ngay_ket_thuc_thuc_te} onChange={event => setForm({ ...form, ngay_ket_thuc_thuc_te: event.target.value })}/>
        </label>
        <label>Hoàn thành thực tế (%)
          <input type="number" min="0" max="100" step="1" required value={form.phan_tram_hoan_thanh} onChange={event => setForm({ ...form, phan_tram_hoan_thanh: event.target.value })}/>
        </label>
        {error && <div className="alert" role="alert">{error}</div>}
        <div className="progress-form-actions">
          <button className="btn btn-primary" disabled={saving}>{saving ? "Đang lưu…" : "Lưu tiến độ"}</button>
          <button className="btn" type="button" disabled={saving} onClick={onClose}>Hủy</button>
        </div>
      </form>
    </div>
  );
}

function Materials() {
  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Quản lý vật tư</h1>
          <p>Theo dõi nhập, xuất và tồn kho vật tư.</p>
        </div>
        <button className="primary"><Plus size={18}/> Nhập vật tư</button>
      </div>
      <SimpleTable title="" endpoint="/vat-tu" columns={["ten","don_vi","ton_kho","muc_toi_thieu"]} headers={["Vật tư","Đơn vị","Tồn kho","Mức tối thiểu"]}/>
    </div>
  );
}

function Diary({canWrite, enqueueItems, imageUploadQueue}) {
  const today = new Date().toLocaleDateString("en-CA");
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [project, setProject] = useState("");
  const [diaryDate, setDiaryDate] = useState(today);
  const [taskFilter, setTaskFilter] = useState("");
  const [entries, setEntries] = useState([]);
  const [summary, setSummary] = useState({nhan_luc_so_nguoi: "", nhan_luc_ghi_chu: "", thiet_bi: "", thoi_tiet: "", ghi_chu_thoi_tiet: ""});
  const [form, setForm] = useState({cong_viec_id: "", gio: new Date().toTimeString().slice(0, 5), noi_dung: ""});
  const [selectedImages, setSelectedImages] = useState([]);
  const [pendingImageCompressions, setPendingImageCompressions] = useState(0);
  const [imageNote, setImageNote] = useState("");
  const [isDraggingImages, setIsDraggingImages] = useState(false);
  const [lightbox, setLightbox] = useState(null);
  const previewUrls = useRef(new Set());
  const pendingImageCompressionCount = useRef(0);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  const [sampleConflict, setSampleConflict] = useState(null);
  const [conflictNotice, setConflictNotice] = useState("");

  useEffect(() => () => {
    for (const url of previewUrls.current) URL.revokeObjectURL(url);
  }, []);

  useEffect(() => {
    const handleUploadedImage = event => {
      const {entryId, image} = event.detail;
      setEntries(current => current.map(entry => entry.id === entryId
        ? {
          ...entry,
          images: [
            ...(entry.images || []).filter(item => item.id !== image.id),
            image,
          ],
        }
        : entry
      ));
    };
    window.addEventListener("diary-image-uploaded", handleUploadedImage);
    return () => window.removeEventListener("diary-image-uploaded", handleUploadedImage);
  }, []);

  function releasePreview(url) {
    if (!url) return;
    URL.revokeObjectURL(url);
    previewUrls.current.delete(url);
  }

  async function prepareImage(image) {
    if (image.compressedBlob && image.thumbnailBlob) return image;
    setSelectedImages(current => current.map(item =>
      item.id === image.id ? {...item, status: "processing", error: ""} : item
    ));
    try {
      const {compressedBlob, thumbnailBlob} = await compressDiaryImage(image.file);
      const preview = URL.createObjectURL(thumbnailBlob);
      previewUrls.current.add(preview);
      releasePreview(image.preview);
      const prepared = {...image, compressedBlob, thumbnailBlob, preview, status: "ready", error: ""};
      setSelectedImages(current => current.map(item => item.id === image.id ? prepared : item));
      return prepared;
    } catch (compressionError) {
      setSelectedImages(current => current.map(item =>
        item.id === image.id
          ? {...item, status: "error", error: compressionError.message || "Không thể nén ảnh."}
          : item
      ));
      return null;
    }
  }

  async function retryImage(image) {
    await prepareImage(image);
  }

  function openLightbox(url, alt) {
    setLightbox({url, alt});
  }

  function closeLightbox() {
    if (lightbox?.objectUrl) releasePreview(lightbox.objectUrl);
    setLightbox(null);
  }

  useEffect(() => {
    Promise.all([apiFetch(`${API}/cong-trinh`).then(r => r.json()), apiFetch(`${API}/cong-viec`).then(r => r.json())])
      .then(([projectList, taskList]) => {
        setProjects(projectList);
        setTasks(taskList);
        setProject(projectList[0]?.ten || "");
      })
      .catch(() => setError("Không tải được danh sách công trình và hạng mục."));
  }, []);

  const projectTasks = tasks.filter(task => task.cong_trinh === project);
  function openSampleConflict() {
    const base = {
      id: "sample-diary-32",
      cong_trinh: project || "Công trình mẫu",
      ngay: diaryDate,
      gio: "09:30",
      hang_muc: "Thi công móng khối A",
      noi_dung: "Đã hoàn thành công tác chuẩn bị mặt bằng.",
      thoi_tiet: "Nắng",
      ghi_chu_thoi_tiet: "",
    };
    setConflictNotice("");
    setSampleConflict({
      title: "Mẫu mô phỏng · Nhật ký thi công móng",
      base,
      versionA: {
        ...base,
        noi_dung: "Đã hoàn thành chuẩn bị mặt bằng và lắp dựng cốp pha móng.",
      },
      versionB: {
        ...base,
        thoi_tiet: "Nhiều mây",
        ghi_chu_thoi_tiet: "Có mưa nhẹ vào cuối buổi sáng.",
        noi_dung: "Đã hoàn thành chuẩn bị mặt bằng và kiểm tra cao độ.",
      },
    });
  }

  function finishSampleConflict(resolvedVersion) {
    setSampleConflict(null);
    setConflictNotice(`Đã tạo phiên bản thống nhất trong bản xem thử: ${resolvedVersion.noi_dung}`);
  }
  const loadEntries = () => {
    if (!project || !diaryDate) return;
    const query = new URLSearchParams({cong_trinh: project, ngay: diaryDate});
    if (taskFilter) query.set("cong_viec_id", taskFilter);
    apiFetch(`${API}/nhat-ky?${query}`)
      .then(async response => {
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.message || "Không tải được nhật ký.");
        setEntries(payload);
      })
      .catch(e => setError(e.message));
  };
  useEffect(() => { loadEntries(); }, [project, diaryDate, taskFilter]);

  useEffect(() => {
    if (!project || !diaryDate) return;
    const query = new URLSearchParams({cong_trinh: project, ngay: diaryDate});
    apiFetch(`${API}/nhat-ky/thong-tin-ngay?${query}`)
      .then(async response => {
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.message || "Không tải được thông tin trong ngày.");
        setSummary(payload || {nhan_luc_so_nguoi: "", nhan_luc_ghi_chu: "", thiet_bi: "", thoi_tiet: "", ghi_chu_thoi_tiet: ""});
      })
      .catch(e => setError(e.message));
  }, [project, diaryDate]);

  async function saveEntry(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setSaving(true);
    const selectedAtSave = selectedImages;
    const imageNoteAtSave = imageNote.trim();
    const diaryPayload = {
      ...form,
      cong_trinh: project,
      ngay: diaryDate,
      cong_viec_id: Number(form.cong_viec_id),
    };
    try {
      const response = await apiFetch(`${API}/nhat-ky`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(diaryPayload),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.message || "Không thể lưu nhật ký.");
      setForm(current => ({...current, noi_dung: ""}));
      setEntries(current => [payload, ...current.filter(entry => entry.id !== payload.id)]);
      const imagesToUpload = selectedAtSave.filter(image => image.compressedBlob && image.thumbnailBlob);
      if (!imagesToUpload.length) {
        setNotice("Đã thêm mục nhật ký.");
        return;
      }
      try {
        await imageUploadQueue.enqueueImages(imagesToUpload.map(image => ({
          ...image,
          entryId: payload.id,
          note: imageNoteAtSave,
        })));
        const queuedIds = new Set(imagesToUpload.map(image => image.id));
        imagesToUpload.forEach(image => releasePreview(image.preview));
        setSelectedImages(current => current.filter(image => !queuedIds.has(image.id)));
        setImageNote("");
        setNotice(`Đã lưu nhật ký. ${imagesToUpload.length} ảnh được đưa vào hàng đợi tải nền.`);
      } catch (queueError) {
        setError(`Đã lưu nhật ký, nhưng không thể lưu ảnh vào hàng đợi: ${queueError.message}`);
      }
    } catch (e) {
      const networkFailure = !navigator.onLine || e instanceof TypeError || e.name === "AbortError";
      if (networkFailure) {
        const diaryQueueId = `sync-diary-${crypto.randomUUID()}`;
        const queuedItems = [{
          id: diaryQueueId,
          type: "diary",
          title: `Nhật ký ${project} - ${diaryDate}`,
          payload: diaryPayload,
        }];
        try {
          await enqueueItems(queuedItems);
          setForm(current => ({...current, noi_dung: ""}));
          setImageNote("");
          const imagesToWait = selectedAtSave.filter(image => image.compressedBlob && image.thumbnailBlob);
          const imageIdsToClear = new Set();
          let imageQueueNotice = "";
          if (imagesToWait.length) {
            try {
              await imageUploadQueue.enqueueImages(imagesToWait.map(image => ({
                ...image,
                entryId: null,
                diaryQueueId,
                note: imageNoteAtSave,
              })));
              imagesToWait.forEach(image => releasePreview(image.preview));
              imagesToWait.forEach(image => imageIdsToClear.add(image.id));
              imageQueueNotice = " Ảnh được giữ riêng trên thiết bị và chỉ tải được sau khi có ID nhật ký từ máy chủ.";
            } catch (imageQueueError) {
              imageQueueNotice = ` Không lưu được hàng đợi ảnh: ${imageQueueError.message}`;
            }
          }
          setSelectedImages(current => current.filter(image => !imageIdsToClear.has(image.id)));
          setNotice(`Nhật ký đã lưu trong hàng đợi S-31.${imageQueueNotice}`);
        } catch (queueError) {
          setError(queueError.message || "Không thể lưu nhật ký vào hàng đợi trên thiết bị.");
        }
      } else {
        setError(e.message);
      }
    } finally {
      setSaving(false);
    }
  }

  function addImages(fileList) {
    const incoming = Array.from(fileList);
    const remaining = 10 - selectedImages.length - pendingImageCompressionCount.current;
    const accepted = incoming.filter(file =>
      file.type.startsWith("image/") && file.size <= 25 * 1024 * 1024
    ).slice(0, remaining);
    if (accepted.length !== incoming.length) {
      setError("Chỉ chọn tối đa 10 tệp ảnh, mỗi ảnh gốc không quá 25 MB.");
    } else {
      setError("");
    }
    pendingImageCompressionCount.current += accepted.length;
    setPendingImageCompressions(pendingImageCompressionCount.current);
    for (const file of accepted) {
      const id = crypto.randomUUID();
      compressDiaryImage(file)
        .then(({compressedBlob, thumbnailBlob}) => {
          const preview = URL.createObjectURL(thumbnailBlob);
          previewUrls.current.add(preview);
          setSelectedImages(current => [...current, {
            id, file, compressedBlob, thumbnailBlob, preview, status: "ready", error: "",
          }]);
        })
        .catch(compressionError => {
          setSelectedImages(current => [...current, {
            id, file, preview: "", status: "error",
            error: compressionError.message || "Không thể nén ảnh.",
          }]);
        })
        .finally(() => {
          pendingImageCompressionCount.current -= 1;
          setPendingImageCompressions(pendingImageCompressionCount.current);
        });
    }
  }

  function removeImage(image) {
    releasePreview(image.preview);
    setSelectedImages(current => current.filter(item => item.id !== image.id));
  }

  function showPendingImage(image) {
    if (!image.compressedBlob) return;
    const objectUrl = URL.createObjectURL(image.compressedBlob);
    previewUrls.current.add(objectUrl);
    setLightbox({url: objectUrl, alt: image.file.name, objectUrl});
  }

  async function saveSummary(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      const response = await apiFetch(`${API}/nhat-ky/thong-tin-ngay`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({...summary, cong_trinh: project, ngay: diaryDate,
          nhan_luc_so_nguoi: summary.nhan_luc_so_nguoi === "" ? null : Number(summary.nhan_luc_so_nguoi)}),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.message || "Không thể lưu thông tin trong ngày.");
      setSummary(payload);
      setNotice("Đã cập nhật nhân lực, thiết bị và thời tiết.");
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="content diary-content">
      <div className="page-title">
        <div>
          <h1>Nhật ký thi công</h1>
          <p>Ghi nhận hoạt động theo công trình, ngày và hạng mục công việc.</p>
        </div>
        {import.meta.env.DEV && <button className="btn btn-primary" type="button" onClick={openSampleConflict}>Thử xung đột mẫu</button>}
      </div>
      {conflictNotice && <div className="success" role="status">{conflictNotice}</div>}
      <section className="panel diary-panel">
        <div className="diary-filters">
          <label>Công trình<select value={project} onChange={e => setProject(e.target.value)}>{projects.map(item => <option key={item.id} value={item.ten}>{item.ten}</option>)}</select></label>
          <label>Ngày<input type="date" value={diaryDate} onChange={e => setDiaryDate(e.target.value)}/></label>
          <label>Lọc theo hạng mục<select value={taskFilter} onChange={e => setTaskFilter(e.target.value)}><option value="">Tất cả hạng mục</option>{projectTasks.map(task => <option key={task.id} value={task.id}>{task.ten}</option>)}</select></label>
        </div>
      </section>
      <section className="panel daily-summary">
        <div className="panel-head"><div><h2>Tình hình trong ngày</h2><p>Nhân lực, thiết bị sử dụng và thời tiết tại công trường.</p></div></div>
        {canWrite ? <form onSubmit={saveSummary} className="summary-form">
          <label>Số nhân lực<input type="number" min="0" max="10000" value={summary.nhan_luc_so_nguoi ?? ""} onChange={e => setSummary({...summary, nhan_luc_so_nguoi: e.target.value})} placeholder="Nhập số người"/></label>
          <label>Ghi chú nhân lực<input maxLength={2000} value={summary.nhan_luc_ghi_chu || ""} onChange={e => setSummary({...summary, nhan_luc_ghi_chu: e.target.value})} placeholder="Ví dụ: 2 tổ thi công, 1 cán bộ giám sát"/></label>
          <label>Thiết bị sử dụng<textarea rows={2} maxLength={4000} value={summary.thiet_bi || ""} onChange={e => setSummary({...summary, thiet_bi: e.target.value})} placeholder="Tên thiết bị và tình trạng sử dụng"/></label>
          <label>Thời tiết<select value={summary.thoi_tiet || ""} onChange={e => setSummary({...summary, thoi_tiet: e.target.value})}><option value="">Chưa ghi nhận</option><option>Nắng</option><option>Nhiều mây</option><option>Mưa</option><option>Khác</option></select></label>
          <label>Ghi chú thời tiết<input maxLength={2000} value={summary.ghi_chu_thoi_tiet || ""} onChange={e => setSummary({...summary, ghi_chu_thoi_tiet: e.target.value})} placeholder="Mô tả ảnh hưởng đến thi công"/></label>
          <button className="primary">Lưu tình hình ngày</button>
        </form> : <div className="summary-readonly"><p><strong>Nhân lực:</strong> {summary.nhan_luc_so_nguoi ?? "Chưa ghi nhận"}{summary.nhan_luc_ghi_chu ? ` — ${summary.nhan_luc_ghi_chu}` : ""}</p><p><strong>Thiết bị:</strong> {summary.thiet_bi || "Chưa ghi nhận"}</p><p><strong>Thời tiết:</strong> {summary.thoi_tiet || "Chưa ghi nhận"}{summary.ghi_chu_thoi_tiet ? ` — ${summary.ghi_chu_thoi_tiet}` : ""}</p></div>}
      </section>
      {canWrite && <form className="panel diary-form" onSubmit={saveEntry}>
        <div className="panel-head"><div><h2>Thêm mục nhật ký</h2><p>Mỗi mục cần gắn với một hạng mục công việc.</p></div></div>
        <div className="diary-form-fields">
          <label>Hạng mục<select required value={form.cong_viec_id} onChange={e => setForm({...form, cong_viec_id: e.target.value})}><option value="">Chọn hạng mục</option>{projectTasks.map(task => <option key={task.id} value={task.id}>{task.ten}</option>)}</select></label>
          <label>Thời gian<input required type="time" value={form.gio} onChange={e => setForm({...form, gio: e.target.value})}/></label>
          <label className="diary-description">Mô tả công việc<textarea required maxLength={5000} rows={3} value={form.noi_dung} onChange={e => setForm({...form, noi_dung: e.target.value})} placeholder="Mô tả công việc đã thực hiện..."/></label>
          <button className="primary" disabled={saving || !projectTasks.length || pendingImageCompressions > 0}>
            {saving ? "Đang lưu..." : pendingImageCompressions > 0 ? `Đang nén ảnh (${pendingImageCompressions})…` : "Lưu nhật ký"}
          </button>
        </div>
        <div className="diary-image-upload">
          <span className="diary-upload-title">Hình ảnh hiện trường</span>
          <div
            className={`diary-dropzone${isDraggingImages ? " dragging" : ""}`}
            onDragOver={event => { event.preventDefault(); setIsDraggingImages(true); }}
            onDragLeave={() => setIsDraggingImages(false)}
            onDrop={event => {
              event.preventDefault();
              setIsDraggingImages(false);
              addImages(event.dataTransfer.files);
            }}
          >
            <UploadCloud size={22}/>
            <span>Kéo thả ảnh vào đây hoặc</span>
            <label className="diary-image-picker">
              Chọn hình ảnh hiện trường
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={event => {
                  addImages(event.target.files);
                  event.target.value = "";
                }}
              />
            </label>
            <small>Tối đa 10 ảnh · Tự động nén mỗi ảnh xuống dưới 1 MB</small>
          </div>
          <label className="diary-image-note">Ghi chú cho ảnh
            <input
              type="text"
              maxLength={500}
              value={imageNote}
              onChange={event => setImageNote(event.target.value)}
              placeholder="Ví dụ: Ảnh thi công móng khối A"
            />
          </label>
          {selectedImages.length > 0 && <div className="diary-image-grid">
            {selectedImages.map(image => <div className={`diary-image-card ${image.status === "error" ? "failed" : ""}`} key={image.id}>
              <button className="diary-image-preview" type="button" onClick={() => showPendingImage(image)} disabled={!image.compressedBlob}>
                {image.preview ? <img src={image.preview} alt={image.file.name}/> : <span className="diary-image-placeholder">Đang xử lý ảnh</span>}
              </button>
              <button className="diary-image-remove" type="button" aria-label={`Xóa ảnh ${image.file.name}`} onClick={() => removeImage(image)}><X size={15}/></button>
              <small className="diary-image-name" title={image.file.name}>{image.file.name}</small>
              <small className="diary-image-size">
                {formatFileSize(image.file.size)}
                {image.compressedBlob ? ` → ${formatFileSize(image.compressedBlob.size)}` : ""}
              </small>
              <span className={`diary-upload-status ${image.status === "error" ? "not-uploaded" : ""}`}>
                {image.status === "processing" ? "Đang nén" : image.status === "uploading" ? "Đang tải" : image.status === "error" ? "Chưa tải" : "Chưa tải"}
              </span>
              {image.status === "error" && <small className="diary-image-error">{image.error}</small>}
              {image.status === "error" && image.entryId && <button className="diary-retry" type="button" onClick={() => retryImage(image)}><RotateCw size={13}/> Tải lại</button>}
              {image.status === "error" && !image.entryId && <button className="diary-retry" type="button" onClick={() => retryImage(image)}><RotateCw size={13}/> Thử nén lại</button>}
            </div>)}
          </div>}
          <DiaryImageUploadStatus
            items={imageUploadQueue.items}
            isOnline={imageUploadQueue.isOnline}
            isLoading={imageUploadQueue.isLoading}
            error={imageUploadQueue.error}
            onRetry={imageUploadQueue.retryImage}
            onRemove={imageUploadQueue.removeImage}
          />
        </div>
      </form>}
      {error && <div className="alert" role="alert">{error}</div>}
      {notice && <div className="success" role="status">{notice}</div>}
      <section className="panel diary-list">
        <div className="panel-head"><div><h2>Nhật ký ngày {diaryDate}</h2><p>{project || "Đang tải công trình"}</p></div></div>
        {entries.length ? <div className="diary-entries">{entries.map(entry => <article className="diary-entry" key={entry.id}>
          <time>{entry.gio}</time><div><strong>{entry.hang_muc}</strong><p>{entry.noi_dung}</p><small>Người ghi: {entry.nguoi_lap}</small>
            {entry.images?.length > 0 && <div className="diary-saved-images">{entry.images.map((image, index) => <figure key={image.id || `${image.url}-${index}`}>
              <button type="button" onClick={() => openLightbox(image.url, image.ghi_chu || `Ảnh hiện trường ${index + 1}`)} aria-label="Mở ảnh hiện trường">
                <img src={image.thumbnail_url || image.url} loading="lazy" alt={image.ghi_chu || `Ảnh hiện trường ${index + 1}`}/>
              </button>
              <span className="diary-upload-status uploaded">Đã tải</span>
              {image.ghi_chu && <figcaption>{image.ghi_chu}</figcaption>}
            </figure>)}</div>}
          </div>
        </article>)}</div> : <p className="diary-empty">Chưa có mục nhật ký cho bộ lọc này.</p>}
      </section>
      {lightbox && <div className="diary-lightbox" role="dialog" aria-modal="true" aria-label="Ảnh hiện trường" onMouseDown={event => {
        if (event.target === event.currentTarget) closeLightbox();
      }}>
        <button type="button" className="diary-lightbox-close" aria-label="Đóng ảnh" onClick={closeLightbox}><X/></button>
        <img src={lightbox.url} alt={lightbox.alt}/>
      </div>}
      {sampleConflict && <DiaryConflictModal
        conflict={sampleConflict}
        onClose={() => setSampleConflict(null)}
        onResolve={finishSampleConflict}
      />}
    </div>
  );
}

function SimpleTable({title, endpoint, columns, headers}) {
  const [data, setData] = useState([]);
  useEffect(() => {
    apiFetch(API + endpoint)
      .then(r => r.json())
      .then(setData)
      .catch(() => {});
  }, [endpoint]);

  return (
    <section className="panel table-panel">
      {title && <div className="panel-head"><h2>{title}</h2></div>}
      <Table data={data} columns={columns} headers={headers}/>
    </section>
  );
}

function Table({data, columns, headers}) {
  if (!data) return null;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {headers.map(h => <th key={h}>{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={r.id || i}>
              {columns.map(c => (
                <td key={c}>
                  {c === "trang_thai" ? <Status value={r[c]}/> : r[c]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SettingsPage({ user, onPasswordChanged }) {
  const [accounts, setAccounts] = useState([]);
  const [form, setForm] = useState({ username: "", full_name: "", password: "", role: "viewer" });
  const [password, setPassword] = useState({ current_password: "", new_password: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadAccounts() {
    const response = await apiFetch(`${API}/auth/users`);
    if (response.ok) setAccounts(await response.json());
  }

  useEffect(() => { if (user.role === "admin") loadAccounts(); }, [user.role]);

  async function createAccount(event) {
    event.preventDefault(); setMessage(""); setError("");
    const response = await apiFetch(`${API}/auth/users`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form),
    });
    const result = await response.json();
    if (!response.ok) { setError(result.message || "Không thể tạo tài khoản."); return; }
    setForm({ username: "", full_name: "", password: "", role: "viewer" });
    setMessage("Đã tạo tài khoản."); loadAccounts();
  }

  async function editAccount(account, changes) {
    setMessage(""); setError("");
    const response = await apiFetch(`${API}/auth/users/${account.id}`, {
      method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(changes),
    });
    const result = await response.json();
    if (!response.ok) { setError(result.message || "Không thể cập nhật tài khoản."); return; }
    setMessage("Đã cập nhật tài khoản."); loadAccounts();
  }

  async function changePassword(event) {
    event.preventDefault(); setMessage(""); setError("");
    const response = await apiFetch(`${API}/auth/change-password`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(password),
    });
    const result = await response.json();
    if (!response.ok) { setError(result.message || "Không thể đổi mật khẩu."); return; }
    setMessage("Đã đổi mật khẩu. Vui lòng đăng nhập lại."); onPasswordChanged();
  }

  return <div className="content settings-content">
    <div className="page-title"><div><h1>Cài đặt tài khoản </h1><p>Quản lý thông tin đăng nhập và vai trò truy cập.</p></div></div>
    {message && <div className="success" role="status">{message}</div>}{error && <div className="alert" role="alert">{error}</div>}
    <section className="panel settings-panel"><div className="panel-head"><h2>Đổi mật khẩu</h2></div>
      <form className="settings-form" onSubmit={changePassword}>
        <label>Mật khẩu hiện tại<input type="password" autoComplete="current-password" required value={password.current_password} onChange={e => setPassword({ ...password, current_password: e.target.value })}/></label>
        <label>Mật khẩu mới (ít nhất 12 ký tự)<input type="password" autoComplete="new-password" minLength="12" maxLength="256" required value={password.new_password} onChange={e => setPassword({ ...password, new_password: e.target.value })}/></label>
        <button className="btn btn-primary">Lưu mật khẩu</button>
      </form>
    </section>
    {user.role === "admin" && <section className="panel settings-panel"><div className="panel-head"><h2>Quản lý tài khoản</h2><span>{accounts.length} tài khoản</span></div>
      <form className="account-create" onSubmit={createAccount}>
        <label>Tên đăng nhập<input pattern="[A-Za-z0-9_.-]{3,40}" required value={form.username} onChange={e => setForm({ ...form, username: e.target.value })}/></label>
        <label>Họ tên<input maxLength="120" required value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })}/></label>
        <label>Mật khẩu (ít nhất 12 ký tự)<input type="password" minLength="12" maxLength="256" required value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}/></label>
        <label>Vai trò<select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>{Object.entries(ROLE_NAMES).map(([role, label]) => <option value={role} key={role}>{label}</option>)}</select></label>
        <button className="btn btn-primary">Tạo tài khoản</button>
      </form>
      <div className="table-wrap"><table><thead><tr><th>Tài khoản</th><th>Vai trò</th><th>Trạng thái</th></tr></thead><tbody>{accounts.map(account => <tr key={account.id}>
        <td>{account.full_name}<small>@{account.username}</small></td>
        <td><select value={account.role} disabled={account.id === user.id} onChange={e => editAccount(account, { role: e.target.value })}>{Object.entries(ROLE_NAMES).map(([role, label]) => <option value={role} key={role}>{label}</option>)}</select></td>
        <td><button className={account.is_active ? "account-status active" : "account-status locked"} disabled={account.id === user.id} onClick={() => editAccount(account, { is_active: !account.is_active })}>{account.is_active ? "Đang hoạt động" : "Đã khóa"}</button></td>
      </tr>)}</tbody></table></div>
    </section>}
  </div>;
}

function Placeholder({title}) {
  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>{title}</h1>
          <p>Phân hệ đang được chuẩn bị. Bạn có thể mở rộng chức năng từ cấu trúc dự án này.</p>
        </div>
      </div>
      <div className="empty">
        <Settings size={38}/>
        <h2>Chức năng {title}</h2>
        <p>Giao diện cơ bản đã sẵn sàng để phát triển tiếp.</p>
      </div>
    </div>
  );
}

function SchedulePage({
  tasks,
  scheduleResults = [],
  baseline,
  baselineLoading,
  baselineError,
  baselineSaving,
  baselineSuccess,
  canManageBaseline,
  onCaptureBaseline,
  hasCycle,
  scheduleMessage,
  canUpdate,
  onOpenProgress,
  error,
}) {
  const [dependencies, setDependencies] = useState([]);
  const [dependencyError, setDependencyError] = useState("");
  const [loadingDependencies, setLoadingDependencies] = useState(true);
  const [criticalOnly, setCriticalOnly] = useState(false);
  const [sortMode, setSortMode] = useState("early-start");
  const categoryKey = [...new Set(
    tasks.map(task => task.category_id).filter(Number.isInteger)
  )].sort((a, b) => a - b).join(",");
  const categoryIds = categoryKey ? categoryKey.split(",").map(Number) : [];

  useEffect(() => {
    let active = true;
    setLoadingDependencies(true);
    setDependencyError("");

    Promise.all(categoryIds.map(async categoryId => {
      const response = await apiFetch(`${API}/categories/${categoryId}/dependencies`);
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.message || "Không thể tải quan hệ phụ thuộc.");
      }
      if (!Array.isArray(result)) {
        throw new Error("Dữ liệu quan hệ phụ thuộc không hợp lệ.");
      }
      return result;
    }))
      .then(results => {
        if (active) setDependencies(results.flat());
      })
      .catch(fetchError => {
        if (active) {
          setDependencies([]);
          setDependencyError(fetchError.message || "Không thể tải quan hệ phụ thuộc.");
        }
      })
      .finally(() => {
        if (active) setLoadingDependencies(false);
      });

    return () => { active = false; };
  }, [categoryKey]);

  const dependencyResult = sortTasksByDependencies(tasks, dependencies);
  const orderedTasks = [...dependencyResult.orderedTasks, ...dependencyResult.blockedTasks];
  const orderById = new Map(dependencyResult.orderedTasks.map((task, index) => [task.id, index + 1]));
  const cycleIds = new Set(dependencyResult.cycleTasks.map(task => task.id));
  const blockedIds = new Set(dependencyResult.blockedTasks.map(task => task.id));
  const relationshipsById = new Map(
    dependencyResult.relationships.map(relationship => [relationship.task.id, relationship])
  );
  const taskById = new Map(tasks.map(task => [task.id, task]));
  const sortedResults = [...scheduleResults]
    .filter(result => !criticalOnly || result.is_critical)
    .sort((left, right) => {
      if (sortMode === "early-start-desc") return right.es - left.es || left.task_id - right.task_id;
      if (sortMode === "delay-desc") return right.total_float - left.total_float || left.task_id - right.task_id;
      return left.es - right.es || left.task_id - right.task_id;
    });
  const chartTasks = sortedResults.map(result => ({
    ...taskById.get(result.task_id),
    ...result,
    id: result.task_id,
    name: result.ten,
    totalFloat: result.total_float,
    isCritical: Boolean(result.is_critical),
    actualTask: taskById.get(result.task_id),
  }));

  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Tiến độ và đường găng</h1>
          <p>Sơ đồ Gantt, đường găng và độ trễ của từng công việc.</p>
        </div>
        {canManageBaseline && (
          <button
            type="button"
            onClick={onCaptureBaseline}
            disabled={baselineSaving}
            style={{ backgroundColor: "#A8E6CF", color: "#2E5A4C", border: "1px solid #7BC4A8" }}
            onMouseEnter={event => { event.currentTarget.style.backgroundColor = "#96DBC2"; }}
            onMouseLeave={event => { event.currentTarget.style.backgroundColor = "#A8E6CF"; }}
          >
            {baselineSaving ? "Đang lưu..." : "Chốt kế hoạch gốc"}
          </button>
        )}
      </div>
      {baselineLoading && <p role="status">Đang tải kế hoạch gốc...</p>}
      {baselineError && <div className="alert" role="alert">{baselineError}</div>}
      {baselineSuccess && <div className="success" role="status">Đã chốt kế hoạch gốc thành công.</div>}
      {baseline && (
        <p className="progress-plan-note">
          Kế hoạch gốc đã chốt bởi {baseline.chot_boi} lúc{" "}
          {new Date(baseline.chot_luc).toLocaleString("vi-VN", { timeZone: "UTC" })} UTC
        </p>
      )}
      {error && <div className="alert" role="alert">{error}</div>}
      {loadingDependencies && <p role="status">Đang tải quan hệ phụ thuộc…</p>}
      {dependencyError && <div className="alert" role="alert">{dependencyError} Không thể đảm bảo thứ tự hiển thị.</div>}
      {dependencyResult.hasCycle && !dependencyError && (
        <div className="alert" role="alert">
          <strong>Phát hiện vòng phụ thuộc. Không thể xếp tất cả công việc.</strong>
          <p>Công việc nằm trong vòng: {dependencyResult.cycleTasks.map(task => task.ten).join(", ")}</p>
          <p>Công việc bị vòng chặn: {dependencyResult.blockedTasks.filter(task => !cycleIds.has(task.id)).map(task => task.ten).join(", ") || "Không có"}</p>
        </div>
      )}
      {canUpdate && <p className="progress-plan-note">Chọn thanh công việc để cập nhật tiến độ thực tế. Phần màu xanh thể hiện tỷ lệ đã hoàn thành.</p>}
      {hasCycle && <div className="alert" role="alert">{scheduleMessage || "Dữ liệu công việc có vòng lặp phụ thuộc, không thể tính tiến độ."}</div>}
      <section className="panel schedule-results-panel">
        <div className="schedule-table-controls">
          <label><input type="checkbox" checked={criticalOnly} onChange={event => setCriticalOnly(event.target.checked)}/> Chỉ hiện công việc găng</label>
          <select aria-label="Sắp xếp bảng tiến độ" value={sortMode} onChange={event => setSortMode(event.target.value)}>
            <option value="early-start">Thời điểm bắt đầu sớm nhất</option>
            <option value="early-start-desc">Thời điểm bắt đầu muộn nhất</option>
            <option value="delay-desc">Độ trễ giảm dần</option>
          </select>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>Công việc</th><th>ES</th><th>EF</th><th>LS</th><th>LF</th>
              <th>Độ trễ</th><th>Trạng thái</th>
            </tr></thead>
            <tbody>
              {sortedResults.map(result => (
                <tr key={result.task_id}>
                  <td>{result.ten}<small>{result.cong_trinh || "Chưa gán công trình"}</small></td>
                  <td>{result.es}</td><td>{result.ef}</td><td>{result.ls}</td><td>{result.lf}</td>
                  <td>{result.total_float} ngày</td>
                  <td>{result.is_critical ? <span className="status done">Công việc găng</span> : <span className="status wait">Không găng</span>}</td>
                </tr>
              ))}
              {!sortedResults.length && <tr><td colSpan="7">{hasCycle ? "Không thể hiển thị bảng do có vòng lặp phụ thuộc." : "Chưa có dữ liệu tiến độ."}</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
      {!loadingDependencies && !dependencyError && <section className="panel table-panel" style={{ marginTop: 18 }}>
        <div className="panel-head" style={{ padding: "18px 18px 0" }}>
          <div><h2>Thứ tự công việc theo quan hệ phụ thuộc</h2><p>Quan hệ tiên quyết và công việc kế tiếp được hiển thị hai chiều.</p></div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Thứ tự</th><th>Công việc</th><th>Phụ thuộc vào</th><th>Công việc kế tiếp</th><th>Trạng thái xếp</th></tr></thead>
            <tbody>
              {orderedTasks.map(task => {
                const relationship = relationshipsById.get(task.id);
                const status = cycleIds.has(task.id) ? "Nằm trong vòng" : blockedIds.has(task.id) ? "Bị vòng chặn" : "Có thể xếp";
                return <tr key={task.id}>
                  <td>{orderById.get(task.id) ?? "—"}</td>
                  <td>{task.ten}</td>
                  <td>{relationship.prerequisites.map(item => item.ten).join(", ") || "—"}</td>
                  <td>{relationship.dependents.map(item => item.ten).join(", ") || "—"}</td>
                  <td>{status}</td>
                </tr>;
              })}
              {!orderedTasks.length && <tr><td colSpan="5">Chưa có công việc.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>}
      {!hasCycle && <GanttChart
        data={chartTasks}
        baseline={baseline?.details}
        onTaskSelect={canUpdate ? onOpenProgress : undefined}
      />}
    </div>
  );
}

export default App;
