import "../s06.css";

const requirements = [
  "Tạo bảng dependencies.",
  "Hỗ trợ 4 loại quan hệ giữa các công việc.",
  "Cho phép nhập độ trễ, kể cả giá trị âm.",
  "Không cho tạo quan hệ trùng cùng một cặp công việc.",
  "Không cho một công việc phụ thuộc chính nó.",
  "Bổ sung khu vực khai báo quan hệ vào form công việc.",
  "Cho phép tìm công việc trước bằng tên khi chọn.",
  "Hiển thị thông báo lỗi khi khai báo quan hệ bị trùng.",
];

export default function S06DependencyPage() {
  return (
    <div className="content s06-content">
      <section className="s06-page" aria-labelledby="s06-title">
        <h1 id="s06-title">S-06 — Khai báo quan hệ phụ thuộc giữa các công việc</h1>
        <div className="s06-actions" aria-label="Trạng thái công việc">
          <button type="button" className="s06-status" aria-label="Trạng thái: To Do">
            <span>To Do</span><span aria-hidden="true">⌄</span>
          </button>
          <button type="button" aria-label="Agents"><span aria-hidden="true">⬡</span> Agents</button>
          <button type="button" aria-label="Automation"><span aria-hidden="true">ϟ</span></button>
          <button type="button" aria-label="Improve Task"><span aria-hidden="true">✦</span> Improve Task</button>
          <button type="button" className="s06-add" aria-label="Thêm">+</button>
        </div>

        <section className="s06-description" aria-labelledby="s06-description-title">
          <h2 id="s06-description-title"><span aria-hidden="true">⌄</span> Description</h2>
          <p><strong>Mục tiêu:</strong> Cho phép xác định công việc nào phụ thuộc vào công việc nào.</p>
          <ul>
            {requirements.map(requirement => <li key={requirement}>{requirement}</li>)}
          </ul>
        </section>
      </section>
    </div>
  );
}
