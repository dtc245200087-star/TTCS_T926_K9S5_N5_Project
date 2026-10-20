import { Cloud, RefreshCw, WifiOff } from "lucide-react";
import "../sync-status.css";

function formatSyncTime(value) {
  if (!value) return "Chưa có lần đồng bộ thành công";
  return `Lần gần nhất: ${new Date(value).toLocaleString("vi-VN")}`;
}

export default function SyncStatusWidget({
  items,
  pendingDiaryCount,
  pendingImageCount,
  lastSuccessfulSyncAt,
  isOnline,
  isLoading,
  isSyncing,
  error,
  syncNow,
}) {
  const pendingCount = pendingDiaryCount + pendingImageCount;

  return (
    <section className="sync-widget" aria-label="Trạng thái đồng bộ">
      <div className="sync-widget-summary" aria-live="polite">
        {isOnline ? <Cloud size={17} aria-hidden="true"/> : <WifiOff size={17} aria-hidden="true"/>}
        <span>{pendingDiaryCount} nhật ký chờ</span>
        <span>{pendingImageCount} ảnh chờ</span>
      </div>
      <small className="sync-widget-time">{formatSyncTime(lastSuccessfulSyncAt)}</small>
      <button
        className="sync-widget-button"
        type="button"
        onClick={syncNow}
        disabled={!isOnline || isSyncing || isLoading || pendingCount === 0}
        title={!isOnline ? "Thiết bị đang ngoại tuyến" : "Đồng bộ các mục đang chờ"}
      >
        <RefreshCw size={14} className={isSyncing ? "sync-widget-spinning" : ""}/>
        {isSyncing ? "Đang đồng bộ" : "Đồng bộ ngay"}
      </button>
      <details className="sync-widget-details">
        <summary>Chi tiết hàng đợi ({items.length})</summary>
        <ul>
          {items.length === 0 && <li>Chưa có mục trong hàng đợi.</li>}
          {items.map(item => (
            <li key={item.id}>
              <span>{item.title}</span>
              <strong className={item.status === "synced" ? "sync-item-done" : "sync-item-pending"}>
                {item.status === "synced" ? "Đã đồng bộ" : "Chưa đồng bộ"}
              </strong>
            </li>
          ))}
        </ul>
      </details>
      {error && <p className="sync-widget-error" role="alert">{error}</p>}
    </section>
  );
}
