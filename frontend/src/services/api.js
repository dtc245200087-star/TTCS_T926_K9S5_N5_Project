import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000/api"
});

export const getDashboard = () => api.get("/dashboard");
export const getCongTrinh = () => api.get("/cong-trinh");
export const getCongViec = () => api.get("/cong-viec");
export const createCongTrinh = (data) => api.post("/cong-trinh", data);
export const deleteCongTrinh = (id) => api.delete(`/cong-trinh/${id}`);

export default api;
