# 🚀 QUICK REFERENCE CARD

## Start the System
```bash
python app.py
```

## Test Everything
```bash
python integration_test.py
```

## Run Examples
```bash
python api_examples.py
```

---

## 📡 API Endpoints

### 1️⃣ Ingest Message
```bash
curl -X POST http://localhost:5000/ingest-message \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your account blocked! Pay 5000@paytm",
      "timestamp": "2026-01-31T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
  }'
```

### 2️⃣ Health Check
```bash
curl http://localhost:5000/health
```

### 3️⃣ List Sessions
```bash
curl http://localhost:5000/sessions -H "x-api-key: test-key-123"
```

---

## 🔑 API Keys
- `test-key-123`
- `guvi-honeypot-key`

---

## 🔄 State Machine
```
INIT → SUSPECTED → ENGAGING → INTEL_COMPLETE → REPORTED
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main entry point |
| `bridge.py` | Integration layer |
| `api-gateway/main.py` | REST endpoints |
| `api-gateway/router.py` | Orchestration |
| `api-gateway/session_manager.py` | State machine |
| `intelligence-engine/extractor.py` | Entity extraction |
| `intelligence-engine/guvi_callback.py` | Final callback |
| `detector.py` | Scam detection |

---

## 🕵️ Intelligence Extracted
- UPI IDs: `9876543210@paytm`
- Bank Accounts: `123456789012`
- Phone Numbers: `+919876543210`
- URLs: `http://fake-site.com`
- Keywords: `urgent`, `blocked`, `verify`

---

## 📤 GUVI Callback
**URL:** `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

Sent automatically when:
- ✅ Intelligence collection complete
- ✅ Exactly once per session
- ✅ Contains extracted entities + behavior summary

---

## 🧪 Testing

| Test | Command |
|------|---------|
| Integration | `python integration_test.py` |
| Detector | `python test_suite.py` |
| Quick | `python quick_test.py` |
| Verify | `python verify.py` |
| Examples | `python api_examples.py` |

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `README.md` | Main overview |
| `INTEGRATION_GUIDE.md` | Complete API docs |
| `DEPLOYMENT.md` | Deployment checklist |
| `SYSTEM_STATUS.md` | Current status |
| `QUICKSTART.md` | Quick reference |

---

## ⚡ Quick Troubleshooting

### Server won't start?
```bash
pip install -r requirements.txt
python --version  # Should be 3.8+
```

### Import errors?
```bash
cd scam-detector  # Run from project root
```

### Tests failing?
```bash
python integration_test.py  # Check detailed output
```

### API not responding?
```bash
curl http://localhost:5000/health
```

---

## 📊 Monitor Logs
```bash
tail -f honeypot.log
```

---

## 🎯 Success Indicators
- ✅ Health endpoint returns 200
- ✅ Tests pass without errors
- ✅ Sessions created and tracked
- ✅ Intelligence extracted correctly
- ✅ Callbacks logged successfully

---

**Need Help?** Check `INTEGRATION_GUIDE.md` for full documentation!
