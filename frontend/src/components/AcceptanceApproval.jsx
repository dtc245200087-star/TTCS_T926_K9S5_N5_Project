import { useState } from "react";
import { Check, RotateCcw, X } from "lucide-react";
import "../acceptance-approval.css";

const initialAcceptances = [
  {
    id: "NT-2026-014",
    project: "Nhà điều hành khu A",
    work: "Nghiệm thu cốt thép móng trục A-B",
    submittedAt: "18/10/2026",
    amount: 48500000,
    status: "pending",
    returnReason: "",
  },
  {
    id: "NT-2026-013",
    project: "Nhà điều hành khu A",
    work: "Nghiệm thu bê tông sàn tầng 1",
    submittedAt: "16/10/2026",
    amount: 126000000,
    status: "approved",
    returnReason: "",
  },
  {
    id: "NT-2026-012",
    project: "Khối nhà xưởng B",
    work: "Nghiệm thu lắp đặt cốt thép dầm",
    submittedAt: "15/10/2026",
    amount: 74200000,
    status: "returned",
    returnReason: "Bổ sung biên bản kiểm tra và ảnh hiện trường.",
  },
  {
    id: "NT-2026-011",
    project: "Khối nhà xưởng B",
    work: "Nghiệm thu cốp pha cột tầng 2",
    submittedAt: "12/10/2026",
    amount: 63800000,
    status: "pending",
    returnReason: "",
  },
];

const statusLabels = {
  pending: "Chờ duyệt",
  approved: "Đã duyệt",
  returned: "Đã trả lại",
};

const currency = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
});

export default function AcceptanceApproval({ canManage }) {
  const [acceptances, setAcceptances] = useState(initialAcceptances);
  const [returningId, setReturningId] = useState(null);
  const [returnReason, setReturnReason] = useState("");
  const [returnError, setReturnError] = useState("");

  const approvedTotal = acceptances
    .filter(acceptance => acceptance.status === "approved")
    .reduce((total, acceptance) => total + acceptance.amount, 0);
  const pendingCount = acceptances.filter(acceptance => acceptance.status === "pending").length;
  const returningAcceptance = acceptances.find(acceptance => acceptance.id === returningId);

  function approveAcceptance(id) {
    setAcceptances(current => current.map(acceptance =>
      acceptance.id === id && acceptance.status === "pending"
        ? {...acceptance, status: "approved"}
        : acceptance
    ));
  }

  function openReturnModal(id) {
    setReturningId(id);
    setReturnReason("");
    setReturnError("");
  }

  function closeReturnModal() {
    setReturningId(null);
    setReturnReason("");
    setReturnError("");
  }

  function returnAcceptance(event) {
    event.preventDefault();
    const reason = returnReason.trim();
    if (!reason) {
      setReturnError("Vui lòng nhập lý do trả lại.");
      return;
    }

    setAcceptances(current => current.map(acceptance =>
      acceptance.id === returningId && acceptance.status === "pending"
        ? {...acceptance, status: "returned", returnReason: reason}
        : acceptance
    ));
    closeReturnModal();
  }

  return (
    <div className="content acceptance-approval">
      <div className="page-title">
        <div>
          <h1>Duyệt phiếu nghiệm thu</h1>
          <p>Kiểm tra hồ sơ nghiệm thu và cập nhật trạng thái phê duyệt.</p>
        </div>
      </div>

      <div className="acceptance-summary">
        <section className="acceptance-summary-card">
          <span>Luỹ kế phiếu đã duyệt</span>
          <strong>{currency.format(approvedTotal)}</strong>
          <small>Chỉ tính các phiếu có trạng thái đã duyệt</small>
        </section>
        <section className="acceptance-summary-card">
          <span>Phiếu chờ duyệt</span>
          <strong>{pendingCount}</strong>
          <small>Phiếu đang cần Ban quản lý xử lý</small>
        </section>
      </div>

      {!canManage && (
        <div className="acceptance-readonly-note" role="status">
          Bạn có quyền xem danh sách; chỉ Ban quản lý dự án mới có thể duyệt hoặc trả lại phiếu.
        </div>
      )}

      <section className="panel acceptance-list">
        <div className="panel-head">
          <div>
            <h2>Danh sách phiếu</h2>
            <p>Thao tác trên dữ liệu mẫu chỉ có hiệu lực trong phiên trình duyệt hiện tại.</p>
          </div>
        </div>
        <div className="acceptance-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Mã phiếu</th>
                <th>Công trình / hạng mục</th>
                <th>Ngày gửi</th>
                <th>Giá trị nghiệm thu</th>
                <th>Trạng thái</th>
                {canManage && <th>Thao tác</th>}
              </tr>
            </thead>
            <tbody>
              {acceptances.map(acceptance => (
                <tr key={acceptance.id}>
                  <td><strong>{acceptance.id}</strong></td>
                  <td>
                    <strong>{acceptance.project}</strong>
                    <small>{acceptance.work}</small>
                    {acceptance.returnReason && (
                      <small className="acceptance-return-reason">Lý do: {acceptance.returnReason}</small>
                    )}
                  </td>
                  <td>{acceptance.submittedAt}</td>
                  <td>{currency.format(acceptance.amount)}</td>
                  <td>
                    <span className={`acceptance-status ${acceptance.status}`}>
                      {statusLabels[acceptance.status]}
                    </span>
                  </td>
                  {canManage && (
                    <td>
                      {acceptance.status === "pending" ? (
                        <div className="acceptance-actions">
                          <button
                            type="button"
                            className="acceptance-approve"
                            onClick={() => approveAcceptance(acceptance.id)}
                          >
                            <Check size={15}/> Duyệt
                          </button>
                          <button
                            type="button"
                            className="acceptance-return"
                            onClick={() => openReturnModal(acceptance.id)}
                          >
                            <RotateCcw size={14}/> Trả lại
                          </button>
                        </div>
                      ) : <span className="acceptance-no-action">—</span>}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {returningAcceptance && (
        <div
          className="acceptance-modal-backdrop"
          onMouseDown={event => {
            if (event.target === event.currentTarget) closeReturnModal();
          }}
        >
          <section
            className="acceptance-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="acceptance-return-title"
          >
            <header className="acceptance-modal-header">
              <div>
                <span>TRẢ LẠI PHIẾU</span>
                <h2 id="acceptance-return-title">Nhập lý do trả lại</h2>
                <p>{returningAcceptance.id} · {returningAcceptance.work}</p>
              </div>
              <button type="button" onClick={closeReturnModal} aria-label="Đóng">
                <X size={19}/>
              </button>
            </header>
            <form onSubmit={returnAcceptance}>
              <label htmlFor="acceptance-return-reason">Lý do trả lại <strong aria-hidden="true">*</strong></label>
              <textarea
                id="acceptance-return-reason"
                value={returnReason}
                onChange={event => {
                  setReturnReason(event.target.value);
                  if (event.target.value.trim()) setReturnError("");
                }}
                placeholder="Nêu rõ hồ sơ hoặc nội dung cần bổ sung..."
                rows={4}
                aria-invalid={Boolean(returnError)}
                aria-describedby={returnError ? "acceptance-return-error" : undefined}
                autoFocus
              />
              {returnError && <p className="acceptance-form-error" id="acceptance-return-error" role="alert">{returnError}</p>}
              <footer>
                <button type="button" className="acceptance-cancel" onClick={closeReturnModal}>Huỷ</button>
                <button type="submit" className="acceptance-confirm-return">Xác nhận trả lại</button>
              </footer>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
