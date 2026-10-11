import React, { useEffect, useState } from "react";
import {
  LayoutDashboard, Building2, ClipboardList, Users, Package,
  Truck, BookOpen, BarChart3, Settings, Bell, Search,
  Plus, MapPin, CalendarDays, CheckCircle2, Clock3, AlertTriangle,
  Menu, X, TrendingUp
} from "lucide-react";
import { apiFetch } from "./api.js";
import GanttChart from "./components/GanttChart";
import scheduleData from "./mocks/scheduleData";

const API = "/api";
const ROLE_NAMES = { admin: "Quản trị viên", manager: "Quản lý công trình", engineer: "Kỹ sư", viewer: "Chỉ xem" };

const menu = [
  ["Tổng quan", LayoutDashboard],
  ["Công trình", Building2],
  ["Công việc", ClipboardList],
  ["Tiến độ và đường găng", TrendingUp],
  ["Nhân sự", Users],
  ["Vật tư", Package],
  ["Thiết bị", Truck],
  ["Nhật ký thi công", BookOpen],
  ["Báo cáo", BarChart3],
  ["Cài đặt", Settings],
];

function App({ user, onLogout, onPasswordChanged }) {
  const [page, setPage] = useState("Tổng quan");
  const [mobile, setMobile] = useState(false);
  const [data, setData] = useState(null);

  const loadDashboard = () =>
    apiFetch(`${API}/dashboard`).then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(setData).catch(() => setData(null));

  useEffect(() => { loadDashboard(); }, []);

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
            <button className="icon-btn"><Bell size={19}/><i></i></button>
            <div className="avatar">{user.full_name.slice(0, 2).toUpperCase()}</div>
            <button className="logout-btn" onClick={onLogout}>Đăng xuất</button>
          </div>
        </header>

        {page === "Tổng quan" ? <Dashboard data={data}/> :
         page === "Công trình" ? <Projects data={data?.cong_trinh_data || []} refresh={loadDashboard} canManage={["admin", "manager"].includes(user.role)}/> :
         page === "Tiến độ và đường găng" ? <SchedulePage user={user} /> :
         page === "Công việc" ? <Tasks canUpdate={["admin", "manager", "engineer"].includes(user.role)}/> :
         page === "Nhân sự" ? <SimpleTable title="Danh sách nhân sự" endpoint="/nhan-su" columns={["ho_ten","vai_tro","cong_trinh","trang_thai"]} headers={["Họ tên","Vai trò","Công trình","Trạng thái"]}/> :
         page === "Vật tư" ? <Materials/> :
         page === "Nhật ký thi công" ? <Diary canWrite={["admin", "manager", "engineer"].includes(user.role)}/> :
         page === "Cài đặt" ? <SettingsPage user={user} onPasswordChanged={onPasswordChanged}/> :
         <Placeholder title={page}/>}
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

function Tasks({canUpdate}) {
  const [data, setData] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function loadTasks() {
    const response = await apiFetch(`${API}/cong-viec`);
    if (!response.ok) throw new Error("Không thể tải danh sách công việc.");
    setData(await response.json());
  }

  useEffect(() => {
    loadTasks().catch(err => setError(err.message));
  }, []);

  function openProgressForm(task) {
    setSelectedTask(task);
    setForm({
      ngay_bat_dau_thuc_te: task.ngay_bat_dau_thuc_te || "",
      ngay_ket_thuc_thuc_te: task.ngay_ket_thuc_thuc_te || "",
      phan_tram_hoan_thanh: String(task.phan_tram_hoan_thanh ?? 0),
    });
    setError("");
  }

  async function saveProgress(event) {
    event.preventDefault();
    setError("");
    if (
      form.ngay_bat_dau_thuc_te &&
      form.ngay_ket_thuc_thuc_te &&
      form.ngay_ket_thuc_thuc_te < form.ngay_bat_dau_thuc_te
    ) {
      setError("Ngày kết thúc thực tế không được trước ngày bắt đầu thực tế.");
      return;
    }
    const completion = Number(form.phan_tram_hoan_thanh);
    if (!Number.isInteger(completion) || completion < 0 || completion > 100) {
      setError("Phần trăm hoàn thành phải là số nguyên từ 0 đến 100.");
      return;
    }

    setSaving(true);
    try {
      const response = await apiFetch(`${API}/cong-viec/${selectedTask.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ngay_bat_dau_thuc_te: form.ngay_bat_dau_thuc_te || null,
          ngay_ket_thuc_thuc_te: form.ngay_ket_thuc_thuc_te || null,
          phan_tram_hoan_thanh: completion,
        }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể cập nhật tiến độ.");
      setData(current => current.map(task => task.id === result.id ? result : task));
      setSelectedTask(null);
      setForm(null);
    } catch (err) {
      setError(err.message || "Không thể kết nối máy chủ.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Quản lý công việc</h1>
          <p>Theo dõi kế hoạch và cập nhật riêng ngày, phần trăm hoàn thành thực tế.</p>
        </div>
      </div>
      {error && !selectedTask && <div className="alert" role="alert">{error}</div>}
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
                {canUpdate && <td><button className="btn btn-primary" onClick={() => openProgressForm(task)}>Cập nhật</button></td>}
              </tr>)}
              {!data.length && <tr><td colSpan={canUpdate ? 9 : 8}>Chưa có công việc.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      {selectedTask && form && <div className="modal-bg" onMouseDown={event => {
        if (event.target === event.currentTarget && !saving) setSelectedTask(null);
      }}>
        <form className="modal progress-modal" onSubmit={saveProgress} aria-labelledby="progress-modal-title">
          <div className="modal-head">
            <div><h2 id="progress-modal-title">Cập nhật tiến độ thực tế</h2><p>{selectedTask.ten}</p></div>
            <button type="button" aria-label="Đóng" onClick={() => setSelectedTask(null)}>✕</button>
          </div>
          <p className="progress-plan-note">Kế hoạch: hạn {selectedTask.han || "chưa có"} · trạng thái {selectedTask.trang_thai}. Cập nhật này không thay đổi kế hoạch.</p>
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
            <button className="btn" type="button" disabled={saving} onClick={() => setSelectedTask(null)}>Hủy</button>
          </div>
        </form>
      </div>}
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

function Diary({canWrite}) {
  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Nhật ký thi công</h1>
          <p>Ghi nhận hoạt động tại công trường theo từng ngày.</p>
        </div>
        {canWrite && <button className="primary"><Plus size={18}/> Ghi nhật ký</button>}
      </div>
      <SimpleTable title="" endpoint="/nhat-ky" columns={["ngay","cong_trinh","noi_dung","nguoi_lap"]} headers={["Ngày","Công trình","Nội dung","Người lập"]}/>
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
    <div className="page-title"><div><h1>Cài đặt tài khoản</h1><p>Quản lý thông tin đăng nhập và vai trò truy cập.</p></div></div>
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

function SchedulePage({ user }) {
  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Tiến độ và đường găng</h1>
          <p>Sơ đồ Gantt, đường găng và độ trễ của từng công việc.</p>
        </div>
      </div>
      <GanttChart data={scheduleData} />
    </div>
  );
}

export default App;
