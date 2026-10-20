import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, LoaderCircle, RotateCw, Trash2, Clock3 } from "lucide-react";
import "../diary-image-queue.css";

function UploadState({item}) {
  if (item.status === "uploading") {
    return <span className="s33-image-state uploading"><LoaderCircle className="s33-spin" size={15}/> Đang tải</span>;
  }
  if (item.status === "synced") {
    return <span className="s33-image-state synced"><CheckCircle2 size={15}/> Đã tải</span>;
  }
  if (item.status === "error") {
    return <span className="s33-image-state failed"><AlertCircle size={15}/> Lỗi</span>;
  }
  if (item.status === "waiting-entry") {
    return <span className="s33-image-state waiting"><Clock3 size={15}/> Chờ nhật ký có ID</span>;
  }
  if (item.status === "waiting") {
    return <span className="s33-image-state waiting"><Clock3 size={15}/> Đang chờ thử lại</span>;
  }
  return <span className="s33-image-state waiting"><Clock3 size={15}/> Đang chờ</span>;
}

function UploadItem({item, onRetry, onRemove}) {
  const [thumbnailUrl, setThumbnailUrl] = useState("");

  useEffect(() => {
    if (!item.thumbnailBlob) return undefined;
    const url = URL.createObjectURL(item.thumbnailBlob);
    setThumbnailUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [item.thumbnailBlob]);

  return (
    <article className={`s33-image-item ${item.status}`}>
      <div className="s33-image-thumb">
        {thumbnailUrl
          ? <img src={thumbnailUrl} alt={`Ảnh chờ tải: ${item.fileName}`}/>
          : <span>Ảnh</span>}
      </div>
      <div className="s33-image-info">
        <strong title={item.fileName}>{item.fileName}</strong>
        <UploadState item={item}/>
        {item.lastError && <small className="s33-image-error">{item.lastError}</small>}
      </div>
      <div className="s33-image-actions">
        {item.status === "error" && <button type="button" onClick={() => onRetry(item.id)} aria-label={`Thử tải lại ${item.fileName}`} title="Thử tải lại"><RotateCw size={15}/></button>}
        {item.status !== "uploading" && <button type="button" onClick={() => onRemove(item.id)} aria-label={`Xóa ${item.fileName} khỏi hàng đợi`} title="Xóa khỏi hàng đợi"><Trash2 size={15}/></button>}
      </div>
    </article>
  );
}

export default function DiaryImageUploadStatus({items, isOnline, isLoading, error, onRetry, onRemove}) {
  if (isLoading && !items.length) return <p className="s33-image-queue-note">Đang khôi phục hàng đợi ảnh…</p>;
  if (!items.length && !error) return null;

  return (
    <section className="s33-image-queue" aria-label="Hàng đợi tải ảnh">
      <div className="s33-image-queue-heading">
        <div><h3>Hàng đợi tải ảnh</h3><p>{isOnline ? "Ảnh được tải lần lượt trong nền." : "Ngoại tuyến — ảnh đã lưu trên thiết bị; ảnh có ID nhật ký sẽ tự thử lại khi có mạng."}</p></div>
        <span>{items.filter(item => item.status !== "synced").length} đang chờ</span>
      </div>
      {error && <p className="s33-image-queue-error" role="alert">{error}</p>}
      <div className="s33-image-queue-list">
        {items.map(item => <UploadItem key={item.id} item={item} onRetry={onRetry} onRemove={onRemove}/>)}
      </div>
    </section>
  );
}
