# FinPilot AI — Portfolio Behavioral Integration & Isolation 🛡️

> **RMK INNOVATE Hackathon** | **Track:** Agentic & Generative AI  
> **Subsystem:** Behavioral Holdings Auditor (`backend/services/financial_iq_service.py`)

---

## 1. Safety & Ethical Mandate: Strict Separation from Real Execution

FinPilot AI is an educational planning and decision-support mentor. It **NEVER** connects to live brokerage order-routing APIs to place real-money market trades, and it **NEVER** alters user funds.

```
┌───────────────────────────────────────────────────────────┐
│               FINPILOT ISOLATION BOUNDARY                 │
│                                                           │
│  [User Portfolio Holdings]                                │
│           │                                               │
│           ▼ (Read-Only Behavioral Audit)                  │
│  ┌─────────────────────────────────┐                      │
│  │    Behavioral Pattern Auditor   │                      │
│  │  • Single-asset concentration?  │                      │
│  │  • Cash reserve adequacy?       │                      │
│  │  • Multi-asset spread?          │                      │
│  └─────────────────────────────────┘                      │
│           │                                               │
│           ▼ (Nudges 0-10 Score)                           │
│  [10-Dimension Financial IQ Ledger]                       │
│           │                                               │
│           ▼ (Pedagogical Guidance Only)                   │
│  [Educational Recommendations & Checklists]               │
│                                                           │
│  ═══════════════════════════════════════════════════════  │
│  ⛔ ZERO Real Broker Connections (Zerodha / Groww Live)   │
│  ⛔ ZERO Automated Trade Placements                       │
│  ⛔ ZERO Movement of Real Bank / Demat Funds              │
└───────────────────────────────────────────────────────────┘
```

---

## 2. Behavioral Audit Checks

When the user requests `/api/iq/portfolio-behavior`, the server analyzes asset weights:
1. **Concentration Risk:** If any single asset class exceeds 40% of total portfolio value, a concentration warning is flagged, and educational rebalancing advice is generated.
2. **Emergency Liquidity Buffer:** Compares liquid cash holdings against monthly expenses. If reserves exceed 3 months, a positive discipline nudge is logged.
3. **Multi-Asset Spread:** Evaluates whether holdings include equity, debt, and liquid instruments to mitigate systematic drawdowns.

All observations are delivered purely as pedagogical insights to empower the investor to make informed decisions for themselves.
