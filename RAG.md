# FinPilot AI — RAG Knowledge Base Architecture 📚

> **RMK INNOVATE Hackathon** | **Track:** Agentic & Generative AI  
> **Module:** Authoritative Regulatory RAG Service (`backend/services/rag_service.py`)

---

## 1. Grounded Knowledge Philosophy

Large Language Models frequently hallucinate financial figures, confuse taxation rules across different jurisdictions, or promote speculative high-risk trading. 

FinPilot AI solves this by implementing **Closed-Domain Grounded Retrieval-Augmented Generation (RAG)**:
- **Authoritative Corpus:** Grounded exclusively in verified, official educational materials published by Indian financial regulators and research institutions (**SEBI, RBI, AMFI, NISM, Finance Act 2024**).
- **Strict Provenance Citations:** Every retrieved fact is tagged with document source, section name, and official verification URL.
- **Bounding Directives:** The AI Tutor is programmatically forbidden from answering questions outside verified financial education principles or offering speculative single-stock tips.

---

## 2. Curated Regulatory Corpus

The knowledge base is pre-seeded with 8 authoritative documents stored in SQLite (`knowledge_documents` table):

| Document ID | Title | Regulatory Source | Key Educational Coverage |
| :--- | :--- | :--- | :--- |
| `sebi_compounding_sip` | Power of Compounding & Systematic Investment Plans | **SEBI** Investor Education | Compounding frequency, SIP rupee cost averaging, hockey-stick growth curves over 10+ years. |
| `rbi_inflation_purchasing_power` | Inflation & The Erosion of Purchasing Power | **RBI** Financial Literacy Guide | CPI inflation, rule of 72, real vs nominal rate of return ($Real = Nominal - Inflation$). |
| `amfi_asset_allocation` | Asset Allocation: Equity, Debt, and Gold | **AMFI** Knowledge Center | Multi-asset class diversification, non-correlated assets, rebalancing without market timing. |
| `rbi_emergency_funds` | Emergency Funds & Liquid Contingency Reserves | **RBI** Financial Inclusion Guide | 3–6 months mandatory living expense buffer, liquid fund redemption features. |
| `sebi_diversification_risk` | Portfolio Diversification & Risk Management | **SEBI** Investor Education | Systematic vs unsystematic risk, company-specific default risk mitigation. |
| `finpilot_reverse_sip_math` | Goal-Based Reverse SIP & Safe Withdrawal Rule | **FinPilot AI** Research | Reverse annuity due formulas, future value discounting, 4% safe withdrawal math. |
| `amfi_ter_direct_vs_regular` | Mutual Fund Expense Ratios: Direct vs Regular | **AMFI** Investor Guidance | Distributor brokerage commissions, 0.5%–1.2% TER delta compounding over 20 years. |
| `tax_ltcg_stcg_finance_act_2024` | Capital Gains Taxation (Finance Act 2024) | **Finance Act 2024** | 12.5% LTCG on equity above ₹1.25 Lakh exemption, 20% STCG, indexation rules on debt. |

---

## 3. Retrieval & Indexing Mechanics

### Hybrid Tokenization & Vector Space Scoring
To maintain zero-dependency local execution while delivering semantic relevance, FinPilot AI utilizes an optimized **TF-IDF + BM25 Keyword Overlap Engine**:

1. **Stopword Stripping & Normalization:** Lowercases, strips punctuation, and removes conversational noise.
2. **Category Prioritization:** Filters by asset class or intent category when specified by the agent.
3. **Term Frequency-Inverse Document Frequency (TF-IDF):** Computes importance of query terms relative to document term distributions.
4. **Keyword Density Multiplier:** Boosts scores for documents containing high-intent financial keywords (`inflation`, `compounding`, `reverse sip`, `ter`, `ltcg`, `emergency`).

### Scoring Function:
$$Score(D, Q) = \sum_{t \in Q \cap D} \left( 1 + \ln(TF_{t,D}) \right) \times IDF_t \times KeywordMultiplier(D, Q)$$

---

## 4. Strict Citation Provenance Format

Retrieved citations are injected into agent contexts and returned to users in a standardized structure:
```json
{
  "title": "Power of Compounding & Systematic Investment Plans (SIP)",
  "source": "SEBI Investor Education Programme",
  "url": "https://investor.sebi.gov.in/educational-resources.html",
  "section": "Wealth Creation & Time Horizon"
}
```

The frontend renders these citations as interactive, verified trust badges with external source links:
```html
<span class="badge badge-gold">
  📜 Source: SEBI Investor Education Programme
</span>
```

---

## 5. Anti-Hallucination Guardrails

The RAG pipeline enforces 3 layers of protection:
1. **Source Isolation:** When Gemini or OpenAI is called, prompts are enclosed with strict boundary prompts:
   > *"Answer strictly from the following verified regulatory literature. Never invent historical returns or promise guaranteed outcomes."*
2. **Forbidden Token Sanitizer:** Outgoing responses are scanned for non-compliant phrases (e.g. `guaranteed return`, `multibagger`, `sure shot`, `penny stock`). Any match is sanitized and replaced with compliant educational terminology.
3. **Deterministic Grounded Fallback:** If API keys are absent, the system uses an authoritative deterministic explanation generator that crafts comprehensive answers directly from the retrieved document extracts.
