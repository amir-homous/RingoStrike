import axios from "axios";

const API_BASE = (
  import.meta.env.VITE_API_BASE ||
  "http://localhost:5005"
).replace(/\/+$/, "");

const instance = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  timeout: 15000,
});

function getStoredToken() {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    return window.localStorage.getItem("ringo_token");
  } catch {
    return null;
  }
}

instance.interceptors.request.use((config) => {
  const token = getStoredToken();

  if (token && !config.headers?.Authorization) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }

  return config;
});

export default {
  get: (...args) => instance.get(...args),
  post: (...args) => instance.post(...args),

  patch: (...args) => instance.patch(...args),

  put: (...args) => instance.put(...args),

  delete: (...args) => instance.delete(...args),
};
