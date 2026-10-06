import React, { useEffect, useState } from "react";
import {
  Building2, ClipboardList, Users, TrendingUp, CalendarDays,
  LayoutDashboard, HardHat, Menu, X, Plus, Trash2, LogOut
} from "lucide-react";
import {
  getDashboard, getCongTrinh, getCongViec,
  createCongTrinh, deleteCongTrinh, getLichLamViec, updateLichLamViec,
  createNgayNghi, deleteNgayNghi, getTienDoCongTrinh, updateCongViec
} from "./services/api";

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

function AppMain() {
  // Kiểm tra phiên đăng nhập từ localStorage
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem("token");
  });
  
  // Thông tin đăng nhập
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState("dashboard");
  const [dashboard, setDashboard] = useState({});
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [calendars, setCalendars] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [schedule, setSchedule] = useState(null);
  const [calendarMessage, setCalendarMessage] = useState("");
  const [holidayForm, setHolidayForm] = useState({ ngay: "", ten: "" });
  const [savingTask, setSavingTask] = useState(null);
  const [scheduleRevision, setScheduleRevision] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    ma_cong_trinh: "",
    ten_cong_trinh: "",
    dia_diem: "",
    chu_dau_tu: "",
    tien_do: 0,
    trang_thai: "Đang thi công",
    ngay_bat_dau: "",
    ngay_ket_thuc_du_kien: ""
  });

  // Xử lý Đăng nhập
  const handleLoginSubmit = (e) => {
    e.preventDefault();
    // Giả lập lưu token và thông tin user khi đăng nhập thành công
    const fakeToken = "jwt_token_dieuhanhthicong_123456";
    const userData = { email: loginEmail };

    localStorage.setItem("token", fakeToken);
    localStorage.setItem("user", JSON.stringify(userData));
    
    setIsAuthenticated(true);
  };

  // Xử lý Đăng xuất
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
  };

  const loadData = async () => {
    if (!isAuthenticated) return;
    try {
      const [d, p, t] = await Promise.all([
        getDashboard(), getCongTrinh(), getCongViec()
      ]);
      setDashboard(d.data);
      setProjects(p.data);
      setTasks(t.data);
      if (p.data.length && !selectedProjectId) setSelectedProjectId(String(p.data[0].id));
      setError("");
    } catch (e) {
      setError("Không kết nối được Backend. Hãy kiểm tra Docker hoặc Flask.");
    }
  };

  useEffect(() => { loadData(); }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated || !selectedProjectId || !["tasks", "calendar"].includes(tab)) return;
    Promise.all([getLichLamViec(), getTienDoCongTrinh(selectedProjectId)])
      .then(([calendarResponse, scheduleResponse]) => {
        setCalendars(calendarResponse.data);
        setSchedule(scheduleResponse.data);
      })
      .catch((e) => setError(e.response?.data?.message || "Không thể tải lịch tiến độ công trình."));
  }, [isAuthenticated, selectedProjectId, tab, scheduleRevision]);

  const saveWeek = async (event) => {
    event.preventDefault();
    const calendar = calendars.find(item => item.cong_trinh_id === Number(selectedProjectId));
    if (!calendar) return;
    try {
      const response = await updateLichLamViec(selectedProjectId, calendar.ngay_lam_viec);
      setCalendars(items => items.map(item => item.cong_trinh_id === response.data.cong_trinh_id ? response.data : item));
      const currentSchedule = await getTienDoCongTrinh(selectedProjectId);
      setSchedule(currentSchedule.data);
      setCalendarMessage("Đã lưu ngày làm việc. Tiến độ công trình đã được tính lại.");
    } catch (e) {
      setCalendarMessage(e.response?.data?.message || "Không thể lưu lịch làm việc.");
    }
  };

  const addHoliday = async (event) => {
    event.preventDefault();
    try {
      await createNgayNghi(selectedProjectId, holidayForm);
      setHolidayForm({ ngay: "", ten: "" });
      const [calendarResponse, scheduleResponse] = await Promise.all([getLichLamViec(), getTienDoCongTrinh(selectedProjectId)]);
      setCalendars(calendarResponse.data);
      setSchedule(scheduleResponse.data);
      setCalendarMessage("Đã thêm ngày nghỉ và tính lại tiến độ công trình.");
    } catch (e) {
      setCalendarMessage(e.response?.data?.message || "Không thể thêm ngày nghỉ.");
    }
  };

  const removeHoliday = async (holidayId) => {
    try {
      await deleteNgayNghi(holidayId);
      const [calendarResponse, scheduleResponse] = await Promise.all([getLichLamViec(), getTienDoCongTrinh(selectedProjectId)]);
      setCalendars(calendarResponse.data);
      setSchedule(scheduleResponse.data);
      setCalendarMessage("Đã xóa ngày nghỉ và tính lại tiến độ công trình.");
    } catch (e) {
      setCalendarMessage(e.response?.data?.message || "Không thể xóa ngày nghỉ.");
    }
  };

  const saveTask = async (task) => {
    setSavingTask(task.id);
    try {
      await updateCongViec(task.id, {
        tien_do: Number(task.tien_do),
        thoi_luong_ngay: Number(task.thoi_luong_ngay),
        ngay_bat_dau_thuc_te: task.ngay_bat_dau_thuc_te || "",
        ngay_hoan_thanh_thuc_te: task.ngay_hoan_thanh_thuc_te || ""
      });
      await loadData();
      setScheduleRevision(revision => revision + 1);
      setCalendarMessage("Đã lưu mốc thực tế và tính lại mạng công việc.");
    } catch (e) {
      setCalendarMessage(e.response?.data?.message || "Không thể cập nhật công việc.");
    } finally {
      setSavingTask(null);
    }
  };

  const submitProject = async (e) => {
    e.preventDefault();
    try {
      await createCongTrinh(form);
      setShowForm(false);
      setForm({
        ma_cong_trinh: "", ten_cong_trinh: "", dia_diem: "",
        chu_dau_tu: "", tien_do: 0, trang_thai: "Đang thi công", ngay_bat_dau: "", ngay_ket_thuc_du_kien: ""
      });
      loadData();
    } catch (e) {
      alert(e.response?.data?.message || "Có lỗi xảy ra");
    }
  };

  const removeProject = async (id) => {
    if (!confirm("Bạn có chắc muốn xóa công trình này?")) return;
    await deleteCongTrinh(id);
    loadData();
  };

  const activeCalendar = calendars.find(item => item.cong_trinh_id === Number(selectedProjectId));
  const weekdays = [[0, "Thứ Hai"], [1, "Thứ Ba"], [2, "Thứ Tư"], [3, "Thứ Năm"], [4, "Thứ Sáu"], [5, "Thứ Bảy"], [6, "Chủ nhật"]];

  // NẾU CHƯA ĐĂNG NHẬP -> Hiển thị Form Đăng nhập
  if (!isAuthenticated) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#0f172a',
        fontFamily: 'sans-serif'
      }}>
        <div style={{
          background: '#ffffff',
          padding: '36px',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '400px',
          boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ textAlign: 'center', margin: '0 0 8px 0', fontSize: '24px', color: '#1e293b' }}>
            Đăng Nhập Hệ Thống
          </h2>
          <p style={{ textAlign: 'center', color: '#64748b', margin: '0 0 28px 0', fontSize: '14px' }}>
            Nền tảng điều hành thi công công trình
          </p>

          <form onSubmit={handleLoginSubmit} method="POST">
            <div style={{ marginBottom: '18px' }}>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500', color: '#334155' }}>
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="username email"
                required
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                placeholder="Nhập email"
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid #cbd5e1',
                  boxSizing: 'border-box',
                  outline: 'none',
                  fontSize: '14px'
                }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500', color: '#334155' }}>
                Mật khẩu
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder="Nhập mật khẩu"
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid #cbd5e1',
                  boxSizing: 'border-box',
                  outline: 'none',
                  fontSize: '14px'
                }}
              />
            </div>

            <button
              type="submit"
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '15px',
                cursor: 'pointer'
              }}
            >
              Đăng Nhập
            </button>
          </form>
        </div>
      </div>
    );
  }

  // NẾU ĐÃ ĐĂNG NHẬP -> Hiển thị Giao diện chính hệ thống
  return (
    <div className="app">
      <aside className={`sidebar ${open ? "show" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><HardHat size={24} /></div>
          <div>
            <strong>THI CÔNG</strong>
            <span>Điều hành công trình</span>
          </div>
        </div>

        <nav>
          <button className={tab === "dashboard" ? "active" : ""} onClick={() => {setTab("dashboard"); setOpen(false)}}>
            <LayoutDashboard size={19}/> Tổng quan
          </button>
          <button className={tab === "projects" ? "active" : ""} onClick={() => {setTab("projects"); setOpen(false)}}>
            <Building2 size={19}/> Công trình
          </button>
          <button className={tab === "tasks" ? "active" : ""} onClick={() => {setTab("tasks"); setOpen(false)}}>
            <ClipboardList size={19}/> Công việc
          </button>
          <button className={tab === "calendar" ? "active" : ""} onClick={() => {setTab("calendar"); setOpen(false)}}>
            <CalendarDays size={19}/> Lịch làm việc
          </button>
          <button>
            <Users size={19}/> Nhân sự
          </button>
        </nav>

        <div className="sidebar-footer">
          <span>Hệ thống điều hành</span>
          <small>v1.0.0</small>
        </div>
      </aside>

      <main className="main">
        <header>
          <button className="mobile-menu" onClick={() => setOpen(!open)}>
            {open ? <X /> : <Menu />}
          </button>
          <div>
            <h1>{tab === "dashboard" ? "Tổng quan điều hành" : tab === "projects" ? "Quản lý công trình" : tab === "calendar" ? "Lịch làm việc dự án" : "Quản lý công việc"}</h1>
            <p>Theo dõi và điều hành tiến độ thi công</p>
          </div>
          <div className="header-user" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="avatar">AD</div>
            <div><strong>Quản trị viên</strong><small>Administrator</small></div>
            <button 
              onClick={handleLogout} 
              title="Đăng xuất"
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#ef4444',
                display: 'flex',
                alignItems: 'center',
                marginLeft: '8px'
              }}
            >
              <LogOut size={20} />
            </button>
          </div>
        </header>

        {error && <div className="error">{error}</div>}

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
                        <div className="progress"><span style={{width: `${p.tien_do}%`}} /></div>
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

        {tab === "projects" && (
          <section className="panel full">
            <div className="panel-title">
              <div><h3>Danh sách công trình</h3><span>Quản lý thông tin và tiến độ công trình</span></div>
              <button className="primary-btn" onClick={() => setShowForm(true)}><Plus size={18}/> Thêm công trình</button>
            </div>
            <div className="table-scroll">
              <table>
                <thead><tr><th>Mã</th><th>Tên công trình</th><th>Địa điểm</th><th>Tiến độ</th><th>Trạng thái</th><th></th></tr></thead>
                <tbody>
                  {projects.map(p => <tr key={p.id}>
                    <td><b>{p.ma_cong_trinh}</b></td>
                    <td>{p.ten_cong_trinh}</td>
                    <td>{p.dia_diem || "-"}</td>
                    <td><div className="mini-progress"><span style={{width:`${p.tien_do}%`}}/></div>{p.tien_do}%</td>
                    <td><span className="badge">{p.trang_thai}</span></td>
                    <td><button className="icon-btn" onClick={() => removeProject(p.id)}><Trash2 size={17}/></button></td>
                  </tr>)}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {tab === "tasks" && (
          <>
          {calendarMessage && <div className="schedule-message" role="status">{calendarMessage}</div>}
          <section className="panel full schedule-overview">
            <div className="panel-title">
              <div><h3>Dự báo tiến độ</h3><span>Tính lại trên máy chủ từ ngày làm việc và mốc thực tế.</span></div>
              <select aria-label="Chọn công trình" value={selectedProjectId} onChange={e => setSelectedProjectId(e.target.value)}>
                {projects.map(project => <option value={project.id} key={project.id}>{project.ten_cong_trinh}</option>)}
              </select>
            </div>
            {schedule && <div className="schedule-kpis"><div><span>Ngày hoàn thành hiện tại</span><strong>{schedule.ngay_hoan_thanh_hien_tai}</strong></div><div><span>Ngày hoàn thành kế hoạch</span><strong>{schedule.ngay_hoan_thanh_ke_hoach}</strong></div><div><span>Chênh lệch</span><strong className={schedule.chenh_lech_ngay_lam_viec > 0 ? "schedule-delay" : "schedule-on-time"}>{schedule.chenh_lech_ngay_lam_viec > 0 ? `Chậm ${schedule.chenh_lech_ngay_lam_viec} ngày làm việc` : schedule.chenh_lech_ngay_lam_viec < 0 ? `Sớm ${Math.abs(schedule.chenh_lech_ngay_lam_viec)} ngày làm việc` : "Đúng kế hoạch"}</strong></div></div>}
          </section>
          <section className="panel full">
            <div className="panel-title"><div><h3>Mốc thực tế và dự báo công việc</h3><span>Lưu tiến độ hoặc mốc ngày thực tế để cập nhật toàn bộ mạng công việc.</span></div></div>
            <div className="table-scroll">
              <table>
                <thead><tr><th>Công việc</th><th>Tiến độ %</th><th>Bắt đầu thực tế</th><th>Hoàn thành thực tế</th><th>Dự báo hoàn thành</th><th></th><th></th></tr></thead>
                <tbody>
                  {tasks.filter(task => task.cong_trinh_id === Number(selectedProjectId)).map(t => <tr key={t.id}>
                    <td><b>{t.ten_cong_viec}</b><small>{t.mo_ta || ""}</small></td>
                    <td><input type="number" min="0" max="100" value={t.tien_do ?? 0} aria-label={`Tiến độ ${t.ten_cong_viec}`} onChange={e => setTasks(current => current.map(task => task.id === t.id ? {...task, tien_do: e.target.value} : task))}/><small>Thời lượng: <input className="duration-input" type="number" min="1" value={t.thoi_luong_ngay ?? 1} aria-label={`Thời lượng ${t.ten_cong_viec}`} onChange={e => setTasks(current => current.map(task => task.id === t.id ? {...task, thoi_luong_ngay: e.target.value} : task))}/> ngày</small></td>
                    <td><input type="date" value={t.ngay_bat_dau_thuc_te || ""} aria-label={`Ngày bắt đầu ${t.ten_cong_viec}`} onChange={e => setTasks(current => current.map(task => task.id === t.id ? {...task, ngay_bat_dau_thuc_te: e.target.value} : task))}/></td>
                    <td><input type="date" value={t.ngay_hoan_thanh_thuc_te || ""} aria-label={`Ngày hoàn thành ${t.ten_cong_viec}`} onChange={e => setTasks(current => current.map(task => task.id === t.id ? {...task, ngay_hoan_thanh_thuc_te: e.target.value} : task))}/></td>
                    <td>{t.ngay_hoan_thanh_du_bao || "—"}</td>
                    <td>{t.la_cong_viec_gang ? <span className="critical-badge">Công việc găng</span> : "—"}</td>
                    <td><button className="save-schedule-btn" disabled={savingTask === t.id} onClick={() => saveTask(t)}>{savingTask === t.id ? "Đang lưu…" : "Lưu mốc"}</button></td>
                  </tr>)}
                </tbody>
              </table>
            </div>
          </section>
          </>
        )}

        {tab === "calendar" && (
          <>
            {calendarMessage && <div className="schedule-message" role="status">{calendarMessage}</div>}
            <section className="panel full calendar-panel">
              <div className="panel-title"><div><h3>Lịch làm việc công trình</h3><span>Mỗi công trình có lịch riêng, mặc định làm việc 6 ngày trong tuần.</span></div>
                <select aria-label="Chọn công trình" value={selectedProjectId} onChange={e => setSelectedProjectId(e.target.value)}>{projects.map(project => <option value={project.id} key={project.id}>{project.ten_cong_trinh}</option>)}</select>
              </div>
              {activeCalendar && <form onSubmit={saveWeek}>
                <h4>Ngày làm việc trong tuần</h4>
                <div className="weekday-picker">{weekdays.map(([value, label]) => <label key={value}><input type="checkbox" checked={activeCalendar.ngay_lam_viec.includes(value)} onChange={e => setCalendars(current => current.map(item => item.cong_trinh_id === Number(selectedProjectId) ? {...item, ngay_lam_viec: e.target.checked ? [...item.ngay_lam_viec, value].sort() : item.ngay_lam_viec.filter(day => day !== value)} : item))}/>{label}</label>)}</div>
                <button className="save-schedule-btn">Lưu lịch tuần</button>
              </form>}
            </section>
            {activeCalendar && <section className="panel full calendar-panel">
              <div className="panel-title"><div><h3>Ngày nghỉ và ngày lễ</h3><span>Ngày nghỉ được loại khỏi phép tính tiến độ.</span></div></div>
              <form className="holiday-form" onSubmit={addHoliday}><label>Ngày nghỉ<input type="date" required value={holidayForm.ngay} onChange={e => setHolidayForm({...holidayForm, ngay: e.target.value})}/></label><label>Tên ngày nghỉ<input required maxLength="120" value={holidayForm.ten} onChange={e => setHolidayForm({...holidayForm, ten: e.target.value})} placeholder="Ví dụ: Nghỉ lễ"/></label><button className="save-schedule-btn">Thêm ngày nghỉ</button></form>
              <div className="table-scroll"><table><thead><tr><th>Ngày</th><th>Tên ngày nghỉ</th><th></th></tr></thead><tbody>{activeCalendar.ngay_nghi.map(day => <tr key={day.id}><td>{day.ngay}</td><td>{day.ten}</td><td><button className="remove-holiday-btn" onClick={() => removeHoliday(day.id)}>Xóa</button></td></tr>)}{!activeCalendar.ngay_nghi.length && <tr><td colSpan="3">Chưa khai báo ngày nghỉ.</td></tr>}</tbody></table></div>
            </section>}
          </>
        )}
      </main>

      {showForm && (
        <div className="modal-backdrop">
          <form className="modal" onSubmit={submitProject}>
            <div className="modal-head"><h3>Thêm công trình</h3><button type="button" onClick={() => setShowForm(false)}><X/></button></div>
            <label>Mã công trình<input required value={form.ma_cong_trinh} onChange={e=>setForm({...form, ma_cong_trinh:e.target.value})}/></label>
            <label>Tên công trình<input required value={form.ten_cong_trinh} onChange={e=>setForm({...form, ten_cong_trinh:e.target.value})}/></label>
            <label>Địa điểm<input value={form.dia_diem} onChange={e=>setForm({...form, dia_diem:e.target.value})}/></label>
            <label>Chủ đầu tư<input value={form.chu_dau_tu} onChange={e=>setForm({...form, chu_dau_tu:e.target.value})}/></label>
            <label>Ngày bắt đầu<input type="date" value={form.ngay_bat_dau} onChange={e=>setForm({...form, ngay_bat_dau:e.target.value})}/></label>
            <label>Ngày hoàn thành kế hoạch<input type="date" value={form.ngay_ket_thuc_du_kien} onChange={e=>setForm({...form, ngay_ket_thuc_du_kien:e.target.value})}/></label>
            <label>Tiến độ (%)<input type="number" min="0" max="100" value={form.tien_do} onChange={e=>setForm({...form, tien_do:e.target.value})}/></label>
            <div className="modal-actions"><button type="button" className="outline-btn" onClick={()=>setShowForm(false)}>Hủy</button><button className="primary-btn">Lưu công trình</button></div>
          </form>
        </div>
      )}
    </div>
  );
}

export default AppMain;
