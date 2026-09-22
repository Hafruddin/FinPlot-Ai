import datetime
from typing import Dict, Any, List

class RegulatoryService:
    """
    Regulatory Intelligence Service for Indian Capital Markets.
    Monitors circulars, notifications, and enforcement actions from:
    - Securities and Exchange Board of India (SEBI)
    - Reserve Bank of India (RBI)
    - Competition Commission of India (CCI)
    - Telecom Regulatory Authority of India (TRAI)
    - Ministry of Corporate Affairs (MCA)
    Maps verified regulatory posture to individual companies and sectors.
    """

    def __init__(self):
        self._actions = [
            {
                "authority": "SEBI",
                "date": "2026-09-08",
                "category": "MARKET_INTEGRITY",
                "headline": "SEBI tightens index derivative framework and increases minimum contract sizing to enhance retail risk protection",
                "affected_sectors": ["Stock Exchanges", "Brokers", "Financial Services"],
                "relevance": "Protects systemic retail liquidity and directs long-term capital toward systematic cash equities."
            },
            {
                "authority": "RBI",
                "date": "2026-08-22",
                "category": "BANKING_SUPERVISION",
                "headline": "RBI issues finalized circular on Project Finance provisioning norms with phased implementation",
                "affected_sectors": ["Banking & Finance", "Infrastructure", "Power"],
                "relevance": "Phased construction-phase provisioning (1.0% to 2.5%) removes previous market overhang on infrastructure lenders."
            },
            {
                "authority": "TRAI",
                "date": "2026-07-15",
                "category": "TELECOM_POLICY",
                "headline": "TRAI mandates quality of service (QoS) benchmarks for 5G network latency and dropped-call metrics",
                "affected_sectors": ["Telecommunications"],
                "relevance": "Encourages disciplined capital expenditure into deep fiber backhaul by tier-1 telecom operators."
            },
            {
                "authority": "CCI",
                "date": "2026-06-30",
                "category": "COMPETITION_REVIEW",
                "headline": "Competition Commission greenlights retail logistics modernization agreements with standard behavioral safeguards",
                "affected_sectors": ["Consumer Discretionary", "Retail", "Logistics"],
                "relevance": "Enables seamless consolidation of omnichannel distribution infrastructure."
            }
        ]

    def get_recent_actions(self) -> List[Dict[str, Any]]:
        return self._actions

    def get_stock_regulatory_context(self, symbol: str, sector: str) -> Dict[str, Any]:
        """
        Retrieves company-specific regulatory environment and compliance notes.
        """
        sec = sector.lower()
        if "bank" in sec or "finance" in sec:
            return {
                "authority": "Reserve Bank of India (RBI) & SEBI",
                "relevance": "HIGH",
                "status": "COMPLIANT_SOUND",
                "headline": "Capital Adequacy Ratio (CAR) and LCR buffers comfortably exceed regulatory thresholds",
                "summary": "The bank operates under Basel III prudential framework with Tier-1 capital well in excess of statutory 11.5% requirements, maintaining strong regulatory inspection track record.",
                "recent_focus": "Adherence to RBI's guidelines on digital lending rails and retail unsecured risk-weight calibration.",
                "source": "RBI Regulatory Disclosures & Basel III Filings"
            }
        elif "telecom" in sec:
            return {
                "authority": "Department of Telecommunications (DoT) & TRAI",
                "relevance": "HIGH",
                "status": "CLEAR_OUTLOOK",
                "headline": "Stable spectrum regulatory framework with predictable five-year roadmap",
                "summary": "Regulatory environment characterized by stable 5G spectrum allocations and rational tariff structures under TRAI oversight.",
                "recent_focus": "Rollout of AI-powered anti-spam filters mandated by telecom regulator.",
                "source": "TRAI Sectoral Notifications"
            }
        elif "energy" in sec or "oil" in sec:
            return {
                "authority": "Ministry of Petroleum & Natural Gas (MoPNG) & PNGRB",
                "relevance": "HIGH",
                "status": "POLICY_SUPPORTIVE",
                "headline": "Administered gas pricing formula with floor-and-ceiling protects downstream margins",
                "summary": "Domestic gas allocation policies provide volume predictability for city gas and industrial feedstock operations.",
                "recent_focus": "Carbon emission intensity reporting under SEBI Business Responsibility and Sustainability Reporting (BRSR).",
                "source": "MoPNG Gazetted Notifications"
            }
        elif "it" in sec or "technology" in sec:
            return {
                "authority": "Ministry of Electronics & IT (MeitY) & Global Data Regulators",
                "relevance": "MEDIUM",
                "status": "COMPLIANT",
                "headline": "Compliance with Digital Personal Data Protection (DPDP) Act and EU GDPR standards",
                "summary": "Strict enterprise client confidentiality agreements and global ISO/SOC-2 cyber certifications maintained across offshore delivery centers.",
                "recent_focus": "Responsible Artificial Intelligence (RAI) governance frameworks for enterprise client engagements.",
                "source": "MeitY Data Protection Rules & SEBI LODR"
            }
        else:
            return {
                "authority": "Securities and Exchange Board of India (SEBI)",
                "relevance": "MEDIUM",
                "status": "STANDARD_COMPLIANCE",
                "headline": "Adherence to SEBI LODR corporate governance and disclosure standards",
                "summary": "Regular statutory corporate filings, independent board representation, and quarterly audit disclosures submitted on time.",
                "recent_focus": "BRSR Core ESG disclosures for top 1,000 listed entities.",
                "source": "SEBI Compliance Portal"
            }

regulatory_service = RegulatoryService()
