# PowerShell script to test API endpoints
# Make sure the server is running: python app.py

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  API Gateway Test Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "[1] Testing /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/health" -Method Get
    Write-Host "  [OK] Server is healthy" -ForegroundColor Green
    Write-Host "  Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "  [ERROR] Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Message Ingestion (CORRECT FORMAT)
Write-Host "[2] Testing /ingest-message endpoint..." -ForegroundColor Yellow
$payload = @{
    sessionId = "demo-session-001"
    message = @{
        sender = "scammer"
        text = "Congratulations! You won a lottery of Rs 50000. Pay Rs 500 to 9876543210@paytm to claim. Click http://fake-lottery.com now!"
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
    conversationHistory = @()
    metadata = @{
        channel = "SMS"
        language = "English"
        locale = "IN"
    }
} | ConvertTo-Json -Depth 10

$headers = @{
    "Content-Type" = "application/json"
    "x-api-key" = "test-key-123"
}

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/ingest-message" -Method Post -Body $payload -Headers $headers
    Write-Host "  [OK] Message processed successfully" -ForegroundColor Green
    Write-Host "  Status: $($response.status)" -ForegroundColor Gray
    Write-Host "  Reply: $($response.reply)" -ForegroundColor Gray
} catch {
    Write-Host "  [ERROR] Message ingestion failed: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "  Response: $responseBody" -ForegroundColor Red
    }
}
Write-Host ""

# Test 3: Invalid Authentication
Write-Host "[3] Testing authentication (should fail)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/ingest-message" -Method Post -Body $payload
    Write-Host "  [ERROR] Authentication should have failed!" -ForegroundColor Red
} catch {
    Write-Host "  [OK] Authentication properly rejected (401)" -ForegroundColor Green
}
Write-Host ""

# Test 4: List Sessions
Write-Host "[4] Testing /sessions endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/sessions" -Method Get -Headers $headers
    Write-Host "  [OK] Sessions retrieved" -ForegroundColor Green
    Write-Host "  Active sessions: $($response.sessions.Count)" -ForegroundColor Gray
    if ($response.sessions.Count -gt 0) {
        foreach ($session in $response.sessions) {
            Write-Host "    - Session: $($session.session_id) | State: $($session.state) | Messages: $($session.message_count)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  [ERROR] Session listing failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tests Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
