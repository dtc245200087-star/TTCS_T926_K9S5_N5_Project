import React, { useCallback, useEffect, useState } from "react";
import { AlertTriangle, Clock3, X } from "lucide-react";
import { apiFetch } from "../api.js";

const API = "/api";

export default function MilestoneAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [detail, setDetail] = useState(null);
  const [detailError, setDetailError] = useState("");
  const [loadingDetail, setLoadingDetail] = useState(false);

  const loadAlerts = useCallback(async () => {
    setError("");
    try {
      const response = await apiFetch(`${API}/milestones/alerts`);
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể tải cảnh báo mốc bàn giao.");
      setAlerts(result);
    } catch (loadError) {
      setError(loadError.message || "Không thể kết nối máy chủ.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAlerts(); }, [loadAlerts]);

  async function openAlert(alert) {
    setDetail(null);
    setDetailError("");
    setLoadingDetail(true);
    try {
      const response = await apiFetch(`${API}/milestones/alerts/${alert.id}`);
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Không thể tải chi tiết cảnh báo.");
      setDetail(result);
    } catch (loadError) {
      setDetailError(loadError.message || "Không thể kết nối máy chủ.");
    } finally {
      setLoadingDetail(false);
    }
  }

  return (
    <div className="content">
      <div className="page-title">
        <div>
          <h1>Cảnh báo mốc bàn giao</h1>
          <p>Các hạng mục có thời điểm kết thúc sớm dự kiến sau ngày bàn giao.</p>
        </div>
        <button className="btn btn-primary" onClick={loadAlerts}>Làm mới</button>
      </div>

      {error && <div className="alert" role="alert">{error}</div>}
      {loading ? <div className="loading">Đang tải cảnh báo...</div> :
        alerts.length === 0 && !error ? (
          <section className="panel milestone-empty">
            <Clock3 size={25}/>
            <div><b>Chưa có mốc nào bị vượt</b><p>Các mốc bàn giao hiện không có dự báo chậm.</p></div>
          </section>
        ) : (
          <section className="milestone-alert-list" aria-label="Danh sách cảnh báo mốc bàn giao">
            {alerts.map(alert => (
              <button className="milestone-alert-card" key={alert.id} onClick={() => openAlert(alert)}>
                <span className="milestone-alert-icon"><AlertTriangle size={19}/></span>
                <span className="milestone-alert-copy">
                  <b>{alert.category_name}</b>
                  <small>Hạn bàn giao {alert.deadline} · Dự kiến {alert.projected_finish}</small>
                </span>
                <strong>{alert.overrun_days} ngày trễ</strong>
              </button>
            ))}
          </section>
        )}

      {(loadingDetail || detailError || detail) && (
        <div className="modal-bg" onMouseDown={event => {
          if (event.target === event.currentTarget) {
            setDetail(null);
            setDetailError("");
          }
        }}>
          <section className="modal milestone-detail-modal" role="dialog" aria-modal="true" aria-labelledby="milestone-detail-title">
            <div className="modal-head">
              <div>
                <h2 id="milestone-detail-title">{detail?.category_name || "Chi tiết cảnh báo"}</h2>
                {detail && <p>Mốc bàn giao: {detail.deadline}</p>}
              </div>
              <button type="button" aria-label="Đóng" onClick={() => { setDetail(null); setDetailError(""); }}><X size={18}/></button>
            </div>
            {loadingDetail && <p className="muted">Đang tải chuỗi công việc...</p>}
            {detailError && <div className="alert" role="alert">{detailError}</div>}
            {detail && <>
              <div className="milestone-detail-summary">
                <AlertTriangle size={18}/>
                <span>Dự kiến hoàn thành {detail.projected_finish || "chưa xác định"}, vượt mốc <b>{detail.overrun_days} ngày</b>.</span>
              </div>
              <h3>Chuỗi công việc gây chậm</h3>
              {detail.delay_chain.length ? (
                <ol className="delay-chain">
                  {detail.delay_chain.map((taskName, index) => (
                    <li key={`${index}-${taskName}`}><span>{index + 1}</span><b>{taskName}</b></li>
                  ))}
                </ol>
              ) : <p className="muted">Chưa có đủ công việc được gán hạng mục và quan hệ phụ thuộc để xác định chuỗi.</p>}
            </>}
          </section>
        </div>
      )}
    </div>
  );
}
