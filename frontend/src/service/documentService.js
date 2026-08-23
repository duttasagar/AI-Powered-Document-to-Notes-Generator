import axiosInstance from "../api/axios/axiosInstance";

async function handleRequest(request) {
  try {
    const response = await request;
    return response.data;
  } catch (error) {
    const detail = error.response?.data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || JSON.stringify(item)).join("; ")
      : typeof detail === "object" && detail !== null
        ? JSON.stringify(detail)
        : detail;
    throw new Error(message || "The server could not complete your request.");
  }
}

function authConfig() {
  const token = localStorage.getItem("notely_access_token");
  return { headers: { Authorization: `Bearer ${token}` } };
}

export function listDocuments() {
  return handleRequest(axiosInstance.get("/document", authConfig()));
}

export function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const token = localStorage.getItem("notely_access_token");
  return handleRequest(
    axiosInstance.post("/document/upload", formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    }),
  );
}

export function extractDocument(documentId) {
  return handleRequest(axiosInstance.post(`/extraction/${documentId}`, null, authConfig()));
}

export function generateNotes(documentId) {
  return handleRequest(axiosInstance.post(`/ai/notes/${documentId}`, null, authConfig()));
}

export function startGeneration(documentId) {
  return handleRequest(axiosInstance.post(`/ai/generate/${documentId}`, null, authConfig()));
}

export function uploadAndStartGeneration(files) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const token = localStorage.getItem("notely_access_token");
  return handleRequest(
    axiosInstance.post("/ai/generate", formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    }),
  );
}

export function deleteDocument(documentId) {
  return handleRequest(axiosInstance.delete(`/document/${documentId}`, authConfig()));
}