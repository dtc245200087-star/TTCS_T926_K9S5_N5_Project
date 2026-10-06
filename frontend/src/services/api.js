import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000/api"
});

export const getDashboard = () => api.get("/dashboard");
export const getCongTrinh = () => api.get("/cong-trinh");
export const getCongViec = () => api.get("/cong-viec");
export const createCongTrinh = (data) => api.post("/cong-trinh", data);
export const deleteCongTrinh = (id) => api.delete(`/cong-trinh/${id}`);
export const getLichLamViec = () => api.get("/lich-lam-viec");
export const updateLichLamViec = (projectId, ngay_lam_viec) => api.patch(`/lich-lam-viec/${projectId}`, { ngay_lam_viec });
export const createNgayNghi = (projectId, data) => api.post(`/lich-lam-viec/${projectId}/ngay-nghi`, data);
export const deleteNgayNghi = (id) => api.delete(`/lich-lam-viec/ngay-nghi/${id}`);
export const getTienDoCongTrinh = (projectId) => api.get(`/cong-trinh/${projectId}/tien-do`);
export const updateCongViec = (id, data) => api.put(`/cong-viec/${id}`, data);

export default api;
