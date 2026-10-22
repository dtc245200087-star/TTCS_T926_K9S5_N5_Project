const acceptanceForms = [
  {
    id: "NT-2026-019",
    project: "Nhà điều hành khu A",
    work: "Chưa cập nhật nội dung nghiệm thu",
    submittedAt: "21/10/2026",
    amount: 85000000,
    status: "pending",
    returnReason: "",
  },
  {
    id: "NT-2026-020",
    project: "Khối nhà xưởng B",
    work: "Chưa cập nhật nội dung nghiệm thu",
    submittedAt: "21/10/2026",
    amount: 120000000,
    status: "pending",
    returnReason: "",
  },
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

const initialAuditLogs = [
  {
    id: "audit-001",
    actor: "Nguyễn Minh Anh",
    action: "Duyệt",
    objectType: "Phiếu nghiệm thu",
    objectName: "NT-2026-018 · Nghiệm thu cốp pha tầng 3",
    timestamp: "21/10/2026 10:42",
    before: "Chờ duyệt",
    after: "Đã duyệt",
  },
  {
    id: "audit-002",
    actor: "Trần Quốc Bảo",
    action: "Sửa",
    objectType: "Đề nghị thanh toán",
    objectName: "DNTT-2026-012 · Đợt thanh toán tháng 10",
    timestamp: "21/10/2026 09:18",
    before: "Giá trị: 185.000.000 ₫",
    after: "Giá trị: 192.500.000 ₫",
  },
  {
    id: "audit-003",
    actor: "Lê Thu Hà",
    action: "Lập",
    objectType: "Khối lượng hợp đồng",
    objectName: "KL-2026-044 · Đổ bê tông sàn tầng 3",
    timestamp: "20/10/2026 16:35",
    before: null,
    after: "Khối lượng: 48,5 m³",
  },
  {
    id: "audit-004",
    actor: "Phạm Đức Long",
    action: "Sửa",
    objectType: "Phiếu nghiệm thu",
    objectName: "NT-2026-017 · Nghiệm thu cốt thép dầm",
    timestamp: "20/10/2026 14:06",
    before: "Ngày nghiệm thu: 19/10/2026",
    after: "Ngày nghiệm thu: 20/10/2026",
  },
  {
    id: "audit-005",
    actor: "Nguyễn Minh Anh",
    action: "Lập",
    objectType: "Đề nghị thanh toán",
    objectName: "DNTT-2026-012 · Đợt thanh toán tháng 10",
    timestamp: "20/10/2026 11:27",
    before: null,
    after: "Giá trị: 185.000.000 ₫",
  },
  {
    id: "audit-006",
    actor: "Võ Thanh Tùng",
    action: "Duyệt",
    objectType: "Khối lượng hợp đồng",
    objectName: "KL-2026-041 · Lắp dựng cốt thép dầm",
    timestamp: "19/10/2026 15:50",
    before: "Chờ duyệt",
    after: "Đã duyệt",
  },
  {
    id: "audit-007",
    actor: "Lê Thu Hà",
    action: "Sửa",
    objectType: "Khối lượng hợp đồng",
    objectName: "KL-2026-039 · Xây tường tầng 2",
    timestamp: "19/10/2026 13:12",
    before: "Khối lượng: 32 m²",
    after: "Khối lượng: 36 m²",
  },
  {
    id: "audit-008",
    actor: "Phạm Đức Long",
    action: "Lập",
    objectType: "Phiếu nghiệm thu",
    objectName: "NT-2026-017 · Nghiệm thu cốt thép dầm",
    timestamp: "19/10/2026 09:04",
    before: null,
    after: "Trạng thái: Chờ duyệt",
  },
  {
    id: "audit-009",
    actor: "Võ Thanh Tùng",
    action: "Duyệt",
    objectType: "Đề nghị thanh toán",
    objectName: "DNTT-2026-010 · Thanh toán vật tư đợt 2",
    timestamp: "18/10/2026 16:21",
    before: "Chờ duyệt",
    after: "Đã duyệt",
  },
];

const listeners = new Set();
let acceptances = acceptanceForms;
let auditLogs = initialAuditLogs;
let nextAuditId = 10;

function notify() {
  listeners.forEach(listener => listener());
}

function createAuditLog(acceptance, action, after) {
  const timestamp = new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(new Date());

  return {
    id: `audit-${Date.now()}-${nextAuditId++}`,
    actor: "Nguyễn Minh Anh",
    action,
    objectType: "Phiếu nghiệm thu",
    objectName: `${acceptance.id} · ${acceptance.work}`,
    timestamp,
    before: "Chờ duyệt",
    after,
  };
}

function updateAcceptance(id, status, action, after, returnReason = "") {
  const acceptance = acceptances.find(item => item.id === id && item.status === "pending");
  if (!acceptance) return false;

  acceptances = acceptances.map(item =>
    item.id === id
      ? {...item, status, returnReason}
      : item
  );
  auditLogs = [createAuditLog(acceptance, action, after), ...auditLogs];
  notify();
  return true;
}

export const mockDatabase = {
  subscribe(listener) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  getAcceptances() {
    return acceptances;
  },
  getAuditLogs() {
    return auditLogs;
  },
  approveAcceptance(id) {
    return updateAcceptance(id, "approved", "Duyệt", "Đã duyệt");
  },
  returnAcceptance(id, reason) {
    return updateAcceptance(id, "returned", "Trả lại", `Đã trả lại: ${reason}`, reason);
  },
};
