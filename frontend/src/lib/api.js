import axios from "axios";

export function normalizeApiBase(value) {
  return String(value || "").trim().replace(/\/+$/, "");
}

export function isLoopbackApiBase(value) {
  const base = normalizeApiBase(value);

  return /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(base);
}

export function getDefaultApiBase() {
  if (import.meta.env.DEV) {
    return "http://localhost:5005";
  }

  return "";
}

function resolveApiBase() {
  const configuredBase = normalizeApiBase(import.meta.env.VITE_API_BASE);

  if (configuredBase) {
    if (import.meta.env.PROD && isLoopbackApiBase(configuredBase)) {
      return "";
    }

    return configuredBase;
  }

  return getDefaultApiBase();
}

export const API_BASE = resolveApiBase();

export const API_BASE_LABEL = API_BASE || "same-origin";

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
  request: (...args) => instance.request(...args),
  get: (...args) => instance.get(...args),
  post: (...args) => instance.post(...args),

  patch: (...args) => instance.patch(...args),

  put: (...args) => instance.put(...args),

  delete: (...args) => instance.delete(...args),
};
