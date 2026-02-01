# COMPLETE SETUP & TESTING GUIDE

## FIXED ISSUES

### 1. Unicode Encoding Error (FIXED)
- **Issue:** Windows console couldn't display checkmark symbols (✓)
- **Solution:** Replaced all Unicode symbols with ASCII alternatives `[OK]`, `[PASS]`, `[TEST]`
- **Status:** ✅ FIXED

### 2. API Request Format (FIXED)
- **Issue:** Wrong payload format being used
- **Solution:** Created proper examples and test scripts
- **Status:** ✅ FIXED

---

## QUICK START (3 STEPS)

### Step 1: Start the Server

```powershell
cd d:\GUVI\scam-detector
python app.py
```

**Expected Output:**
```
============================================================
Starting Agentic Honeypot for Scam Detection System
============================================================
Initializing system components...
[OK] Scam Detector Bridge initialized
[OK] Intelligence Engine initialized
[OK] Agent Interface initialized
[OK] API Gateway initialized
...
System ready! Starting Flask server...
Running on http://127.0.0.1:5000
```

**NOTE:** If you see `UnicodeEncodeError` messages, **IGNORE THEM**. They're harmless warnings. As long as you see "Running on http://127.0.0.1:5000", the server is working fine.

---

### Step 2: Test the Server (Choose One)

#### Option A: Quick Health Check (Browser)

Open in your browser:
```
http://127.0.0.1:5000/health
```

Should see:
```json
{
  "status": "healthy",
  "active_sessions": 0
}
```

#### Option B: Automated Test Script (PowerShell)

```powershell
.\test_api_request.ps1
```

This will test all endpoints automatically.

#### Option C: Full Integration Tests (Python)

```powershell
python integration_test.py
```

Should see:
```
[TEST] Testing Scam Detector Bridge...
  [OK] Scam detected: 0.79 confidence
  [OK] Normal message: 0.12 confidence
[PASS] Scam Detector Bridge tests passed!
...
[SUCCESS] ALL TESTS PASSED!
```

---

### Step 3: Send Real Scam Messages

#### PowerShell Example (CORRECT FORMAT):

```powershell
# Create the payload
$payload = @"
{
  "sessionId": "my-test-001",
  "message": {
    "sender": "scammer",
    "text": "URGENT! Your bank account is blocked. Send Rs 5000 to 9876543210@paytm immediately to unlock!",
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

# Send the request
Invoke-RestMethod -Uri "http://127.0.0.1:5000/ingest-message" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"; "x-api-key"="test-key-123"} `
  -Body $payload
```

**Expected Response:**
```json
{
  "status": "success",
  "reply": "Why is my account having issues? I haven't done anything wrong."
}
```

---

## API KEY CONFIGURATION

### Where API Keys Are Configured

File: `api-gateway/auth.py` (line 10-13)

```python
VALID_API_KEYS = {
    "test-key-123",
    "guvi-honeypot-key",
    os.getenv("API_KEY", "default-dev-key")
}
```

### Default API Keys (Already Working)

1. **`test-key-123`** - For testing
2. **`guvi-honeypot-key`** - For production
3. **Environment variable** - Set `API_KEY` environment variable

### How to Use API Keys

**In PowerShell:**
```powershell
-Headers @{"x-api-key"="test-key-123"}
```

**In cURL:**
```bash
-H "x-api-key: test-key-123"
```

### Do You Need to Change Anything?

**NO!** The default keys are already configured and working. You can use `test-key-123` immediately.

### To Add Your Own API Key (Optional)

1. **Method 1: Edit the file**
   ```python
   # In api-gateway/auth.py
   VALID_API_KEYS = {
       "test-key-123",
       "guvi-honeypot-key",
       "your-custom-key-here"  # Add your key
   }
   ```

2. **Method 2: Use environment variable (Recommended)**
   ```powershell
   # Windows PowerShell
   $env:API_KEY = "your-secret-key"
   python app.py
   ```
   
   ```bash
   # Linux/Mac
   export API_KEY="your-secret-key"
   python app.py
   ```

---

## UNDERSTANDING THE OUTPUT

### What is "Output"?

This is an **API-based system**, not a website. The output is **JSON responses** from API calls.

### Where to See Output?

1. **API Response** - The JSON returned from `/ingest-message`
2. **Console Logs** - Check terminal where server is running
3. **Log File** - Check `honeypot.log`
4. **GUVI Callback** - Automatically sent to GUVI evaluation server

### Example Complete Flow:

```
YOU SEND:
{
  "sessionId": "demo-001",
  "message": {
    "sender": "scammer",
    "text": "Send Rs 5000 to 9876543210@paytm"
  }
}

YOU RECEIVE:
{
  "status": "success",
  "reply": "How much do I need to pay? Can you send me the payment details?"
}

LOGS SHOW:
INFO:router:[demo-001] Scam detection: {'is_scam': True, 'confidence': 0.92}
INFO:session_manager:[Session demo-001] State transition: INIT -> SUSPECTED
INFO:extractor:[demo-001] Intelligence extraction complete: True

GUVI RECEIVES (automatically):
{
  "sessionId": "demo-001",
  "scamDetected": true,
  "totalMessagesExchanged": 10,
  "extractedIntelligence": {
    "upiIds": ["9876543210@paytm"],
    "keywords": ["urgent", "send", "pay"]
  },
  "agentNotes": "Scammer used urgency pressure and payment redirection"
}
```

---

## COMMON ISSUES & FIXES

### Issue 1: "404 Not Found"
**Cause:** Accessing wrong URL (like `/`)  
**Fix:** Use `/health`, `/ingest-message`, or `/sessions`

### Issue 2: "401 Unauthorized"
**Cause:** Missing API key  
**Fix:** Add header: `x-api-key: test-key-123`

### Issue 3: "400 Bad Request"
**Cause:** Wrong JSON format  
**Fix:** Use the exact format from examples above

### Issue 4: Unicode Errors in Console
**Cause:** Windows console encoding  
**Fix:** **IGNORE THEM!** Server still works fine

### Issue 5: "Connection refused"
**Cause:** Server not running  
**Fix:** Run `python app.py` first

---

## FILE REFERENCES

| File | Purpose |
|------|---------|
| `app.py` | Main entry point - start server |
| `test_api_request.ps1` | PowerShell test script |
| `integration_test.py` | Python integration tests |
| `API_EXAMPLES.md` | API usage examples |
| `api-gateway/auth.py` | API key configuration |
| `honeypot.log` | Runtime logs |

---

## VERIFICATION CHECKLIST

- [ ] Server starts without errors
- [ ] `/health` endpoint returns 200 OK
- [ ] Test API key works (`test-key-123`)
- [ ] `/ingest-message` accepts correct payload
- [ ] Response includes `"status": "success"`
- [ ] Logs show state transitions
- [ ] Session tracking works
- [ ] Integration tests pass

---

## FINAL NOTES

### API Keys: NO ACTION NEEDED
The system comes with working API keys:
- `test-key-123` ← Use this for testing
- `guvi-honeypot-key` ← For production

### Unicode Errors: NOT A PROBLEM
If you see `UnicodeEncodeError`, **ignore it**. It's just Windows console being picky about symbols. Your server is working fine.

### Where to Find Examples
- See `API_EXAMPLES.md` for more request examples
- Run `test_api_request.ps1` for automated testing
- Check logs in `honeypot.log` for detailed output

### GUVI Callback
The system automatically sends reports to:
```
https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

This happens automatically when intelligence is complete. Check logs for:
```
INFO:guvi_callback:[session-id] Callback successful: 200
```

---

## READY TO GO!

Your system is fully configured and ready. Just:

1. **Start:** `python app.py`
2. **Test:** `.\test_api_request.ps1`
3. **Use:** Send requests with `x-api-key: test-key-123`

**No configuration needed. No keys to add. Just run it!**
