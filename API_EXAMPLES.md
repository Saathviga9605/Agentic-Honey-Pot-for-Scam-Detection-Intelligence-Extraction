# API Testing Examples

## Server Status Check

### Health Check
```bash
curl http://127.0.0.1:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "active_sessions": 0
}
```

---

## Message Ingestion (Main Endpoint)

### PowerShell (Windows)

**IMPORTANT:** The payload MUST include sessionId, message object with sender/text/timestamp, conversationHistory array, and metadata object.

```powershell
$payload = @"
{
  "sessionId": "demo-001",
  "message": {
    "sender": "scammer",
    "text": "URGENT! Your account will be blocked. Send Rs 5000 to 9876543210@paytm immediately!",
    "timestamp": "2026-01-31T10:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
"@

Invoke-RestMethod -Uri "http://127.0.0.1:5000/ingest-message" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"; "x-api-key"="test-key-123"} `
  -Body $payload
```

### cURL (Linux/Mac/Git Bash)

```bash
curl -X POST http://127.0.0.1:5000/ingest-message \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "sessionId": "demo-001",
    "message": {
      "sender": "scammer",
      "text": "URGENT! Your account will be blocked. Send Rs 5000 to 9876543210@paytm immediately!",
      "timestamp": "2026-01-31T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "reply": "Why is my account having issues? I haven't done anything wrong."
}
```

---

## Multi-Turn Conversation Example

Send multiple messages with the same sessionId to simulate a conversation:

### First Message
```powershell
# Message 1
$payload1 = @"
{
  "sessionId": "conversation-001",
  "message": {
    "sender": "scammer",
    "text": "Hello, this is from bank customer care. Your account has suspicious activity.",
    "timestamp": "2026-01-31T10:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {"channel": "Call", "language": "English", "locale": "IN"}
}
"@

Invoke-RestMethod -Uri "http://127.0.0.1:5000/ingest-message" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"; "x-api-key"="test-key-123"} `
  -Body $payload1
```

### Second Message
```powershell
# Message 2 - Include previous conversation
$payload2 = @"
{
  "sessionId": "conversation-001",
  "message": {
    "sender": "scammer",
    "text": "Please send your OTP and account number for verification.",
    "timestamp": "2026-01-31T10:02:00Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Hello, this is from bank customer care. Your account has suspicious activity.",
      "timestamp": "2026-01-31T10:00:00Z"
    },
    {
      "sender": "honeypot",
      "text": "What kind of suspicious activity?",
      "timestamp": "2026-01-31T10:01:00Z"
    }
  ],
  "metadata": {"channel": "Call", "language": "English", "locale": "IN"}
}
"@

Invoke-RestMethod -Uri "http://127.0.0.1:5000/ingest-message" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"; "x-api-key"="test-key-123"} `
  -Body $payload2
```

---

## List Active Sessions

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/sessions" `
  -Method Get `
  -Headers @{"x-api-key"="test-key-123"}
```

### cURL
```bash
curl http://127.0.0.1:5000/sessions -H "x-api-key: test-key-123"
```

**Expected Response:**
```json
{
  "status": "success",
  "sessions": [
    {
      "session_id": "demo-001",
      "state": "SUSPECTED",
      "message_count": 1,
      "scam_detected": true,
      "intelligence_ready": false,
      "created_at": "2026-01-31T10:00:00.123456"
    }
  ]
}
```

---

## Authentication Test (Should Fail)

### Without API Key
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/ingest-message" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"sessionId":"test","message":{"sender":"test","text":"test"}}'
```

**Expected Response:** `401 Unauthorized`

---

## Quick Test Script

Run the automated test script:

### Windows PowerShell
```powershell
.\test_api_request.ps1
```

### Python Test Suite
```bash
python integration_test.py
```

---

## API Keys

**Valid API Keys:**
- `test-key-123`
- `guvi-honeypot-key`

**Header Required:**
```
x-api-key: test-key-123
```

---

## Common Errors

### Error: "404 Not Found"
- **Cause:** You're trying to access `/` instead of actual endpoints
- **Solution:** Use `/health`, `/ingest-message`, or `/sessions`

### Error: "401 Unauthorized"
- **Cause:** Missing or invalid API key
- **Solution:** Add header: `x-api-key: test-key-123`

### Error: "400 Bad Request"
- **Cause:** Invalid payload format
- **Solution:** Ensure JSON has `sessionId`, `message` (with `sender`, `text`, `timestamp`), `conversationHistory`, and `metadata`

### Error: Connection refused
- **Cause:** Server not running
- **Solution:** Start server with `python app.py`

---

## GUVI Callback

The system automatically sends intelligence to:
```
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

This happens automatically when:
- 10+ messages exchanged, OR
- High-value entities found (UPI/bank/URLs), OR
- 3+ credential requests detected

Check logs for confirmation:
```
INFO:guvi_callback:[session-id] Callback successful: 200
```
