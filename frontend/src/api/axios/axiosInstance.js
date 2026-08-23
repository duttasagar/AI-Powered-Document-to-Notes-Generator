import axios from "axios";

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

let refreshRequest = null;

axiosInstance.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem("notely_access_token");
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const refreshToken = localStorage.getItem("notely_refresh_token");

    if (
      error.response?.status !== 401 ||
      originalRequest?._retry ||
      originalRequest?.url?.endsWith("/user/refresh") ||
      !refreshToken
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    refreshRequest ??= axios.post(
      `${axiosInstance.defaults.baseURL}/user/refresh`,
      { refresh_token: refreshToken },
      { headers: { "Content-Type": "application/json" } },
    ).then((response) => {
      localStorage.setItem("notely_access_token", response.data.access_token);
      localStorage.setItem("notely_refresh_token", response.data.refresh_token);
      return response.data.access_token;
    }).finally(() => {
      refreshRequest = null;
    });

    try {
      const accessToken = await refreshRequest;
      originalRequest.headers.Authorization = `Bearer ${accessToken}`;
      return axiosInstance(originalRequest);
    } catch (refreshError) {
      localStorage.removeItem("notely_access_token");
      localStorage.removeItem("notely_refresh_token");
      return Promise.reject(refreshError);
    }
  },
);

export default axiosInstance;
