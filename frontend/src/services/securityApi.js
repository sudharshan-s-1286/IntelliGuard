const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function getHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/security/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching health status:", error);
    throw error;
  }
}

export async function analyzePrompt(prompt) {
  try {
    const response = await fetch(`${API_BASE}/api/security/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error analyzing prompt:", error);
    throw error;
  }
}
