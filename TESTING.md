# FinPilot AI — Automated Testing Suite 🧪

> **RMK INNOVATE Hackathon** | **Track:** Agentic & Generative AI  
> **Test Suite File:** `backend/test_hackathon_suite.py`  
> **Total Test Cases:** 9 | **Pass Rate:** 100% (9/9 Passed)

---

## 1. How to Execute the Test Suite

Run the full end-to-end integration and verification suite with Python:

```bash
python3 backend/test_hackathon_suite.py
```

### Expected Output:
```
----------------------------------------------------------------------
Ran 9 tests in 0.208s

OK
```

---

## 2. Test Suite Coverage & Verification Matrix

| # | Test Case | Function Under Test | Verified Behavior |
| :---: | :--- | :--- | :--- |
| **01** | `test_01_health_check` | `GET /api/health` & `GET /` | API reports status `ok` and version `1.2.0`; root serves canonical React `index.html`. |
| **02** | `test_02_auth_signup_and_jwt` | `POST /api/auth/signup` & `GET /api/auth/me` | Cryptographic `bcrypt` password hashing, JWT bearer token issuance, and authenticated endpoint authorization. |
| **03** | `test_03_rag_knowledge_base_retrieval` | `POST /api/rag/query` & `query_knowledge_base` | Curated corpus has $\ge 8$ regulatory documents; TF-IDF query yields relevant docs with verified SEBI/AMFI/RBI citations. |
| **04** | `test_04_ai_tutor_and_safety_guardrails` | `POST /api/tutor/chat` & `answer_financial_query` | Structured educational answer generation; speculative query ("guaranteed 100% penny stock") triggers regulatory safety notice. |
| **05** | `test_05_deterministic_reverse_sip_engine_and_edge_cases` | `solve_reverse_sip` | Reverse annuity due solves ₹21,521/mo for ₹50L in 10y @ 12%; handles target already achieved (₹0 SIP) and zero-return linear edge cases. |
| **06** | `test_06_whatif_timeline_engine` | `POST /api/simulation/whatif` | Compares 10y vs 15y timeline; confirms $\sim 55.1\%$ drop in required SIP and generates educational takeaway. |
| **07** | `test_07_seven_agent_pipeline_and_db_logging` | `POST /api/agents/run` & `run_pipeline` | Full 7-agent DAG execution (`Profile`, `Goal`, `Risk`, `Knowledge`, `Simulation`, `Strategy`, `Explanation`); execution trace stored in SQLite. |
| **08** | `test_08_financial_iq_six_pillar_engine` | `GET /api/iq/questions` & `POST /api/iq/evaluate` | Evaluates answers across 6 competency pillars; perfect answers return 100/100 (1000/1000) Master Investor tier. |
| **09** | `test_09_portfolio_guardian_allocation_drift` | `GET /api/portfolio/guardian` & `analyze_portfolio_drift` | Calculates real equity drift (+9% drift for 79% equity vs 70% target); returns `MODERATE_DRIFT` and zero-tax fresh SIP inflow plan. |

---

## 3. Mathematical Proof & Edge-Case Verifications

### Reverse Annuity Due Equation
In systematic investment plans (SIP), contributions occur at the start of each compounding interval. The Future Value ($FV$) of an annuity due is:

$$FV = P \times \left[ \frac{(1 + r)^n - 1}{r} \right] \times (1 + r)$$

Rearranging for the required monthly investment ($P$):

$$P = \frac{FV_{net}}{\left[ \frac{(1 + r)^n - 1}{r} \right] \times (1 + r)}$$

Where:
- $FV_{net} = Target - Savings \times (1 + R_{annual})^Y$
- $r = \frac{R_{annual}}{12} = \frac{0.12}{12} = 0.01$
- $n = Y \times 12 = 10 \times 12 = 120$

For Arjun Patel ($Target = ₹50,00,000$, $Savings = ₹50,000$):
- Future value of existing savings: $₹50,000 \times (1.12)^{10} = ₹1,55,292$
- Net corpus required: $₹50,00,000 - ₹1,55,292 = ₹48,44,708$
- Annuity factor: $\frac{(1.01)^{120} - 1}{0.01} \times 1.01 = 232.327$
- **Required Monthly SIP:** $\frac{₹48,44,708}{232.327} = \mathbf{₹21,521 / month}$

The automated test `test_05` verifies this exact mathematical output.

### Edge Cases Tested:
1. **Target Already Achieved ($Target \le CurrentSavings$):** Returns `TARGET_ALREADY_ACHIEVED`, `required_monthly_sip: 0`.
2. **Zero Return ($R_{annual} = 0\%$):** Returns `ZERO_RETURN_LINEAR`, applying linear division $P = \lceil \frac{NetNeeded}{n} \rceil$.
3. **Horizon Calibration ($10y \rightarrow 15y$):** Required monthly SIP drops from **₹21,521** to **₹9,657**, a **-55.1%** reduction verified by `test_06`.
