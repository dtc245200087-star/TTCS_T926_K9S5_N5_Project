import { useRegisterSW } from 'virtual:pwa-register/react';

export default function ReloadPrompt() {
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    immediate: true,
    onRegisterError(error) {
      console.error('Không thể đăng ký Service Worker:', error);
    },
  });

  if (!needRefresh) return null;

  return (
    <aside className="pwa-update" role="status" aria-live="polite">
      <button
        className="pwa-update-button"
        type="button"
        onClick={() => updateServiceWorker(true)}
      >
        Đã có phiên bản mới. Nhấn để cập nhật
      </button>
    </aside>
  );
}
