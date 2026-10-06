import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import {
  Building2, ClipboardList, Users, TrendingUp,
  LayoutDashboard, HardHat, Menu, X, Plus, Trash2
} from "lucide-react";
import axios from "axios";
import "./styles.css";

// Cấu hình URL API từ môi trường Vite hoặc mặc định
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

// Component hiển thị thẻ thẻ thống kê
function StatCard({ icon, title, value, suffix = "" }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div>
        <p>{title}</p>
        <h2>{value}{suffix}</h2>
      </div>
    </div>
  );
}

// Component ứng dụng chính
function AppMain() {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState("dashboard");
  const [dashboard, setDashboard] = useState({});
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    ma_cong_trinh: "",
    ten_cong_trinh: "",
    dia_diem: "",
    chu_dau_tu: "",
    tien_do: 0,
    trang_thai: "Đang thi công"
  });

  // Gọi API lấy toàn bộ dữ liệu từ Backend
  const loadData = async () => {
    try {
      const [dRes, pRes, tRes] = await Promise.all([
        axios.get(`${API_BASE}/dashboard`),
        axios.get(`${API_BASE}/cong-trinh`),
        axios.get(`${API_BASE}/cong-viec`)
      ]);
      setDashboard(dRes.data || {});
      setProjects(pRes.data || []);
      setTasks(tRes.data || []);
      setError("");
    } catch (e) {
      setError("Không kết nối được Backend. Hãy kiểm tra Backend Flask hoặc Docker.");
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Xử lý thêm công trình mới
  const submitProject = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/cong-trinh`, form);
      setShowForm(false);
      setForm({
        ma_cong_trinh: "",
        ten_cong_trinh: "",
        dia_diem: "",
        chu_dau_tu: "",
        tien_do: 0,
        trang_thai: "Đang thi công"
      });
      loadData();
    } catch (e) {
      alert(e.response?.data?.message || "Có lỗi xảy ra khi thêm công trình");
    }
  };

  // Xử lý xóa công trình
  const removeProject = async (id) => {
    if (!confirm("Bạn có chắc chắn muốn xóa công trình này?")) return;
    try {
      await axios.delete(`${API_BASE}/cong-trinh/${id}`);
      loadData();
    } catch (e) {
      alert(e.response?.data?.message || "Không thể xóa công trình");
    }
  };

  return (
    <div className="app">
      {/* Thanh điều hướng Sidebar */}
      <aside className={`sidebar ${open ? "show" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><HardHat size={24} /></div>
          <div>
            <strong>THI CÔNG</strong>
            <span>Điều hành công trình</span>
          </div>
        </div>

        <nav>
          <button className={tab === "dashboard" ? "active" : ""} onClick={() => { setTab("dashboard"); setOpen(false); }}>
            <LayoutDashboard size={19} /> Tổng quan
          </button>
          <button className={tab === "projects" ? "active" : ""} onClick={() => { setTab("projects"); setOpen(false); }}>
            <Building2 size={19} /> Công trình
          </button>
          <button className={tab === "tasks" ? "active" : ""} onClick={() => { setTab("tasks"); setOpen(false); }}>
            <ClipboardList size={19} /> Công việc
          </button>
          <button onClick={() => alert("Chức năng Quản lý Nhân sự đang được phát triển!")}>
            <Users size={19} /> Nhân sự
          </button>
        </nav>

        <div className="sidebar-footer">
          <span>Hệ thống điều hành</span>
          <small>v1.0.0</small>
        </div>
      </aside>

      {/* Khu vực nội dung chính */}
      <main className="main">
        <header>
          <button className="mobile-menu" onClick={() => setOpen(!open)}>
            {open ? <X /> : <Menu />}
          </button>
          <div>
            <h1>{tab === "dashboard" ? "Tổng quan điều hành" : tab === "projects" ? "Quản lý công trình" : "Quản lý công việc"}</h1>
            <p>Theo dõi và điều hành tiến độ thi công</p>
          </div>
          <div className="header-user">
            <div className="avatar">AD</div>
            <div><strong>Quản trị viên</strong><small>Administrator</small></div>
          </div>
        </header>

        {error && <div className="error">{error}</div>}

        {/* TAB 1: TỔNG QUAN (DASHBOARD) */}
        {tab === "dashboard" && (
          <>
            <section className="stats">
              <StatCard icon={<Building2 />} title="Tổng công trình" value={dashboard.tong_cong_trinh ?? 0} />
              <StatCard icon={<HardHat />} title="Đang thi công" value={dashboard.dang_thi_cong ?? 0} />
              <StatCard icon={<ClipboardList />} title="Công việc" value={dashboard.tong_cong_viec ?? 0} />
              <StatCard icon={<TrendingUp />} title="Tiến độ TB" value={dashboard.tien_do_trung_binh ?? 0} suffix="%" />
            </section>

            <section className="content-grid">
              <div className="panel">
                <div className="panel-title">
                  <div><h3>Tiến độ công trình</h3><span>Cập nhật theo dữ liệu hệ thống</span></div>
                  <button className="outline-btn" onClick={() => setTab("projects")}>Xem tất cả</button>
                </div>
                <div className="project-list">
                  {projects.length === 0 ? <div className="empty">Chưa có dữ liệu công trình.</div> :
                    projects.slice(0, 5).map(p => (
                      <div className="project-row" key={p.id}>
                        <div className="project-info">
                          <strong>{p.ten_cong_trinh}</strong>
                          <span>{p.ma_cong_trinh} · {p.dia_diem || "Chưa cập nhật"}</span>
                        </div>
                        <div className="progress-wrap">
                          <div className="progress"><span style={{ width: `${p.tien_do}%` }} /></div>
                          <b>{p.tien_do}%</b>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              <div className="panel">
                <div className="panel-title">
                  <div><h3>Trạng thái công việc</h3><span>Tổng hợp hiện tại</span></div>
                </div>
                <div className="task-summary">
                  <div><span>Đã hoàn thành</span><b>{dashboard.cong_viec_hoan_thanh ?? 0}</b></div>
                  <div><span>Tổng công việc</span><b>{dashboard.tong_cong_viec ?? 0}</b></div>
                  <div><span>Nhân sự</span><b>{dashboard.tong_nhan_su ?? 0}</b></div>
                </div>
              </div>
            </section>
          </>
        )}

        {/* TAB 2: QUẢN LÝ CÔNG TRÌNH */}
        {tab === "projects" && (
          <section className="panel full">
            <div className="panel-title">
              <div><h3>Danh sách công trình</h3><span>Quản lý thông tin và tiến độ công trình</span></div>
              <button className="primary-btn" onClick={() => setShowForm(true)}><Plus size={18} /> Thêm công trình</button>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr><th>Mã</th><th>Tên công trình</th><th>Địa điểm</th><th>Tiến độ</th><th>Trạng thái</th><th>Thao tác</th></tr>
                </thead>
                <tbody>
                  {projects.length === 0 ? (
                    <tr><td colSpan="6" style={{ textAlign: "center", padding: "20px" }}>Chưa có công trình nào.</td></tr>
                  ) : (
                    projects.map(p => (
                      <tr key={p.id}>
                        <td><b>{p.ma_cong_trinh}</b></td>
                        <td>{p.ten_cong_trinh}</td>
                        <td>{p.dia_diem || "-"}</td>
                        <td>
                          <div className="mini-progress"><span style={{ width: `${p.tien_do}%` }} /></div>
                          {p.tien_do}%
                        </td>
                        <td><span className="badge">{p.trang_thai}</span></td>
                        <td>
                          <button className="icon-btn" onClick={() => removeProject(p.id)}><Trash2 size={17} /></button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* TAB 3: QUẢN LÝ CÔNG VIỆC */}
        {tab === "tasks" && (
          <section className="panel full">
            <div className="panel-title">
              <div><h3>Danh sách công việc</h3><span>Theo dõi các đầu việc thi công</span></div>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr><th>Công việc</th><th>Trạng thái</th><th>Ưu tiên</th><th>Tiến độ</th></tr>
                </thead>
                <tbody>
                  {tasks.length === 0 ? (
                    <tr><td colSpan="4" style={{ textAlign: "center", padding: "20px" }}>Chưa có công việc nào.</td></tr>
                  ) : (
                    tasks.map(t => (
                      <tr key={t.id}>
                        <td><b>{t.ten_cong_viec}</b><small>{t.mo_ta || ""}</small></td>
                        <td><span className="badge">{t.trang_thai}</span></td>
                        <td>{t.uu_tien}</td>
                        <td>{t.tien_do}%</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>

      {/* Modal Thêm công trình */}
      {showForm && (
        <div className="modal-backdrop">
          <form className="modal" onSubmit={submitProject}>
            <div className="modal-head">
              <h3>Thêm công trình</h3>
              <button type="button" onClick={() => setShowForm(false)}><X /></button>
            </div>
            <label>Mã công trình
              <input required value={form.ma_cong_trinh} onChange={e => setForm({ ...form, ma_cong_trinh: e.target.value })} />
            </label>
            <label>Tên công trình
              <input required value={form.ten_cong_trinh} onChange={e => setForm({ ...form, ten_cong_trinh: e.target.value })} />
            </label>
            <label>Địa điểm
              <input value={form.dia_diem} onChange={e => setForm({ ...form, dia_diem: e.target.value })} />
            </label>
            <label>Chủ đầu tư
              <input value={form.chu_dau_tu} onChange={e => setForm({ ...form, chu_dau_tu: e.target.value })} />
            </label>
            <label>Tiến độ (%)
              <input type="number" min="0" max="100" value={form.tien_do} onChange={e => setForm({ ...form, tien_do: Number(e.target.value) })} />
            </label>
            <div className="modal-actions">
              <button type="button" className="outline-btn" onClick={() => setShowForm(false)}>Hủy</button>
              <button type="submit" className="primary-btn">Lưu công trình</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

// Render ứng dụng vào DOM root
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AppMain />
  </React.StrictMode>
);