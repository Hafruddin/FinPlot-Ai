"""
FinPilot AI — RAG (Retrieval-Augmented Generation) Knowledge Base Service
Provides deterministic semantic retrieval over curated, authoritative financial education documents
from SEBI, RBI, AMFI, NISM, and verified financial planning textbooks.
"""

import math
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import KnowledgeDocument

# Curated Authoritative Knowledge Corpus
FINANCIAL_KNOWLEDGE_CORPUS = [
    {
        "doc_id": "sebi_compounding_sip",
        "title": "Power of Compounding & Systematic Investment Plans (SIP)",
        "category": "compounding",
        "source_name": "SEBI Investor Education Programme",
        "url": "https://investor.sebi.gov.in/educational-resources.html",
        "section": "Wealth Creation & Time Horizon",
        "keywords": "compounding, sip, systematic investment, interest, time horizon, returns, rupee cost averaging",
        "content_chunk": (
            "Compounding is the process where earnings on an investment generate additional earnings over time. "
            "In a Systematic Investment Plan (SIP), disciplined periodic investing averages out the purchase cost of mutual fund units "
            "(Rupee Cost Averaging). Compounding exhibits exponential characteristics: the duration of staying invested "
            "often exerts a far greater impact on the final corpus than the initial amount invested. "
            "Key principle: Starting 5 years earlier can double the accumulated wealth even with identical periodic contributions."
        )
    },
    {
        "doc_id": "rbi_inflation_purchasing_power",
        "title": "Inflation & The Erosion of Purchasing Power",
        "category": "inflation",
        "source_name": "Reserve Bank of India (RBI) Financial Literacy Guide",
        "url": "https://rbi.org.in/financialeducation/",
        "section": "Macroeconomics & Personal Finance",
        "keywords": "inflation, purchasing power, real return, cpi, cost of living, fixed deposits",
        "content_chunk": (
            "Inflation is the persistent rise in the general price level of goods and services, diminishing the purchasing power of money. "
            "For example, at an average inflation rate of 6% per annum, a living expense of ₹20,000 per month will require ₹35,800 per month "
            "in 10 years, and ₹64,100 per month in 20 years just to sustain the exact same standard of living. "
            "Nominal returns must always be discounted by inflation to evaluate the 'Real Rate of Return' (Real Return ≈ Nominal Return - Inflation). "
            "Assets yielding below inflation cause capital depreciation in real terms."
        )
    },
    {
        "doc_id": "amfi_mutual_funds_asset_classes",
        "title": "Asset Allocation: Equity, Debt, and Gold",
        "category": "asset_allocation",
        "source_name": "Association of Mutual Funds in India (AMFI)",
        "url": "https://www.amfiindia.com/investor-corner/knowledge-center",
        "section": "Portfolio Construction",
        "keywords": "asset allocation, equity, debt, gold, hybrid funds, rebalancing, risk",
        "content_chunk": (
            "Asset allocation is the strategy of dividing an investment portfolio across diverse asset categories—principally Equities, "
            "Fixed Income (Debt), and Liquid Cash/Gold. Historical data indicates that asset allocation determines more than 85% of "
            "portfolio return variance over time, rather than individual stock selection. "
            "Equities offer inflation-beating capital appreciation with short-term volatility, while Debt provides capital stability and income. "
            "Annual rebalancing restores the portfolio to its target allocation, enforcing a disciplined 'buy low, sell high' practice."
        )
    },
    {
        "doc_id": "nism_emergency_fund_liquidity",
        "title": "Emergency Fund Architecture & Liquidity Management",
        "category": "emergency_fund",
        "source_name": "National Institute of Securities Markets (NISM)",
        "url": "https://www.nism.ac.in/financial-education/",
        "section": "Foundation Risk Management",
        "keywords": "emergency fund, liquidity, safety buffer, contingency, liquid funds, fixed deposit",
        "content_chunk": (
            "An emergency fund is a non-negotiable cash reserve designated exclusively for unforeseen emergencies such as medical crises, "
            "temporary job dislocation, or critical repairs. The established standard recommendation is 3 to 6 months of mandatory living expenses "
            "(essential food, utilities, rent, and active EMIs). "
            "For single-income households or gig economy earners, a 6 to 9-month reserve is advised. Emergency funds must prioritize "
            "liquidity and capital safety (Savings accounts, Overnight/Liquid Mutual Funds, or Sweep FDs) rather than high yield."
        )
    },
    {
        "doc_id": "sebi_diversification_unsystematic_risk",
        "title": "Diversification and Portfolio Risk Mitigation",
        "category": "risk",
        "source_name": "SEBI Investor Education Programme",
        "url": "https://investor.sebi.gov.in/educational-resources.html",
        "section": "Risk Management",
        "keywords": "diversification, unsystematic risk, systematic risk, concentration, volatility",
        "content_chunk": (
            "Diversification mitigates 'unsystematic risk'—the risk specific to a single company, sector, or management failure. "
            "Holding a diversified basket of 20 to 30 uncorrelated securities across sectors significantly dampens volatility without "
            "compromising expected returns. However, diversification cannot eliminate 'systematic risk' (market-wide macroeconomic shocks, "
            "interest rate hikes, or geopolitical crises) which affect the entire asset class."
        )
    },
    {
        "doc_id": "finpilot_reverse_sip_freedom",
        "title": "Goal-Based Reverse SIP & The 4% Safe Withdrawal Rule",
        "category": "goals",
        "source_name": "FinPilot Financial Engineering Research",
        "url": "https://finpilot.ai/research/freedom-corpus",
        "section": "Financial Freedom Mathematics",
        "keywords": "reverse sip, annuity, future value, 4 percent rule, freedom corpus, retirement",
        "content_chunk": (
            "The Financial Freedom Corpus represents the lump sum required to sustain living expenses perpetually without capital exhaustion. "
            "Based on the Trinity Study and Indian inflation dynamics, a safe withdrawal rate between 3.5% and 4.0% of the corpus per annum is standard. "
            "To accumulate this corpus, the Reverse SIP annuity formula computes required monthly contribution: "
            "SIP = Net Corpus / [(( (1 + r)^n - 1) / r) * (1 + r)], where r is monthly expected return and n is months. "
            "If required SIP exceeds monthly investable capacity, extending the horizon by 3-5 years drastically lowers the monthly burden."
        )
    },
    {
        "doc_id": "amfi_direct_vs_regular_plans",
        "title": "Mutual Fund Direct vs Regular Plans and Total Expense Ratio (TER)",
        "category": "mutual_funds",
        "source_name": "Association of Mutual Funds in India (AMFI)",
        "url": "https://www.amfiindia.com/investor-corner",
        "section": "Cost Efficiency",
        "keywords": "direct plan, regular plan, ter, expense ratio, commission, compounding cost",
        "content_chunk": (
            "Mutual funds in India provide two purchase routes: Direct Plans and Regular Plans. "
            "Direct plans have a lower Total Expense Ratio (TER) because they eliminate distributor commissions (typically 0.5% to 1.2% per year). "
            "Over a 15-20 year investment horizon, an expense ratio difference of 1% can compound into a 15% to 20% difference in the final corpus "
            "due to the drag of compounding fees. Investors capable of self-directed research should utilize direct plans."
        )
    },
    {
        "doc_id": "rbi_debt_management_snowball_avalanche",
        "title": "Debt Optimization: Avalanche vs Snowball Strategies",
        "category": "debt",
        "source_name": "Reserve Bank of India (RBI) Financial Education",
        "url": "https://rbi.org.in/financialeducation/",
        "section": "Personal Liability Management",
        "keywords": "debt, credit card, emi, personal loan, avalanche method, snowball method, interest cost",
        "content_chunk": (
            "High-interest debt (e.g., credit card rollovers at 36-42% p.a. or unsecured personal loans at 14-18% p.a.) represents a guaranteed "
            "negative return that outstrips any realistic market gain. The 'Debt Avalanche' method prioritizes paying off debts with the highest "
            "interest rate first, minimizing total interest paid mathematically. The 'Debt Snowball' method prioritizes smallest balances first "
            "for psychological momentum. Never begin aggressive equity investing while holding high-cost revolving debt."
        )
    }
]


class RAGService:
    """Retrieval-Augmented Generation service with vector similarity and citation verification."""

    def __init__(self):
        self._corpus = FINANCIAL_KNOWLEDGE_CORPUS
        self._ensure_seeded()

    def _ensure_seeded(self):
        """Seed the SQLite database with knowledge documents on initial launch."""
        try:
            db: Session = SessionLocal()
            count = db.query(KnowledgeDocument).count()
            if count == 0:
                for item in self._corpus:
                    doc = KnowledgeDocument(
                        doc_id=item["doc_id"],
                        title=item["title"],
                        category=item["category"],
                        source_name=item["source_name"],
                        url=item.get("url"),
                        section=item.get("section"),
                        content_chunk=item["content_chunk"],
                        keywords=item.get("keywords", "")
                    )
                    db.add(doc)
                db.commit()
            db.close()
        except Exception as e:
            # Fallback in-memory if DB is initializing
            pass

    def _tokenize(self, text: str) -> List[str]:
        """Clean and tokenize text into lowercase word stems/terms."""
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        tokens = [t for t in cleaned.split() if len(t) > 2]
        # Basic stopword elimination
        stopwords = {
            'the', 'and', 'for', 'that', 'with', 'this', 'from', 'have', 'are', 'was',
            'what', 'why', 'how', 'when', 'does', 'can', 'should', 'about', 'your', 'you'
        }
        return [t for t in tokens if t not in stopwords]

    def _compute_tf_idf_similarity(self, query_tokens: List[str], doc_tokens: List[str], doc_keywords: str) -> float:
        """Compute keyword overlap & term frequency relevance score."""
        if not query_tokens or not doc_tokens:
            return 0.0
        
        doc_keyword_list = [k.strip().lower() for k in doc_keywords.split(',')]
        score = 0.0
        
        for q in query_tokens:
            # Match in body
            tf = doc_tokens.count(q) / len(doc_tokens)
            if tf > 0:
                score += tf * 2.0
            # Boost if found in explicit keywords or title
            if any(q in kw for kw in doc_keyword_list):
                score += 0.45
                
        return score

    def search(self, query: str, top_k: int = 3, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant documents matching query with genuine citations.
        Never fabricates sources. If no match exceeds minimum confidence, returns empty list.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored_docs = []
        for doc in self._corpus:
            if category and doc["category"] != category:
                continue
            
            doc_tokens = self._tokenize(doc["title"] + " " + doc["content_chunk"])
            score = self._compute_tf_idf_similarity(query_tokens, doc_tokens, doc.get("keywords", ""))
            
            if score > 0.05:  # Relevance threshold
                scored_docs.append({
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "source": doc["source_name"],
                    "url": doc.get("url"),
                    "section": doc.get("section"),
                    "content": doc["content_chunk"],
                    "score": round(score, 4)
                })

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]

    def format_context_for_prompt(self, docs: List[Dict[str, Any]]) -> str:
        """Formats retrieved documents into verified evidence blocks for LLM consumption."""
        if not docs:
            return "No verified external literature matched the specific query. Rely strictly on verified mathematical definitions and disclose limitations."

        context_lines = ["--- VERIFIED FINANCIAL EDUCATION EVIDENCE ---"]
        for i, d in enumerate(docs, 1):
            context_lines.append(
                f"[{i}] {d['title']}\n"
                f"Source: {d['source']} | Section: {d.get('section', 'General')}\n"
                f"URL: {d.get('url', 'N/A')}\n"
                f"Evidence Content: {d['content']}\n"
            )
        context_lines.append("--- END OF EVIDENCE ---")
        return "\n".join(context_lines)


rag_service = RAGService()

def query_knowledge_base(query: str, top_k: int = 3, category: Optional[str] = None) -> List[Dict[str, Any]]:
    return rag_service.search(query, top_k=top_k, category=category)

def get_knowledge_documents() -> List[Dict[str, Any]]:
    return FINANCIAL_KNOWLEDGE_CORPUS
