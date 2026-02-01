# System Architecture Diagram

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                         EXTERNAL CLIENT / TESTER                          ║
║                    (Sends scam messages for analysis)                     ║
╚═══════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ HTTP POST /ingest-message
                                    │ Header: x-api-key
                                    ↓
╔═══════════════════════════════════════════════════════════════════════════╗
║                           API GATEWAY LAYER                               ║
║ ┌─────────────────────────────────────────────────────────────────────┐   ║
║ │  main.py (Flask REST API)                                           │   ║
║ │  • POST /ingest-message    (Main endpoint)                          │   ║
║ │  • GET  /health            (System health check)                    │   ║
║ │  • GET  /sessions          (List active sessions)                   │   ║
║ └─────────────────────────────────────────────────────────────────────┘   ║
║                                    │                                       ║
║                                    ↓                                       ║
║ ┌─────────────────────────────────────────────────────────────────────┐   ║
║ │  auth.py (Authentication)                                           │   ║
║ │  • Validates x-api-key header                                       │   ║
║ │  • Returns 401 if invalid                                           │   ║
║ └─────────────────────────────────────────────────────────────────────┘   ║
║                                    │                                       ║
║                                    ↓                                       ║
║ ┌─────────────────────────────────────────────────────────────────────┐   ║
║ │  session_manager.py (State Machine)                                 │   ║
║ │  • Creates/retrieves session                                        │   ║
║ │  • Tracks conversation history                                      │   ║
║ │  • Manages state: INIT → SUSPECTED → ENGAGING →                    │   ║
║ │                   INTEL_COMPLETE → REPORTED                         │   ║
║ └─────────────────────────────────────────────────────────────────────┘   ║
║                                    │                                       ║
║                                    ↓                                       ║
║ ┌─────────────────────────────────────────────────────────────────────┐   ║
║ │  router.py (Orchestration)                                          │   ║
║ │  • Routes requests to modules                                       │   ║
║ │  • Coordinates detection → intelligence → callback                  │   ║
║ │  • Handles latency budgeting (3s timeout)                           │   ║
║ │  • Returns reply to caller                                          │   ║
║ └─────────────────────────────────────────────────────────────────────┘   ║
╚═══════════════════════════════════════════════════════════════════════════╝
                   │                                  │
                   │                                  │
         ┌─────────┴──────────┐          ┌───────────┴──────────┐
         ↓                    │          │                      ↓
╔════════════════════╗         │          │         ╔═══════════════════════╗
║  INTEGRATION       ║         │          │         ║  INTEGRATION          ║
║  BRIDGE            ║         │          │         ║  BRIDGE               ║
║  (bridge.py)       ║         │          │         ║  (bridge.py)          ║
╚════════════════════╝         │          │         ╚═══════════════════════╝
         │                    │          │                      │
         ↓                    │          │                      ↓
╔════════════════════╗         │          │         ╔═══════════════════════╗
║  SCAM DETECTOR     ║         │          │         ║  INTELLIGENCE ENGINE  ║
║  (Existing Module) ║         │          │         ║  (New Module)         ║
║                    ║         │          │         ║                       ║
║ ┌────────────────┐ ║         │          │         ║ ┌───────────────────┐ ║
║ │ detector.py    │ ║         │          │         ║ │ extractor.py      │ ║
║ │ • Validates    │ ║         │          │         ║ │ • Extracts UPI    │ ║
║ │ • Orchestrates │ ║         │          │         ║ │ • Extracts banks  │ ║
║ └────────────────┘ ║         │          │         ║ │ • Extracts phones │ ║
║         │          ║         │          │         ║ │ • Extracts URLs   │ ║
║         ↓          ║         │          │         ║ │ • Extracts words  │ ║
║ ┌────────────────┐ ║         │          │         ║ └───────────────────┘ ║
║ │ rules.py       │ ║         │          │         ║          │            ║
║ │ • Pattern match│ ║         │          │         ║          ↓            ║
║ │ • Regex detect │ ║         │          │         ║ ┌───────────────────┐ ║
║ │ • Multi-turn   │ ║         │          │         ║ │ patterns.py       │ ║
║ └────────────────┘ ║         │          │         ║ │ • 15+ regex       │ ║
║         │          ║         │          │         ║ │ • 50+ keywords    │ ║
║         ↓          ║         │          │         ║ │ • 6 categories    │ ║
║ ┌────────────────┐ ║         │          │         ║ └───────────────────┘ ║
║ │ scorer.py      │ ║         │          │         ║          │            ║
║ │ • Progressive  │ ║         │          │         ║          ↓            ║
║ │ • Confidence   │ ║         │          │         ║ ┌───────────────────┐ ║
║ │ • Threshold    │ ║         │          │         ║ │ reporter.py       │ ║
║ └────────────────┘ ║         │          │         ║ │ • Aggregates data │ ║
║         │          ║         │          │         ║ │ • Generates report│ ║
║         ↓          ║         │          │         ║ │ • Checks complete │ ║
║ ┌────────────────┐ ║         │          │         ║ └───────────────────┘ ║
║ │ signals.py     │ ║         │          │         ║          │            ║
║ │ • Signal types │ ║         │          │         ║          ↓            ║
║ │ • Weights      │ ║         │          │         ║ ┌───────────────────┐ ║
║ │ • Categories   │ ║         │          │         ║ │ guvi_callback.py  │ ║
║ └────────────────┘ ║         │          │         ║ │ • POST to GUVI    │ ║
║                    ║         │          │         ║ │ • Send once only  │ ║
║ Returns:           ║         │          │         ║ │ • 5s timeout      │ ║
║ • scamDetected     ║         │          │         ║ │ • Log result      │ ║
║ • confidence       ║         │          │         ║ └───────────────────┘ ║
║ • signals          ║         │          │         ║          │            ║
║ • explanation      ║         │          │         ║          │            ║
╚════════════════════╝         │          │         ╚══════════│════════════╝
         │                    │          │                    │
         │                    │          │                    │
         └────────────────────┘          └────────────────────┘
                   │                                  │
                   ↓                                  ↓
         [Agent Reply Generated]         [Intelligence Complete?]
                   │                                  │
                   │                                  ↓
                   │                     [If YES: Trigger Callback]
                   │                                  │
                   └──────────────┬───────────────────┘
                                  ↓
                        [Return Reply to Caller]
                                  │
                                  ↓
╔═══════════════════════════════════════════════════════════════════════════╗
║                        GUVI EVALUATION ENDPOINT                           ║
║      https://hackathon.guvi.in/api/updateHoneyPotFinalResult             ║
║                                                                           ║
║  Receives (once per session):                                            ║
║  • sessionId                                                              ║
║  • scamDetected (bool)                                                    ║
║  • totalMessagesExchanged                                                 ║
║  • extractedIntelligence (UPIs, accounts, URLs, phones, keywords)        ║
║  • agentNotes (behavior summary)                                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## Data Flow Example

```
1. Client sends message:
   POST /ingest-message
   {
     "sessionId": "abc123",
     "message": {
       "sender": "scammer",
       "text": "Pay 5000 to 9876543210@paytm now!"
     }
   }

2. API Gateway authenticates (auth.py)
   ✓ API key valid

3. Session Manager creates/retrieves session (session_manager.py)
   • Current state: INIT
   • Stores message in history

4. Router orchestrates (router.py):
   
   a) Calls Scam Detector (via bridge)
      → detector.py analyzes text
      → rules.py detects patterns
      → scorer.py calculates confidence
      → Returns: scamDetected=True, confidence=0.85
   
   b) Session state: INIT → SUSPECTED → ENGAGING
   
   c) Generates reply (via agent interface)
      → Returns: "How much should I pay?"
   
   d) Calls Intelligence Engine
      → extractor.py processes conversation
      → Finds: UPI ID "9876543210@paytm"
      → Finds keywords: "pay", "now"
      → reporter.py checks if complete
      → Returns: complete=False (need more messages)

5. Response to client:
   {
     "status": "success",
     "reply": "How much should I pay?"
   }

6. After 10 messages...
   
   Intelligence Engine marks complete:
   • State: ENGAGING → INTEL_COMPLETE
   
   Callback triggered:
   • guvi_callback.py sends to GUVI
   • Payload includes all extracted intelligence
   • State: INTEL_COMPLETE → REPORTED

7. Session complete ✓
```

## State Machine Flow

```
┌────────────┐
│    INIT    │  New session created
└─────┬──────┘
      │
      │ (scam detected)
      ↓
┌────────────┐
│ SUSPECTED  │  Scam indicators found
└─────┬──────┘
      │
      │ (continue conversation)
      ↓
┌────────────┐
│  ENGAGING  │  Actively conversing with scammer
└─────┬──────┘
      │
      │ (intelligence criteria met)
      ↓
┌────────────┐
│ INTEL_     │  Sufficient intelligence collected
│ COMPLETE   │
└─────┬──────┘
      │
      │ (callback sent)
      ↓
┌────────────┐
│  REPORTED  │  Final callback sent to GUVI
└────────────┘
```

## Module Interaction Matrix

```
                │ API    │ Scam    │ Intel   │ Bridge  │ GUVI
                │ Gateway│ Detector│ Engine  │         │ API
────────────────┼────────┼─────────┼─────────┼─────────┼──────
API Gateway     │   ●    │    ○    │    ○    │    ●    │
Scam Detector   │   ○    │    ●    │         │    ●    │
Intel Engine    │   ○    │         │    ●    │    ●    │  ●
Bridge          │   ●    │    ●    │    ●    │    ●    │
GUVI API        │        │         │    ●    │         │  ●

● = Direct interaction
○ = Indirect (via Bridge/Router)
```

## Key Design Principles

1. **Separation of Concerns**
   - API Gateway: HTTP handling only
   - Scam Detector: Detection logic only
   - Intelligence Engine: Extraction only
   - Bridge: Interface adaptation only

2. **No Business Logic Mixing**
   - Router has NO detection logic
   - Gateway has NO intelligence logic
   - Each module is self-contained

3. **Deterministic Behavior**
   - Same input → same output
   - State transitions are explicit
   - No hidden side effects

4. **Production Ready**
   - Comprehensive error handling
   - Logging at all levels
   - Timeout protection
   - Graceful degradation
