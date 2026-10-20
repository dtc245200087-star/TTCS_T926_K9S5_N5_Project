import { useEffect, useMemo, useState } from "react";
import { X } from "lucide-react";
import {
  compareDiaryVersions,
  getDiaryFieldLabel,
  resolveDiaryConflict,
} from "../sync/diaryConflict.js";
import "../diary-conflict.css";

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

export default function DiaryConflictModal({ conflict, onClose, onResolve }) {
  const [choice, setChoice] = useState("merge");
  const {base, versionA, versionB} = conflict;
  const comparison = useMemo(
    () => compareDiaryVersions(base, versionA, versionB),
    [base, versionA, versionB],
  );
  const fieldSet = new Set([
    ...Object.keys(base || {}),
    ...Object.keys(versionA || {}),
    ...Object.keys(versionB || {}),
  ]);
  const fields = [...fieldSet].filter(field => field !== "id");
  const conflictingFields = new Set(comparison.conflicts.map(item => item.field));

  useEffect(() => {
    function closeOnEscape(event) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  function saveResolution() {
    onResolve(resolveDiaryConflict(base, versionA, versionB, choice));
  }

  return (
    <div className="diary-conflict-backdrop" onMouseDown={event => {
      if (event.target === event.currentTarget) onClose();
    }}>
      <section
        className="diary-conflict-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="diary-conflict-title"
      >
        <header className="diary-conflict-header">
          <div>
            <span className="diary-conflict-eyebrow">S-32 · GIẢI QUYẾT XUNG ĐỘT</span>
            <h2 id="diary-conflict-title">Hai phiên bản nhật ký khác nhau</h2>
            <p>{conflict.title || "So sánh thay đổi trước khi chọn phiên bản thống nhất."}</p>
          </div>
          <button type="button" className="diary-conflict-close" onClick={onClose} aria-label="Đóng">
            <X size={20}/>
          </button>
        </header>

        <div className="diary-conflict-legend">
          <span><i className="diary-conflict-dot auto"/>Tự động gộp được</span>
          <span><i className="diary-conflict-dot manual"/>Cần chọn cách xử lý</span>
          {comparison.conflicts.length === 0 && <strong>Không có trường xung đột trực tiếp.</strong>}
        </div>

        <div className="diary-conflict-columns">
          <VersionColumn
            title="Bản A · Thiết bị này"
            version={versionA}
            fields={fields}
            conflictingFields={conflictingFields}
          />
          <VersionColumn
            title="Bản B · Máy chủ"
            version={versionB}
            fields={fields}
            conflictingFields={conflictingFields}
          />
        </div>

        <section className="diary-conflict-automerge">
          <div className="diary-conflict-section-title">
            <div><h3>Kết quả tự gộp</h3><p>Các trường chỉ một bên thay đổi được lấy tự động.</p></div>
            <span>{comparison.conflicts.length ? `${comparison.conflicts.length} trường cần chọn` : "Có thể dùng ngay"}</span>
          </div>
          <div className="diary-conflict-merged-grid">
            {fields.map(field => (
              <div className={conflictingFields.has(field) ? "is-conflicting" : ""} key={field}>
                <strong>{getDiaryFieldLabel(field)}</strong>
                <p>{formatValue(comparison.merged[field])}</p>
                {conflictingFields.has(field) && <small>Giá trị đang hiển thị là bản A; chọn “Gộp cả hai” để giữ cả hai nội dung.</small>}
              </div>
            ))}
          </div>
        </section>

        <fieldset className="diary-conflict-choices">
          <legend>Chọn cách giải quyết</legend>
          <label className={choice === "versionA" ? "selected" : ""}>
            <input type="radio" name="diary-conflict-choice" value="versionA" checked={choice === "versionA"} onChange={() => setChoice("versionA")}/>
            <span><strong>Giữ bản A</strong><small>Dùng toàn bộ phiên bản trên thiết bị này.</small></span>
          </label>
          <label className={choice === "versionB" ? "selected" : ""}>
            <input type="radio" name="diary-conflict-choice" value="versionB" checked={choice === "versionB"} onChange={() => setChoice("versionB")}/>
            <span><strong>Giữ bản B</strong><small>Dùng toàn bộ phiên bản trên máy chủ.</small></span>
          </label>
          <label className={choice === "merge" ? "selected" : ""}>
            <input type="radio" name="diary-conflict-choice" value="merge" checked={choice === "merge"} onChange={() => setChoice("merge")}/>
            <span><strong>Gộp cả hai</strong><small>Tự gộp trường riêng; nối nội dung ở trường văn bản xung đột.</small></span>
          </label>
        </fieldset>

        <footer className="diary-conflict-footer">
          <p role="note">Bản thử nghiệm: lựa chọn chỉ được áp dụng trong giao diện, chưa ghi lên máy chủ.</p>
          <div>
            <button type="button" className="diary-conflict-secondary" onClick={onClose}>Để sau</button>
            <button type="button" className="diary-conflict-primary" onClick={saveResolution}>Xác nhận lựa chọn</button>
          </div>
        </footer>
      </section>
    </div>
  );
}

function VersionColumn({title, version, fields, conflictingFields}) {
  return (
    <section className="diary-conflict-version">
      <h3>{title}</h3>
      {fields.map(field => (
        <div className={`diary-conflict-field${conflictingFields.has(field) ? " is-conflicting" : ""}`} key={field}>
          <strong>{getDiaryFieldLabel(field)}</strong>
          <p>{formatValue(version?.[field])}</p>
          {conflictingFields.has(field) && <small>Hai bên cùng sửa trường này</small>}
        </div>
      ))}
    </section>
  );
}
