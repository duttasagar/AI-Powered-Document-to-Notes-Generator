import axiosInstance from "../api/axios/axiosInstance";

async function handleRequest(request) {
  try {
    const response = await request;
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || "The server could not complete your request.");
  }
}

export async function registerUser(payload) {
  return handleRequest(axiosInstance.post("/user/register", payload));
}

export async function loginUser(payload) {
  return handleRequest(axiosInstance.post("/user/login", payload));
}

export async function sendForgotPasswordOtp(email) {
  return handleRequest(axiosInstance.post("/user/forgot-password", { email }));
}

export async function verifyRegistrationOtp(payload) {
  return handleRequest(axiosInstance.post("/user/verify_otp", payload));
}

export async function verifyResetOtp(payload) {
  return handleRequest(axiosInstance.post("/user/verify-reset-otp", payload));
}

export async function resendRegistrationOtp(email) {
  return handleRequest(axiosInstance.post("/user/resend-otp", { email }));
}

export async function resetPassword(payload) {
  return handleRequest(axiosInstance.post("/user/reset-password", payload));
}

export async function logoutUser() {
  const token = localStorage.getItem("notely_access_token");
  return handleRequest(axiosInstance.post("/user/logout", null, {
    headers: { Authorization: `Bearer ${token}` },
  }));
}

export async function refreshAccessToken(refreshToken) {
  return handleRequest(axiosInstance.post("/user/refresh", { refresh_token: refreshToken }));
}

export function getGoogleLoginUrl() {
  return `${axiosInstance.defaults.baseURL}/auth/google/login`;
}
