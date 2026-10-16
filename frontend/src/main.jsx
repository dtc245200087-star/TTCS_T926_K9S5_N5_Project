import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import { apiFetch, setCsrfToken, setUnauthorizedHandler } from './api.js';
import { clearOfflineProfile, getOfflineProfile, saveOfflineProfile } from './offlineDiary.js';
import './style.css';
import './task-progress.css';

function LoginGate() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [offlineMode, setOfflineMode] = useState(false);

  useEffect(() => {
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
    setUnauthorizedHandler(() => {
      setUser(null); setCsrfToken(''); clearOfflineProfile().catch(() => {});
    });
    apiFetch('/api/auth/me').then(async response => {
      if (!response.ok) return;
      const data = await response.json();
      setUser(data.user); setCsrfToken(data.csrf_token); setOfflineMode(false);
      await saveOfflineProfile(data.user).catch(() => {});
    }).catch(async () => {
      const cachedUser = await getOfflineProfile().catch(() => null);
      if (cachedUser) { setUser(cachedUser); setOfflineMode(true); }
    }).finally(() => setLoading(false));
  }, []);

  async function submit(event) {
    event.preventDefault(); setError(''); setBusy(true);
    try {
      const csrfResponse = await apiFetch('/api/auth/csrf');
      const csrf = (await csrfResponse.json()).csrf_token;
      setCsrfToken(csrf);
      const response = await apiFetch('/api/auth/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || 'Không thể đăng nhập.');
      setCsrfToken(data.csrf_token); setUser(data.user); setOfflineMode(false);
      await saveOfflineProfile(data.user).catch(() => {});
      setCredentials({ username: '', password: '' });
    } catch (err) { setError(err.message || 'Không thể kết nối máy chủ.'); }
    finally { setBusy(false); }
  }

  async function logout() {
    try { await apiFetch('/api/auth/logout', { method: 'POST' }); }
    finally {
      setUser(null); setCsrfToken(''); setOfflineMode(false);
      await clearOfflineProfile().catch(() => {});
    }
  }

  function passwordChanged() {
    setUser(null); setCsrfToken('');
    clearOfflineProfile().catch(() => {});
  }

  if (loading) return <main className="login-shell"><p className="muted">Đang kiểm tra phiên đăng nhập…</p></main>;
  if (user) return <App user={user} offlineMode={offlineMode} onLogout={logout} onPasswordChanged={passwordChanged} />;
  return <main className="login-shell">
    <section className="login-card">
      <div className="brand-mark">DT</div>
      <p className="eyebrow">ĐIỀU HÀNH CÔNG TRÌNH</p>
      <h1>Đăng nhập</h1>
      <p className="muted">Sử dụng tài khoản được cấp để tiếp tục.</p>
      {error && <div className="alert" role="alert">{error}</div>}
      <form onSubmit={submit} className="stack">
        <label>Tên đăng nhập<input autoComplete="username" required value={credentials.username} onChange={e => setCredentials({ ...credentials, username: e.target.value })} /></label>
        <label>Mật khẩu<input autoComplete="current-password" type="password" required value={credentials.password} onChange={e => setCredentials({ ...credentials, password: e.target.value })} /></label>
        <button className="primary" disabled={busy}>{busy ? 'Đang đăng nhập…' : 'Đăng nhập'}</button>
      </form>
      <p className="footnote">Nếu chưa có tài khoản, liên hệ quản trị viên hệ thống.</p>
    </section>
  </main>;
}

createRoot(document.getElementById('root')).render(<LoginGate />);
