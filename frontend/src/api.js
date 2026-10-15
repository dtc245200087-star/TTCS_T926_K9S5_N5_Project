let csrfToken = '';
let unauthorizedHandler = () => {};

export function setCsrfToken(value) {
  csrfToken = value || '';
}

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler || (() => {});
}

export async function apiFetch(input, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const headers = new Headers(options.headers || {});
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method) && csrfToken) {
    headers.set('X-CSRF-Token', csrfToken);
  }
  const response = await fetch(input, { ...options, headers, credentials: 'include' });
  if (response.status === 401) unauthorizedHandler();
  return response;
}
