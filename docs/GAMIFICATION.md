# FinPilot AI — Gamification & Progression Architecture 🏆

> **RMK INNOVATE Hackathon** | **Track:** Agentic & Generative AI  
> **Subsystem:** Gamification Hub & Habit Formation Engine (`backend/services/gamification_service.py`)

---

## 1. Architectural Philosophy: The 4-Way Separation

A foundational principle in FinPilot AI is that engagement must never be conflated with financial competence:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   1. Game XP    │       │ 2. Simulation   │       │3. Financial IQ  │       │ 4. User Real    │
│    & Levels     │       │   Performance   │       │ (10 Dimensions) │       │    Portfolio    │
│                 │  ≠≠≠  │                 │  ≠≠≠  │                 │  ≠≠≠  │                 │
│  Effort, streaks│       │ Virtual cash,   │       │ Competence,     │       │ Holdings audited│
│  & learning quests      │ P&L, drawdown   │       │ risk discipline │       │ solely for habit│
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

1. **Game XP & Levels:** Measures learning effort, consistency, lesson completions, and quiz participation.
2. **Simulation Performance:** Measures virtual rupee returns inside historical scenarios.
3. **Financial IQ (0–1000 scale):** Authoritative measurement of actual financial intelligence across 10 dimensions.
4. **User Portfolio:** Real user holdings audited solely for behavioral patterns without executing trades.

---

## 2. Level Progression Model

Investors progress through 10 distinct competence titles based on cumulative XP:

| Level | Title | XP Range | Competence Focus |
|:---:|:---|:---:|:---|
| **1** | Financial Novice | 0 – 200 | Foundational literacy & budget awareness |
| **2** | Budget Tracker | 200 – 500 | Positive monthly surplus creation |
| **3** | Saver Apprentice | 500 – 900 | Emergency fund establishment (3 months) |
| **4** | Asset Allocator | 900 – 1,400 | Multi-asset diversification (Equity + Debt + Gold) |
| **5** | Market Explorer | 1,400 – 2,000 | Understanding volatility & market cycles |
| **6** | Compounder Specialist | 2,000 – 2,800 | Reverse SIP math & inflation calibration |
| **7** | Portfolio Strategist | 2,800 – 3,800 | Risk-capacity balancing & rebalancing triggers |
| **8** | Crisis Resilience Master | 3,800 – 5,000 | Staying invested through severe market drawdowns |
| **9** | Financial Freedom Pioneer | 5,000 – 7,000 | Safe withdrawal rate & corpus sustainability |
| **10** | Wealth Sage | 7,000+ | Long-term generational compounding & legacy |

---

## 3. Investor Badges of Honor

Badges reward deliberate, disciplined milestones rather than speculative luck:

- 🧭 **Self-Aware Investor (+100 XP):** Completed the baseline 10-dimension Financial IQ evaluation.
- 📈 **Eighth Wonder (+120 XP):** Mastered reverse annuity compounding mathematics.
- 🛡️ **Fort Knox Reserve (+150 XP):** Validated an emergency liquidity cushion of at least 3 months.
- 💎 **Iron Discipline (+180 XP):** Maintained high decision score during a panic crash simulation without selling at the bottom.
- 🌐 **Non-Correlated Mindset (+140 XP):** Constructed a multi-asset allocation spanning Equity, Debt, and Liquid cash.
- 🔥 **Consistency Titan (+200 XP):** Maintained a 7-day continuous learning streak.

---

## 4. Daily Market Intelligence Challenge

Every day, investors receive a single targeted question on behavioral finance, macroeconomic cycles, or regulatory literacy. Answering correctly awards +50 XP and extends the active learning streak; participating even when incorrect still awards +15 XP and immediate pedagogical explanation.
