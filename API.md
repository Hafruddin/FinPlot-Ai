# FinPilot AI — REST API Reference 🔌

> **RMK INNOVATE Hackathon** | **Track:** Agentic & Generative AI  
> **Base URL:** `http://localhost:8000` (Local) | `https://finpilot.netlify.app` (Production)

---

## Table of Contents
1. [Authentication & Profile](#1-authentication--profile)
2. [Multi-Agent Planning Pipeline](#2-multi-agent-planning-pipeline)
3. [RAG Knowledge Base](#3-rag-knowledge-base)
4. [AI Financial Tutor](#4-ai-financial-tutor)
5. [Interactive What-If Simulation](#5-interactive-what-if-simulation)
6. [Financial IQ 6-Pillar Assessment](#6-financial-iq-6-pillar-assessment)
7. [Portfolio Guardian & Allocation Sentinel](#7-portfolio-guardian--allocation-sentinel)
8. [System & Market APIs](#8-system--market-apis)

---

## 1. Authentication & Profile

### `POST /api/auth/signup`
Registers a new user account with direct bcrypt password hashing.
- **Request Body:**
  ```json
  {
    "name": "Arjun Patel",
    "email": "arjun@finpilot.ai",
    "password": "SecurePassword123!"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

### `POST /api/auth/login`
Authenticates existing credentials and returns JWT bearer token.
- **Request Body:**
  ```json
  {
    "email": "arjun@finpilot.ai",
    "password": "SecurePassword123!"
  }
  ```
- **Response (`200 OK`):** Same as signup.

### `GET /api/auth/me` *(or `/api/user/profile`)*
Returns authenticated user identity, goals, and verified financial IQ.
- **Headers:** `Authorization: Bearer <token>`
- **Response (`200 OK`):**
  ```json
  {
    "id": 1,
    "name": "Arjun Patel",
    "email": "arjun@finpilot.ai",
    "financial_iq": 750,
    "paper_cash": 100000.0,
    "goals": {
      "goal_type": "Wealth Accumulation & Freedom",
      "target_amount": 5000000.0,
      "duration_years": 10
    }
  }
  ```

---

## 2. Multi-Agent Planning Pipeline

### `POST /api/agents/run`
Executes the full 7-agent DAG orchestration pipeline (`ProfileAgent` $\rightarrow$ `GoalAgent` $\rightarrow$ `RiskAgent` $\rightarrow$ `KnowledgeAgent` $\rightarrow$ `SimulationAgent` $\rightarrow$ `StrategyAgent` $\rightarrow$ `ExplanationAgent`).

- **Request Body:**
  ```json
  {
    "name": "Arjun Patel",
    "age": 21,
    "monthly_income": 30000.0,
    "monthly_expenses": 20000.0,
    "current_savings": 50000.0,
    "monthly_investment_capacity": 5000.0,
    "target_corpus": 5000000.0,
    "horizon_years": 10,
    "risk_profile": "moderate",
    "expected_return": 12.0
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "run_id": "run_042a850fe1f9",
    "status": "COMPLETED",
    "executed_agents_count": 7,
    "trace": [
      {
        "agent_name": "ProfileAgent",
        "responsibility": "Validates cash flow, mandatory expenses, and investable capacity.",
        "status": "completed",
        "duration_ms": 0.37,
        "input_summary": "{...}",
        "output_summary": "{...}",
        "evidence": "Early Career Foundation"
      }
    ],
    "results": {
      "profile": { "surplus": 10000.0, "validated_monthly_capacity": 5000.0 },
      "goal": { "inflation_adjusted_target": 8954238.0 },
      "risk": { "target_asset_allocation": { "Equity": 65, "Debt": 20, "Cash/Liquid": 10, "Gold": 5 } },
      "simulation": { "base_case_required_sip": 21521 },
      "strategy": { "monthly_shortfall": 16521.0 },
      "explanation": {
        "what": "To accumulate ₹5,000,000 over 10 years, your baseline monthly SIP requirement is ₹21,521/month.",
        "why": "Calculated using reverse annuity due solver with 12% expected annual return.",
        "citations": [ "SEBI Investor Education", "AMFI Knowledge Center" ]
      }
    }
  }
  ```

---

## 3. RAG Knowledge Base

### `POST /api/rag/query`
Queries the regulatory financial knowledge base using TF-IDF + BM25 keyword overlap.
- **Request Body:**
  ```json
  {
    "query": "Why direct mutual fund plans have lower expense ratio?",
    "top_k": 2
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "query": "Why direct mutual fund plans have lower expense ratio?",
    "count": 2,
    "results": [
      {
        "doc_id": "amfi_ter_direct_vs_regular",
        "title": "Mutual Fund Expense Ratios: Direct vs Regular",
        "source": "Association of Mutual Funds in India (AMFI)",
        "url": "https://www.amfiindia.com/investor-corner/knowledge-center",
        "section": "Cost Transparency & Investor Protection",
        "score": 1.48
      }
    ]
  }
  ```

### `GET /api/rag/documents`
Lists all 8 curated documents in the regulatory knowledge corpus.

---

## 4. AI Financial Tutor

### `POST /api/tutor/chat` *(or `/api/copilot/chat`)*
Generates a structured educational response with intent detection, pedagogical takeaways, real-world examples, and verified regulatory citations.

- **Request Body:**
  ```json
  {
    "message": "What is the difference between direct and regular mutual funds?"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "intent": "MUTUAL_FUND_COSTS",
    "answer": "Direct plans bypass distributor commissions, reducing annual expense ratio...",
    "summary": "Direct plans eliminate distributor commissions.",
    "key_takeaways": [
      "Direct plans save 0.5%–1.2% in annual TER.",
      "Over 20 years, this difference can amount to 15–20% higher terminal wealth."
    ],
    "example": "On a ₹10,000/mo SIP over 20 years, a 1% TER difference equals ₹18 Lakh in fee leakage.",
    "citations": [
      {
        "title": "Mutual Fund Expense Ratios: Direct vs Regular",
        "source": "Association of Mutual Funds in India (AMFI)",
        "url": "https://www.amfiindia.com/investor-corner/knowledge-center"
      }
    ],
    "limitations": "Educational decision-support tool; not personalized investment advice.",
    "provider": "deterministic_grounded"
  }
  ```

---

## 5. Interactive What-If Simulation

### `POST /api/simulation/whatif`
Quantifies the exact mathematical impact of altering investment timelines or savings amounts.

- **Request Body:**
  ```json
  {
    "target_amount": 5000000.0,
    "current_savings": 50000.0,
    "previous_horizon_years": 10,
    "new_horizon_years": 15,
    "annual_return": 0.12,
    "monthly_capacity": 5000.0
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "previous_required_sip": 21521,
    "new_required_sip": 9657,
    "sip_difference": 11864,
    "sip_reduction_pct": 55.1,
    "previous_total_contributed": 2582520,
    "new_total_contributed": 1738260,
    "previous_growth_gain": 2417480,
    "new_growth_gain": 3261740,
    "what_changed_explanation": "Extending timeline from 10 to 15 years reduces required monthly SIP by ₹11,864 (-55.1%).",
    "educational_takeaway": "Time in the market outperforms timing the market: 5 additional years cuts required out-of-pocket savings in half."
  }
  ```

---

## 6. Financial IQ 6-Pillar Assessment

### `GET /api/iq/questions`
Fetches the 8 multi-dimensional quiz questions across the 6 competency pillars.

### `POST /api/iq/evaluate`
Scores answers against the 6 pillars and updates the user's Financial IQ.
- **Request Body:**
  ```json
  {
    "answers": {
      "q_know_1": "B",
      "q_know_2": "B",
      "q_risk_1": "C",
      "q_risk_2": "B",
      "q_inf_1": "C",
      "q_goal_1": "B",
      "q_div_1": "B",
      "q_dec_1": "B"
    }
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "total_score": 100.0,
    "scale_maximum": 100,
    "normalized_1000_score": 1000,
    "tier_name": "Master Investor",
    "tier_badge": "Mastery (Top Tier)",
    "dimensions": {
      "knowledge": { "score": 30.0, "max": 30.0, "label": "Financial Knowledge" },
      "risk": { "score": 20.0, "max": 20.0, "label": "Risk Understanding" },
      "inflation": { "score": 15.0, "max": 15.0, "label": "Inflation Understanding" },
      "goals": { "score": 15.0, "max": 15.0, "label": "Goal Planning" },
      "diversification": { "score": 10.0, "max": 10.0, "label": "Diversification" },
      "decision_making": { "score": 10.0, "max": 10.0, "label": "Decision Making" }
    },
    "strengths": [ "Financial Knowledge Mastery (30/30 pts)", "Risk Understanding Mastery (20/20 pts)" ],
    "weak_areas": [ "None identified! Excellent holistic financial competency." ],
    "recommended_learning": [ "Advanced Wealth Structuring & Tax Optimization" ]
  }
  ```

---

## 7. Portfolio Guardian & Allocation Sentinel

### `GET /api/portfolio/guardian`
Analyzes current equity/debt/cash holdings against benchmark target allocations.
- **Query Params:** `portfolio_value=300000&current_equity=237000&current_debt=45000&current_cash=18000&risk_tolerance=moderate`
- **Response (`200 OK`):**
  ```json
  {
    "total_portfolio_value": 300000.0,
    "risk_profile": "moderate",
    "drift_status": "MODERATE_DRIFT",
    "headline": "Moderate Allocation Drift (+9.0%)",
    "equity_drift_pct": 9.0,
    "health_score": 82,
    "review_recommended": true,
    "target_allocation": { "Equity": 70.0, "Debt": 25.0, "Cash": 5.0 },
    "current_allocation": { "Equity": 79.0, "Debt": 15.0, "Cash": 6.0 },
    "deviations": { "Equity": 9.0, "Debt": -10.0, "Cash": 1.0 },
    "rebalance_action_plan": [
      "Moderate Drift: Direct next 3–6 months of fresh SIP inflows into Debt to restore balance without selling equities.",
      "Deploy upcoming fresh SIP inflows into underweighted asset classes"
    ]
  }
  ```

---

## 8. System & Market APIs

- `GET /api/health`: Health status, service name, and version (`1.2.0`).
- `GET /api/markets/status`: NSE/BSE operating status and timings.
- `GET /api/markets/stocks`: Real-time stock prices, day changes, and technical fundamentals.
- `GET /api/funds`: Curated mutual funds catalog with TER and historical CAGR.
