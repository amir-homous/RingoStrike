import axios from "axios";

const API_BASE = (import.meta.env.VITE_API_BASE || "http://localhost:5005").replace(/\/+$/, "");

const instance = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // ✅ برای کوکی لوکال
  timeout: 15000,
});

export default {
  get: (...args) => instance.get(...args),
  post: (...args) => instance.post(...args),
};
