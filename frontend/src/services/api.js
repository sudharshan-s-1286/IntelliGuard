// Placeholder API file for FastAPI backend

const API_BASE_URL = "/api/v1";

export const api = {
  get: async (endpoint) => {
    // const response = await fetch(`${API_BASE_URL}${endpoint}`);
    // return response.json();
    return Promise.resolve({ data: [] });
  },
  post: async (endpoint, data) => {
    // const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify(data),
    // });
    // return response.json();
    return Promise.resolve({ status: "success" });
  },
  // Add other methods (put, delete) as needed
};

// Domain specific mock calls
export const getDashboardData = () => api.get("/dashboard");
export const getAgents = () => api.get("/agents");
export const getAuditLogs = () => api.get("/audit");
export const getReports = () => api.get("/reports");
