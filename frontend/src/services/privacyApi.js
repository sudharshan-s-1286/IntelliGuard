const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function analyzePrivacy(text, metadata = {}) {
  if (!text || !text.trim()) {
    throw new Error('Text cannot be empty.');
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${API_BASE}/api/v1/privacy/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, metadata }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      let errorDetail = `HTTP error! status: ${response.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorDetail = errorJson.detail || errorJson.message || errorDetail;
      } catch {
        if (errorText) errorDetail = errorText;
      }
      throw new Error(errorDetail);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Request timeout: The privacy analysis took too long to respond.');
    }
    if (error.message) {
      throw error;
    }
    throw new Error('Network failure: Unable to connect to the Privacy Agent.');
  }
}
