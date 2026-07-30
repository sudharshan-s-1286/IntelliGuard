#!/bin/bash
# Start backend in background
venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to be ready
echo "Waiting for server to start..."
sleep 5

# Hit the endpoint
echo "Sending cURL request..."
curl -s -X POST "http://localhost:8000/api/security/analyze" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json"}' > curl_output.json

echo "Server logs should have been printed above."
echo "API response:"
cat curl_output.json | python3 -m json.tool

# Kill server
kill $SERVER_PID
