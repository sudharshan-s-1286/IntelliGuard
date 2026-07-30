import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api():
    # We must run the lifespan events
    with TestClient(app) as client:
        test_prompt = "# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json"
        
        response = client.post("/api/security/analyze", json={"prompt": test_prompt})
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        import json
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_api()
