import React, { useEffect, useState } from "react";
import {
  LayoutDashboard, Building2, ClipboardList, Users, Package,
  Truck, BookOpen, BarChart3, Settings, Bell, Search,
  Plus, MapPin, CalendarDays, CheckCircle2, Clock3, AlertTriangle,
  Menu, X, LockKeyhole, UnlockKeyhole, Pencil, History, TrendingUp
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
         page === "Công việc" ? <Tasks data={data?.cong_viec_hom_nay || []}/> :
         page === "Nhân sự" ? <SimpleTable title="Danh sách nhân sự" endpoint="/nhan-su" columns={["ho_ten","vai_tro","cong_trinh","trang_thai"]} headers={["Họ tên","Vai trò","Công trình","Trạng thái"]}/> :
         page === "Vật tư" ? <Materials/> :
         page === "Nhật ký thi công" ? <Diary canWrite={["admin", "manager", "engineer"].includes(user.role)} canUnlock={["admin", "manager"].includes(user.role)}/> :
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

function Tasks({data}) {
  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Quản lý công việc</h1>
          <p>Theo dõi nhiệm vụ và người phụ trách tại công trường.</p>
        </div>
        <button className="primary"><Plus size={18}/> Thêm công việc</button>
      </div>
      <Table data={data} columns={["ten","cong_trinh","nguoi_phu_trach","trang_thai","han"]} headers={["Công việc","Công trình","Người phụ trách","Trạng thái","Hạn"]}/>
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

function Diary({canWrite, canUnlock}) {
  const [entries, setEntries] = useState([]);
  const [show, setShow] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ ngay: new Date().toLocaleDateString("en-CA"), cong_trinh: "", noi_dung: "" });
  const [unlockDay, setUnlockDay] = useState("");
  const [reason, setReason] = useState("");
  const [auditDay, setAuditDay] = useState("");
  const [audit, setAudit] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadEntries() {
    const response = await apiFetch(`${API}/nhat-ky`);
    if (response.ok) setEntries(await response.json());
  }
  useEffect(() => { loadEntries().catch(() => setError("Không thể tải nhật ký.")); }, []);

  function startAdd() {
    setEditing(null);
    setForm({ ngay: new Date().toLocaleDateString("en-CA"), cong_trinh: "", noi_dung: "" });
    setError(""); setShow(true);
  }

  function startEdit(entry) {
    setEditing(entry);
    setForm({ ngay: entry.ngay, cong_trinh: entry.cong_trinh, noi_dung: entry.noi_dung });
    setError(""); setShow(true);
  }

  async function saveEntry(event) {
    event.preventDefault(); setError(""); setMessage("");
    const response = await apiFetch(editing ? `${API}/nhat-ky/${editing.id}` : `${API}/nhat-ky`, {
      method: editing ? "PATCH" : "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(editing ? { cong_trinh: form.cong_trinh, noi_dung: form.noi_dung } : form),
    });
    const result = await response.json();
    if (!response.ok) { setError(result.message || "Không thể lưu nhật ký."); return; }
    setShow(false); setMessage(editing ? "Đã cập nhật nhật ký." : "Đã ghi nhật ký."); await loadEntries();
  }

  async function lockDay(day) {
    if (!window.confirm(`Khóa sổ nhật ký ngày ${day}? Sau khi khóa, nhật ký ngày này sẽ không thể chỉnh sửa.`)) return;
    setError(""); setMessage("");
    const response = await apiFetch(`${API}/nhat-ky/ngay/${day}/lock`, { method: "POST" });
    const result = await response.json();
    if (!response.ok) { setError(result.message || "Không thể khóa nhật ký."); return; }
    setMessage(`Đã khóa sổ nhật ký ngày ${day}.`); await loadEntries();
  }

  async function unlock(day) {
    setError(""); setMessage("");
    const response = await apiFetch(`${API}/nhat-ky/ngay/${day}/unlock`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ly_do: reason }),
    });
    const result = await response.json();
    if (!response.ok) { setError(result.message || "Không thể mở khóa nhật ký."); return; }
    setUnlockDay(""); setReason(""); setMessage(`Đã mở khóa nhật ký ngày ${day}.`); await loadEntries();
  }

  async function openAudit(day) {
    const response = await apiFetch(`${API}/nhat-ky/audit?ngay=${encodeURIComponent(day)}`);
    if (!response.ok) return;
    setAudit(await response.json()); setAuditDay(day);
  }

  const groups = Object.values(entries.reduce((result, entry) => {
    (result[entry.ngay] ||= { day: entry.ngay, locked: entry.is_locked, lockedBy: entry.khoa_boi, lockedAt: entry.khoa_luc, entries: [] }).entries.push(entry);
    return result;
  }, {}));

  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Nhật ký thi công</h1>
          <p>Ghi nhận và khóa sổ nhật ký theo ngày sau khi xác nhận.</p>
        </div>
        {canWrite && <button className="primary" onClick={startAdd}><Plus size={18}/> Ghi nhật ký</button>}
      </div>
      {message && <div className="success" role="status">{message}</div>}{error && <div className="alert" role="alert">{error}</div>}
      <section className="panel table-panel diary-panel">
        <div className="table-wrap"><table>
          <thead><tr><th>Công trình</th><th>Nội dung</th><th>Người lập</th><th>Thao tác</th></tr></thead>
          <tbody>{groups.length === 0 ? <tr><td colSpan="4" className="diary-empty">Chưa có nhật ký.</td></tr> : groups.map(group => <React.Fragment key={group.day}>
            <tr className={group.locked ? "diary-day locked" : "diary-day"}>
              <td colSpan="4"><div className="diary-day-head">
                <div className="diary-date"><CalendarDays size={15}/><b>{group.day}</b>{group.locked ? <span className="lock-badge"><LockKeyhole size={13}/> Đã khóa</span> : <span className="open-badge">Đang mở</span>}
                  {group.locked && <small>Khóa bởi {group.lockedBy}</small>}
                </div>
                <div className="diary-actions">
                  {group.locked ? canUnlock && <button className="text-btn" onClick={() => { setUnlockDay(group.day); setReason(""); setError(""); }}><UnlockKeyhole size={14}/> Mở khóa</button> : canWrite && <button className="text-btn" onClick={() => lockDay(group.day)}><LockKeyhole size={14}/> Khóa ngày</button>}
                  {canUnlock && <button className="text-btn" onClick={() => openAudit(group.day)}><History size={14}/> Lịch sử</button>}
                </div>
              </div></td>
            </tr>
            {group.entries.map(entry => <tr key={entry.id}>
              <td>{entry.cong_trinh}</td><td className="diary-content">{entry.noi_dung}</td><td>{entry.nguoi_lap}</td>
              <td>{canWrite && <button className="row-action" disabled={group.locked} title={group.locked ? "Ngày đã khóa" : "Sửa nhật ký"} onClick={() => startEdit(entry)}><Pencil size={15}/></button>}</td>
            </tr>)}
          </React.Fragment>)}</tbody>
        </table></div>
      </section>
      {show && <div className="modal-bg"><form className="modal" onSubmit={saveEntry}>
        <div className="modal-head"><h2>{editing ? "Sửa nhật ký" : "Ghi nhật ký"}</h2><button type="button" onClick={() => setShow(false)}>✕</button></div>
        {!editing && <label>Ngày nhật ký<input type="date" required value={form.ngay} onChange={e => setForm({ ...form, ngay: e.target.value })}/></label>}
        <label>Công trình<input required maxLength="255" value={form.cong_trinh} onChange={e => setForm({ ...form, cong_trinh: e.target.value })}/></label>
        <label>Nội dung<textarea required maxLength="10000" rows="5" value={form.noi_dung} onChange={e => setForm({ ...form, noi_dung: e.target.value })}/></label>
        {error && <div className="alert" role="alert">{error}</div>}
        <div className="modal-actions"><button className="btn btn-primary">Lưu nhật ký</button><button type="button" className="btn" onClick={() => setShow(false)}>Hủy</button></div>
      </form></div>}
      {unlockDay && <div className="modal-bg"><form className="modal" onSubmit={e => { e.preventDefault(); unlock(unlockDay); }}>
        <div className="modal-head"><h2>Mở khóa nhật ký</h2><button type="button" onClick={() => setUnlockDay("")}>✕</button></div>
        <p className="modal-note">Nhật ký ngày {unlockDay} sẽ cho phép chỉnh sửa trở lại.</p>
        <label>Lý do mở khóa<input required maxLength="500" value={reason} onChange={e => setReason(e.target.value)} placeholder="Nhập lý do mở khóa"/></label>
        {error && <div className="alert" role="alert">{error}</div>}
        <div className="modal-actions"><button className="btn btn-primary">Mở khóa</button><button type="button" className="btn" onClick={() => setUnlockDay("")}>Hủy</button></div>
      </form></div>}
      {auditDay && <div className="modal-bg"><div className="modal audit-modal">
        <div className="modal-head"><h2>Lịch sử nhật ký {auditDay}</h2><button onClick={() => setAuditDay("")}>✕</button></div>
        {audit.length ? <div className="audit-list">{audit.map(item => <div className="audit-row" key={item.id}><b>{item.hanh_dong === "lock" ? "Khóa sổ" : "Mở khóa"}</b><span>{item.thuc_hien_boi} · {new Date(item.thuc_hien_luc).toLocaleString("vi-VN")}</span>{item.ly_do && <small>Lý do: {item.ly_do}</small>}</div>)}</div> : <p className="modal-note">Chưa có thao tác khóa/mở khóa.</p>}
      </div></div>}
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
