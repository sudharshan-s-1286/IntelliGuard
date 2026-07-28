const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function getHealth() {
  const url = `${API_BASE}/api/v1/trust/health`;
  console.log(`[trustApi] GET ${url}`);
  try {
    const response = await fetch(url);
    console.log(`[trustApi] GET ${url} response status: ${response.status}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log(`[trustApi] GET ${url} response:`, data);
    return data;
  } catch (error) {
    console.error(`[trustApi] Error fetching health status from ${url}:`, error);
    throw error;
  }
}

export async function analyzePrompt(prompt) {
  const url = `${API_BASE}/api/v1/trust/analyze`;
  const payload = { prompt };
  console.log(`[trustApi] POST ${url} payload:`, payload);
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    console.log(`[trustApi] POST ${url} response status: ${response.status}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log(`[trustApi] POST ${url} response:`, data);
    return data;
  } catch (error) {
    console.error(`[trustApi] Error analyzing prompt at ${url}:`, error);
    throw error;
  }
}
