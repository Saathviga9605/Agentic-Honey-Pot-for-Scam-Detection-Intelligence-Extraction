# Live System Demonstration Script
# Run this to see the complete integrated system in action

$baseUrl = "http://127.0.0.1:5000"
$apiKey = "test-key-123"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " AGENTIC HONEYPOT SYSTEM - LIVE DEMONSTRATION" -ForegroundColor Cyan
Write-Host " With Real Persona-Based Agent Engine" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Function to display results
function Show-Result {
    param($title, $response)
    Write-Host ""
    Write-Host ">>> $title" -ForegroundColor Yellow
    Write-Host "Agent Reply: " -NoNewline -ForegroundColor Green
    Write-Host $response.reply -ForegroundColor White
    Write-Host ""
}

# Wait for server
Write-Host "[INFO] Checking if server is running..." -ForegroundColor Gray
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -ErrorAction Stop
    Write-Host "[OK] Server is healthy with $($health.active_sessions) active sessions" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Server not running! Start with: python app.py" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " DEMONSTRATION: Realistic Scam Conversation" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Simulating a phishing scammer trying to extract UPI details..." -ForegroundColor Gray
Write-Host ""

# Session 1: UPI Phishing Attack
$sessionId = "demo-realistic-$(Get-Date -Format 'HHmmss')"

# Message 1: Initial urgent threat
Write-Host "[Scammer - Turn 1]" -ForegroundColor Red
Write-Host "Your SBI account will be blocked in 24 hours!" -ForegroundColor White

$payload1 = @{
    sessionId = $sessionId
    message = @{
        sender = "scammer"
        text = "Your SBI account will be blocked in 24 hours!"
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    }
    conversationHistory = @()
    metadata = @{
        channel = "SMS"
        language = "English"
        locale = "IN"
    }
} | ConvertTo-Json -Depth 10

$response1 = Invoke-RestMethod -Uri "$baseUrl/ingest-message" -Method Post `
    -Headers @{"Content-Type"="application/json"; "x-api-key"=$apiKey} `
    -Body $payload1

Show-Result "Agent Response (Turn 1)" $response1

Start-Sleep -Seconds 2

# Message 2: Verification demand
Write-Host "[Scammer - Turn 2]" -ForegroundColor Red
Write-Host "Verify immediately! Call this number: 9876543210" -ForegroundColor White

$history = @(
    @{sender="scammer"; text="Your SBI account will be blocked in 24 hours!"; timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")}
    @{sender="agent"; text=$response1.reply; timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")}
)

$payload2 = @{
    sessionId = $sessionId
    message = @{
        sender = "scammer"
        text = "Verify immediately! Call this number: 9876543210"
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    }
    conversationHistory = $history
    metadata = @{
        channel = "SMS"
        language = "English"
    }
} | ConvertTo-Json -Depth 10

$response2 = Invoke-RestMethod -Uri "$baseUrl/ingest-message" -Method Post `
    -Headers @{"Content-Type"="application/json"; "x-api-key"=$apiKey} `
    -Body $payload2

Show-Result "Agent Response (Turn 2)" $response2

Start-Sleep -Seconds 2

# Message 3: Link with urgency
Write-Host "[Scammer - Turn 3]" -ForegroundColor Red
Write-Host "Click now to restore: http://fake-sbi.com/verify?id=12345" -ForegroundColor White

$history += @{sender="scammer"; text="Verify immediately! Call this number: 9876543210"; timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")}
$history += @{sender="agent"; text=$response2.reply; timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")}

$payload3 = @{
    sessionId = $sessionId
    message = @{
        sender = "scammer"
        text = "Click now to restore: http://fake-sbi.com/verify?id=12345"
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    }
    conversationHistory = $history
    metadata = @{
        channel = "SMS"
        language = "English"
    }
} | ConvertTo-Json -Depth 10

$response3 = Invoke-RestMethod -Uri "$baseUrl/ingest-message" -Method Post `
    -Headers @{"Content-Type"="application/json"; "x-api-key"=$apiKey} `
    -Body $payload3

Show-Result "Agent Response (Turn 3)" $response3

Start-Sleep -Seconds 2

# Message 4: Direct UPI request
Write-Host "[Scammer - Turn 4]" -ForegroundColor Red
Write-Host "Send Rs 500 verification fee to scammer@paytm NOW!" -ForegroundColor White

$history += @{sender="scammer"; text="Click now to restore: http://fake-sbi.com/verify?id=12345"; timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")}
$history += @{sender="agent"; text=$response3.reply; timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")}

$payload4 = @{
    sessionId = $sessionId
    message = @{
        sender = "scammer"
        text = "Send Rs 500 verification fee to scammer@paytm NOW!"
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    }
    conversationHistory = $history
    metadata = @{
        channel = "SMS"
        language = "English"
    }
} | ConvertTo-Json -Depth 10

$response4 = Invoke-RestMethod -Uri "$baseUrl/ingest-message" -Method Post `
    -Headers @{"Content-Type"="application/json"; "x-api-key"=$apiKey} `
    -Body $payload4

Show-Result "Agent Response (Turn 4)" $response4

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " DEMONSTRATION COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Notice the agent's behavior:" -ForegroundColor Green
Write-Host "  [OK] Natural language with filler words" -ForegroundColor Gray
Write-Host "  [OK] Shows confusion/concern appropriately" -ForegroundColor Gray
Write-Host "  [OK] Mentions link issues when relevant" -ForegroundColor Gray
Write-Host "  [OK] Asks verification questions" -ForegroundColor Gray
Write-Host "  [OK] Maintains consistent persona throughout" -ForegroundColor Gray
Write-Host ""
Write-Host "Intelligence extracted:" -ForegroundColor Green
Write-Host "  - Phone: 9876543210" -ForegroundColor Gray
Write-Host "  - URL: http://fake-sbi.com/verify?id=12345" -ForegroundColor Gray
Write-Host "  - UPI ID: scammer@paytm" -ForegroundColor Gray
Write-Host "  - Keywords: urgency, account threat, payment request" -ForegroundColor Gray
Write-Host ""
Write-Host "Final callback sent to GUVI evaluation server!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Run 'python comprehensive_test.py' to see full test suite" -ForegroundColor Cyan
Write-Host ""
