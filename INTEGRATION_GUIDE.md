# Agentic Honeypot for Scam Detection & Intelligence Extraction

A production-ready backend system for defensive cybersecurity research that detects scams, orchestrates conversation sessions, extracts intelligence, and reports findings to evaluation endpoints.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ auth.py      │  │ router.py    │  │ session_manager │  │
│  │ (API Key)    │  │ (Orchestrate)│  │ (State Machine) │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    ┌──────────────┐
                    │   bridge.py  │
                    │ (Integration)│
                    └──────────────┘
                           ↓
        ┌──────────────────┴──────────────────┐
        ↓                                      ↓
┌──────────────────┐              ┌────────────────────────┐
│ SCAM DETECTOR    │              │ INTELLIGENCE ENGINE    │
│ (Existing)       │              │                        │
│ - detector.py    │              │ - extractor.py         │
│ - rules.py       │              │ - patterns.py          │
│ - scorer.py      │              │ - reporter.py          │
│ - signals.py     │              │ - guvi_callback.py     │
└──────────────────┘              └────────────────────────┘
                                              ↓
                                  ┌──────────────────────┐
                                  │ GUVI Evaluation API  │
                                  │ (Final Callback)     │
                                  └──────────────────────┘
```

## 📁 Project Structure

```
scam-detector/
├── app.py                          # Main entry point
├── bridge.py                       # Integration layer
├── requirements.txt                # Dependencies
│
├── api-gateway/                    # REST API & Orchestration
│   ├── __init__.py
│   ├── main.py                     # Flask app & endpoints
│   ├── auth.py                     # API key validation
│   ├── router.py                   # Request orchestration
│   └── session_manager.py          # Session state machine
│
├── intelligence-engine/            # Intelligence Extraction
│   ├── __init__.py
│   ├── extractor.py                # Entity extraction logic
│   ├── patterns.py                 # Regex patterns & keywords
│   ├── reporter.py                 # Report generation
│   └── guvi_callback.py            # Final callback sender
│
├── contracts/                      # API Contracts
│   ├── input_schema.json           # Request schema
│   └── output_schema.json          # Response schema
│
└── [Existing Files]                # Original scam detector
    ├── detector.py
    ├── rules.py
    ├── scorer.py
    └── signals.py
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000`

### 3. Test the API

```bash
curl -X POST http://localhost:5000/ingest-message \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "sessionId": "test-session-001",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked immediately! Send payment to 9876543210@paytm",
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

## 📡 API Endpoints

### POST /ingest-message
**Ingest incoming scam messages**

**Headers:**
- `x-api-key`: Valid API key (required)

**Request Body:**
```json
{
  "sessionId": "abc123",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked",
    "timestamp": "2026-01-31T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Why is my account being suspended?"
}
```

### GET /health
**Health check endpoint**

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 5
}
```

### GET /sessions
**List active sessions (admin)**

**Headers:**
- `x-api-key`: Valid API key (required)

**Response:**
```json
{
  "status": "success",
  "sessions": [
    {
      "session_id": "abc123",
      "state": "ENGAGING",
      "message_count": 8,
      "scam_detected": true,
      "created_at": "2026-01-31T10:00:00Z",
      "intelligence_ready": false
    }
  ]
}
```

## 🔐 Authentication

Valid API keys (configurable):
- `test-key-123`
- `guvi-honeypot-key`
- Environment variable: `API_KEY`

Include in request header:
```
x-api-key: test-key-123
```

## 🔄 Session State Machine

Each session transitions through these states:

```
INIT → SUSPECTED → ENGAGING → INTEL_COMPLETE → REPORTED
```

| State | Description |
|-------|-------------|
| `INIT` | New session created |
| `SUSPECTED` | Scam detected in message |
| `ENGAGING` | Actively conversing with scammer |
| `INTEL_COMPLETE` | Sufficient intelligence collected |
| `REPORTED` | Final callback sent to GUVI |

## 🕵️ Intelligence Extraction

### Entities Detected
- **UPI IDs**: `9876543210@paytm`, `user@okaxis`
- **Bank Accounts**: 9-18 digit account numbers
- **Phone Numbers**: Indian (+91) and international formats
- **URLs**: Phishing links
- **IFSC Codes**: Bank routing codes

### Suspicious Keywords Categories
- **Urgency**: urgent, immediately, expire
- **Threats**: block, suspend, legal action
- **Verification**: verify, confirm, authenticate
- **Payment**: pay, transfer, refund
- **Impersonation**: bank, official, government
- **Credentials**: password, OTP, CVV

### Confidence Filtering
Only entities appearing **2+ times** are included in final report to reduce noise.

## 📤 Final Callback

When intelligence collection is complete (`INTEL_COMPLETE` state), the system automatically sends a callback to:

**Endpoint:** `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

**Payload:**
```json
{
  "sessionId": "abc123",
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": ["123456789012"],
    "upiIds": ["9876543210@paytm"],
    "phishingLinks": ["http://fake-bank.com"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "blocked", "verify"]
  },
  "agentNotes": "Scammer used urgency pressure and payment redirection tactics across 18 messages"
}
```

**Guarantees:**
- Sent exactly **once** per session
- Only after `INTEL_COMPLETE` state
- 5-second timeout
- Failure logged but doesn't crash system

## ⚙️ Configuration

### Environment Variables

```bash
# Server configuration
export HOST=0.0.0.0
export PORT=5000
export DEBUG=false

# API key
export API_KEY=your-secure-key-here
```

### Latency Budgeting

Agent response timeout: **3 seconds**

If exceeded, fallback reply is sent:
```
"Please wait, I'm checking this."
```

## 🧪 Intelligence Completion Criteria

Intelligence collection is marked complete when:

1. **10+ messages** exchanged, OR
2. **High-value entities** found (UPI, bank account, URLs), OR
3. **3+ credential requests** detected

## 🏗️ Module Responsibilities

### API Gateway (`api-gateway/`)
- ✅ Expose REST endpoints
- ✅ Validate API keys
- ✅ Manage session lifecycle
- ✅ Route requests between modules
- ✅ Return agent replies

### Intelligence Engine (`intelligence-engine/`)
- ✅ Extract entities (UPI, accounts, URLs)
- ✅ Detect suspicious keywords
- ✅ Generate behavior summaries
- ✅ Determine completion status
- ✅ Send final callback to GUVI

### Bridge (`bridge.py`)
- ✅ Integrate with existing scam detector
- ✅ Adapt interfaces for orchestration
- ✅ Mock agent replies (placeholder)

## 🔍 Example Flow

1. **Request arrives** at `/ingest-message` with API key
2. **Authentication** validates key
3. **Session created/retrieved** with state tracking
4. **Message stored** in conversation history
5. **Scam detection** analyzes text
6. **State transition** if scam detected
7. **Agent reply generated** (with timeout handling)
8. **Intelligence extraction** from conversation
9. **Completion check** determines if ready
10. **Final callback** sent to GUVI (if complete)
11. **Response returned** to caller

## 🛡️ Safety & Ethics

- ✅ No interaction with real users
- ✅ No real transactions or credentials
- ✅ Purely analytical and defensive
- ✅ Designed for cybersecurity research only

## 📊 Logging

Comprehensive logging to:
- **Console**: Real-time monitoring
- **File**: `honeypot.log` for persistence

Log levels:
- `INFO`: Normal operations
- `WARNING`: Authentication failures, timeouts
- `ERROR`: Processing errors, callback failures

## 🧑‍💻 Development

### Run Tests
```bash
python test_suite.py
```

### Check Implementation
```bash
python verify.py
```

### Quick Test
```bash
python quick_test.py
```

## 📝 API Contract Validation

JSON schemas available in `contracts/`:
- `input_schema.json`: Request validation
- `output_schema.json`: Response validation

## 🎯 Success Criteria

✅ Sessions tracked correctly  
✅ State transitions visible and logged  
✅ Intelligence extracted accurately  
✅ Callback sent exactly once  
✅ API returns fast and stable responses  
✅ Clean separation of concerns  
✅ Production-ready code quality  

## 🚨 Error Handling

- Invalid API key → `401 Unauthorized`
- Missing fields → `400 Bad Request`
- Processing errors → `500 Internal Server Error`
- Callback failures → Logged, session continues

## 📞 Support

For issues or questions about this implementation:
1. Check logs in `honeypot.log`
2. Verify API key is valid
3. Ensure all dependencies installed
4. Review session state transitions

---

**Built for GUVI Hackathon - Defensive Cybersecurity Research**
