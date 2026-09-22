# FinPilot AI — Historical Simulation Engine ⏳

> **RMK INNOVATE Hackathon** | **Track:** Agentic & Generative AI  
> **Subsystem:** Server-Authoritative Historical Trader (`backend/services/simulation_engine.py`)

---

## 1. Strict Anti-Future-Leakage Architecture

Standard educational trading simulators suffer from **future data leakage**: the client either loads the entire historical dataset up front or has access to full price series, allowing users to make artificially perfect trades with hindsight bias.

FinPilot AI strictly guarantees **Zero Future Data Leakage**:

```
Server Historical Database (2020-01-01 to 2020-12-31)
                    │
                    ▼
       ┌─────────────────────────┐
       │   Simulation Session    │  Current Step: T = 2020-03-23
       │ (Server Authoritative)  │  (Lockdown Crash Date)
       └─────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
[Revealed to Client]    [Strictly Hidden & Encrypted]
• Candles: T ≤ 2020-03-23  • Future Candles: T > 2020-03-23
• News:    T ≤ 2020-03-23  • Future Corporate Earnings
• Current Price: ₹880      • Future Rebound to ₹2,320
```

At simulation step $T$, the server-side timeline slicer executes:
```python
sliced_timeline = sc["timeline"][:idx + 1] # ZERO elements > idx
sliced_events = [ev for ev in sc["events"] if ev["date"] <= current_date]
```
The client literally cannot inspect future candles in the DOM, state, or network response.

---

## 2. Authentic Crisis Scenarios

1. **March 2020 Covid Shock & Liquidity Turnaround (Reliance Industries):**
   - **Context:** Nationwide lockdown, crude oil market crash, Sensex plunges 35% in weeks.
   - **Behavioral Challenge:** Maintaining composure, avoiding panic selling at the bottom (₹880), and executing disciplined value accumulation before the massive Meta-Jio liquidity partnership.
2. **2021 Tech Super-Cycle & Cloud Boom (Tata Consultancy Services):**
   - **Context:** Global enterprise digital transformation, cloud migrations, and high earnings multiples.
   - **Behavioral Challenge:** Managing risk without chasing late-stage euphoric market peaks.

---

## 3. Order Execution & Timeline Advancement

Investors execute 4 standard actions at each timeline period:
- **BUY:** Deducts virtual cash, updates average buy price and share quantity.
- **SELL:** Trims position, releases virtual cash, calculates realized P&L.
- **HOLD:** Remains invested undisturbed, testing patience through volatile drawdowns.
- **WAIT:** Stays in liquid cash waiting for better risk-reward entry.

Advancing the timeline advances $T \leftarrow T + 1$, revealing the next historical market candle and any breaking news that occurred on that date.
