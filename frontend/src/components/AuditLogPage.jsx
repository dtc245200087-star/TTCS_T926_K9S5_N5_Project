import { useMemo, useState, useSyncExternalStore } from "react";
import { ClipboardCheck, FileText, PackageCheck, Search } from "lucide-react";
import { mockDatabase } from "../mocks/mockDatabase.js";
import "./audit-log.css";

const objectTypes = ["Phiếu nghiệm thu", "Đề nghị thanh toán", "Khối lượng hợp đồng"];
const actions = ["Lập", "Sửa", "Duyệt", "Trả lại"];

function AuditLogPage() {
  const auditLogData = useSyncExternalStore(mockDatabase.subscribe, mockDatabase.getAuditLogs);
  const [search, setSearch] = useState("");
  const [objectType, setObjectType] = useState("");
  const [action, setAction] = useState("");

  const filteredEntries = useMemo(() => {
    const query = search.trim().toLocaleLowerCase("vi");
    return auditLogData.filter(entry => {
      const matchesQuery = !query || [
        entry.actor,
        entry.action,
        entry.objectType,
        entry.objectName,
      ].some(value => value.toLocaleLowerCase("vi").includes(query));
      return matchesQuery
        && (!objectType || entry.objectType === objectType)
        && (!action || entry.action === action);
    });
  }, [auditLogData, search, objectType, action]);

  return (
    <div className="content audit-log-page">
      <div className="page-title">
        <div>
          <h1>Nhật ký thao tác</h1>
          <p>Theo dõi lịch sử lập, sửa và duyệt hồ sơ trong hệ thống.</p>
        </div>
        <span className="audit-log-total">{auditLogData.length} hoạt động mẫu</span>
      </div>

      <section className="audit-log-panel panel" aria-label="Lịch sử thao tác">
        <div className="audit-log-toolbar">
          <label className="audit-log-search">
            <Search size={17} aria-hidden="true"/>
            <input
              type="search"
              placeholder="Tìm người dùng hoặc hồ sơ..."
              value={search}
              onChange={event => setSearch(event.target.value)}
              aria-label="Tìm người dùng hoặc hồ sơ"
            />
          </label>
          <label className="audit-log-select-label">
            <span>Loại hồ sơ</span>
            <select value={objectType} onChange={event => setObjectType(event.target.value)} aria-label="Lọc theo loại hồ sơ">
              <option value="">Tất cả hồ sơ</option>
              {objectTypes.map(type => <option key={type} value={type}>{type}</option>)}
            </select>
          </label>
          <label className="audit-log-select-label">
            <span>Thao tác</span>
            <select value={action} onChange={event => setAction(event.target.value)} aria-label="Lọc theo thao tác">
              <option value="">Tất cả thao tác</option>
              {actions.map(value => <option key={value} value={value}>{value}</option>)}
            </select>
          </label>
        </div>

        <div className="audit-log-table-wrap">
          <table className="audit-log-table">
            <thead>
              <tr>
                <th>Người thực hiện</th>
                <th>Thao tác</th>
                <th>Đối tượng</th>
                <th>Thời điểm</th>
                <th>Giá trị trước / sau</th>
              </tr>
            </thead>
            <tbody>
              {filteredEntries.map(entry => (
                <tr key={entry.id}>
                  <td>
                    <div className="audit-log-actor">
                      <span className="audit-log-avatar" aria-hidden="true">{entry.actor.split(" ").slice(-2).map(part => part[0]).join("")}</span>
                      <strong>{entry.actor}</strong>
                    </div>
                  </td>
                  <td><span className={`audit-log-action audit-log-action-${entry.action}`}>{entry.action}</span></td>
                  <td>
                    <div className="audit-log-object">
                      <span className="audit-log-object-icon" aria-hidden="true">
                        {entry.objectType === "Phiếu nghiệm thu"
                          ? <ClipboardCheck size={16}/>
                          : entry.objectType === "Đề nghị thanh toán"
                            ? <FileText size={16}/>
                            : <PackageCheck size={16}/>}
                      </span>
                      <span><strong>{entry.objectType}</strong><small>{entry.objectName}</small></span>
                    </div>
                  </td>
                  <td><time>{entry.timestamp}</time></td>
                  <td>
                    <div className="audit-log-changes">
                      <span><small>Trước</small>{entry.before || "—"}</span>
                      <span><small>Sau</small>{entry.after || "—"}</span>
                    </div>
                  </td>
                </tr>
              ))}
              {!filteredEntries.length && (
                <tr><td className="audit-log-empty" colSpan="5">Không tìm thấy lịch sử thao tác phù hợp.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="audit-log-footer">
          Đang hiển thị {filteredEntries.length} / {auditLogData.length} hoạt động mẫu
        </div>
      </section>
    </div>
  );
}

export default AuditLogPage;
