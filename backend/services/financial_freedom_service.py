"""
FinPilot AI — Financial Freedom Planning & Calculation Service
Authoritative mathematical calculation engine for Cash Flow, Emergency Fund,
Inflation, Freedom Corpus, Reverse SIP Annuity Solver, Timeline, and Readiness Score.
"""

import math
from typing import Dict, Any, List, Optional


def calculate_cashflow(
    income_dict: Dict[str, float],
    essential_dict: Dict[str, float],
    lifestyle_dict: Dict[str, float],
    emi_dict: Dict[str, float],
    custom_expenses: Optional[List[Dict[str, Any]]] = None,
    current_investments_dict: Optional[Dict[str, float]] = None,
    current_savings: float = 0.0,
    emergency_target_months: int = 6,
    risk_level: str = "moderate"
) -> Dict[str, Any]:
    """
    Computes complete monthly cashflow analysis, surplus, and safe investment capacity.
    Maintains a calculated safety buffer based on debt obligations and emergency fund gap.
    """
    # 1. Incomes
    monthly_income = max(0.0, float(income_dict.get("monthly_income", 0.0)))
    additional_income = max(0.0, float(income_dict.get("additional_income", 0.0)))
    rental_income = max(0.0, float(income_dict.get("rental_income", 0.0)))
    spouse_income = max(0.0, float(income_dict.get("spouse_income", 0.0)))
    total_monthly_income = monthly_income + additional_income + rental_income + spouse_income

    # 2. Essential Expenses
    total_essential = sum(max(0.0, float(v)) for v in essential_dict.values())

    # 3. Lifestyle Expenses
    total_lifestyle = sum(max(0.0, float(v)) for v in lifestyle_dict.values())

    # 4. EMIs
    total_emis = sum(max(0.0, float(v)) for v in emi_dict.values())

    # 5. Custom Expenses
    total_custom = 0.0
    if custom_expenses:
        for item in custom_expenses:
            total_custom += max(0.0, float(item.get("amount", 0.0)))

    # Total Monthly Expenses
    total_monthly_expenses = total_essential + total_lifestyle + total_emis + total_custom

    # 6. Current Investments
    total_current_investments = 0.0
    if current_investments_dict:
        total_current_investments = sum(max(0.0, float(v)) for v in current_investments_dict.values())

    # Monthly Surplus
    monthly_surplus = total_monthly_income - total_monthly_expenses

    # 7. Safety Buffer & Safe Investment Capacity
    # Never invest 100% of surplus. Calculate buffer based on essential obligations & emergency gap.
    monthly_debt_and_essentials = total_essential + total_emis
    emergency_target = monthly_debt_and_essentials * emergency_target_months
    emergency_gap = max(0.0, emergency_target - current_savings)

    if monthly_surplus <= 0:
        suggested_safety_buffer = 0.0
        safe_investment_capacity = 0.0
    else:
        # Buffer between 15% and 30% of surplus depending on risk and emergency status
        base_buffer_pct = 0.30 if emergency_gap > 0 else 0.20
        if risk_level.lower() == "conservative":
            base_buffer_pct += 0.05
        elif risk_level.lower() == "aggressive":
            base_buffer_pct = max(0.15, base_buffer_pct - 0.05)

        raw_buffer = monthly_surplus * base_buffer_pct
        # Minimum safety cushion of ₹3,000 or 5% of income if surplus allows
        min_buffer = min(monthly_surplus, max(3000.0, total_monthly_income * 0.05))
        suggested_safety_buffer = round(max(raw_buffer, min_buffer))
        safe_investment_capacity = max(0.0, round(monthly_surplus - suggested_safety_buffer))

    savings_rate_pct = round((monthly_surplus / total_monthly_income * 100.0), 1) if total_monthly_income > 0 else 0.0
    emi_burden_pct = round((total_emis / total_monthly_income * 100.0), 1) if total_monthly_income > 0 else 0.0

    return {
        "total_monthly_income": round(total_monthly_income),
        "total_essential_expenses": round(total_essential),
        "total_lifestyle_expenses": round(total_lifestyle),
        "total_emis": round(total_emis),
        "total_custom_expenses": round(total_custom),
        "total_monthly_expenses": round(total_monthly_expenses),
        "total_current_investments": round(total_current_investments),
        "monthly_surplus": round(monthly_surplus),
        "suggested_safety_buffer": round(suggested_safety_buffer),
        "safe_investment_capacity": round(safe_investment_capacity),
        "savings_rate_pct": savings_rate_pct,
        "emi_burden_pct": emi_burden_pct
    }


def calculate_emergency_fund(
    essential_monthly: float,
    emi_monthly: float,
    current_savings: float,
    multiplier_months: int = 6,
    monthly_capacity: float = 0.0
) -> Dict[str, Any]:
    """
    Evaluates emergency fund readiness against 3, 6, 9, or 12 months of mandatory obligations.
    """
    monthly_obligations = max(0.0, essential_monthly) + max(0.0, emi_monthly)
    target_amount = round(monthly_obligations * multiplier_months)
    current_savings_val = max(0.0, current_savings)
    gap = max(0.0, round(target_amount - current_savings_val))
    is_ready = current_savings_val >= target_amount

    # Estimate months to complete
    if is_ready:
        months_to_complete = 0
    elif monthly_capacity > 0:
        months_to_complete = math.ceil(gap / monthly_capacity)
    else:
        months_to_complete = 999

    status_message = (
        "Emergency reserve is fully funded! Your foundation is resilient."
        if is_ready
        else f"Build your emergency reserve (₹{gap:,.0f} gap) before aggressively expanding long-term illiquid assets."
    )

    return {
        "monthly_obligations": round(monthly_obligations),
        "multiplier_months": multiplier_months,
        "target_amount": target_amount,
        "current_savings": round(current_savings_val),
        "gap": gap,
        "is_ready": is_ready,
        "months_to_complete": months_to_complete,
        "status_message": status_message
    }


def calculate_financial_freedom(
    monthly_expense_today: float,
    inflation_rate: float,
    horizon_years: int,
    withdrawal_rate: float,
    existing_investments: float,
    return_assumption: float,
    monthly_investment_capacity: float
) -> Dict[str, Any]:
    """
    Central Financial Freedom Engine:
    - Calculates inflation-adjusted future expense
    - Computes required Freedom Corpus via safe withdrawal rate assumption (e.g. 4%)
    - Projects existing investments compounding
    - Solves required monthly SIP via reverse annuity equation
    - Compares against safe capacity and provides 6 concrete alternatives if in shortfall
    """
    horizon_years = max(1, horizon_years)
    inflation_rate = max(0.0, min(0.20, inflation_rate))  # 0% to 20%
    withdrawal_rate = max(0.01, min(0.10, withdrawal_rate)) # 1% to 10%
    return_assumption = max(0.0, min(0.30, return_assumption)) # 0% to 30%
    monthly_expense_today = max(0.0, monthly_expense_today)
    existing_investments = max(0.0, existing_investments)
    monthly_investment_capacity = max(0.0, monthly_investment_capacity)

    # 1. Future Expense with Inflation
    inflation_factor = math.pow(1.0 + inflation_rate, horizon_years)
    future_monthly_expense_val = monthly_expense_today * inflation_factor
    future_annual_expense_val = future_monthly_expense_val * 12.0

    # 2. Target Financial Freedom Corpus
    freedom_corpus = round(future_annual_expense_val / withdrawal_rate)

    # 3. Existing Investment Growth (FV = PV * (1 + r)^n)
    growth_factor = math.pow(1.0 + return_assumption, horizon_years)
    existing_investments_fv = round(existing_investments * growth_factor)
    existing_growth_gain = max(0, existing_investments_fv - round(existing_investments))

    # 4. Net Corpus needed from future SIP
    net_corpus_needed = max(0, freedom_corpus - existing_investments_fv)

    # 5. Reverse SIP Calculation
    r_month = return_assumption / 12.0
    total_months = horizon_years * 12

    if net_corpus_needed == 0:
        required_sip = 0
        denom = ((math.pow(1.0 + r_month, total_months) - 1.0) / r_month) * (1.0 + r_month) if r_month > 0 else total_months
        sip_target_already_achieved = True
    elif r_month <= 0:
        denom = float(total_months)
        required_sip = math.ceil(net_corpus_needed / total_months) if total_months > 0 else 0
        sip_target_already_achieved = False
    else:
        # Annuity formula: FV = P * [ ((1+r)^n - 1) / r ] * (1+r)
        denom = ((math.pow(1.0 + r_month, total_months) - 1.0) / r_month) * (1.0 + r_month)
        required_sip = math.ceil(net_corpus_needed / denom) if denom > 0 else 0
        sip_target_already_achieved = False

    # Capacity comparison
    sip_surplus_or_deficit = round(monthly_investment_capacity - required_sip)
    has_capacity_shortfall = required_sip > monthly_investment_capacity

    # Actionable alternatives if shortfall exists
    alternatives = []
    if has_capacity_shortfall and required_sip > 0:
        # Option A: Start with current capacity + Step-up SIP
        alternatives.append({
            "code": "OPTION_A",
            "title": "Apply Annual Step-Up SIP",
            "description": f"Start with your available ₹{monthly_investment_capacity:,.0f}/month today and increase your contribution by 10% each year as your income grows."
        })
        # Option B: Extend investment horizon
        # Calculate how many extra years needed with current capacity
        extra_years = 3
        alt_horizon = horizon_years + extra_years
        alt_n = alt_horizon * 12
        alt_fv_exist = existing_investments * math.pow(1.0 + return_assumption, alt_horizon)
        alt_fut_exp = (monthly_expense_today * math.pow(1.0 + inflation_rate, alt_horizon)) * 12
        alt_corpus = alt_fut_exp / withdrawal_rate
        alt_net = max(0, alt_corpus - alt_fv_exist)
        alt_denom = ((math.pow(1.0 + r_month, alt_n) - 1.0) / r_month) * (1.0 + r_month) if r_month > 0 else alt_n
        alt_req_sip = math.ceil(alt_net / alt_denom) if alt_denom > 0 else 0
        alternatives.append({
            "code": "OPTION_B",
            "title": f"Extend Horizon by {extra_years} Years",
            "description": f"Extending your timeline from {horizon_years} to {alt_horizon} years reduces the required monthly SIP to approximately ₹{alt_req_sip:,.0f}/month."
        })
        # Option C: Inject Additional Lumpsum Today
        # Lumpsum needed today to bridge shortfall
        shortfall_corpus = net_corpus_needed - (monthly_investment_capacity * denom if denom > 0 else 0)
        lump_needed = max(0, round(shortfall_corpus / growth_factor)) if growth_factor > 0 else 0
        alternatives.append({
            "code": "OPTION_C",
            "title": "Add One-Time Initial Capital",
            "description": f"Deploying an additional one-time lumpsum of ~₹{lump_needed:,.0f} today allows your current capacity of ₹{monthly_investment_capacity:,.0f}/month to bridge the target."
        })
        # Option D: Moderate Target Income in Today's Value
        alt_target_income = round(monthly_expense_today * (monthly_investment_capacity / required_sip))
        alternatives.append({
            "code": "OPTION_D",
            "title": "Moderate Desired Monthly Target",
            "description": f"Calibrating your target living expense to ₹{alt_target_income:,.0f}/month (in today's purchasing power) aligns precisely with your current investment capacity."
        })
        # Option E: Review and Optimize Discretionary Expenses
        alternatives.append({
            "code": "OPTION_E",
            "title": "Audit Lifestyle Expenses & Subscriptions",
            "description": f"Redirecting ₹{abs(sip_surplus_or_deficit):,.0f}/month from discretionary dining, entertainment, or shopping directly closes your monthly planning gap."
        })
        # Option F: Balanced Hybrid Strategy
        alternatives.append({
            "code": "OPTION_F",
            "title": "Balanced Hybrid Execution",
            "description": "Combine a moderate 2-year timeline extension with a modest 5% annual step-up to achieve target freedom without straining cashflow."
        })

    return {
        "monthly_expense_today": round(monthly_expense_today),
        "horizon_years": horizon_years,
        "inflation_rate": inflation_rate,
        "inflation_rate_pct": round(inflation_rate * 100, 1),
        "withdrawal_rate": withdrawal_rate,
        "withdrawal_rate_pct": round(withdrawal_rate * 100, 1),
        "return_assumption": return_assumption,
        "return_assumption_pct": round(return_assumption * 100, 1),
        "future_monthly_expense": round(future_monthly_expense_val),
        "future_annual_expense": round(future_annual_expense_val),
        "freedom_corpus": freedom_corpus,
        "existing_investments": round(existing_investments),
        "existing_investments_fv": existing_investments_fv,
        "existing_growth_gain": existing_growth_gain,
        "net_corpus_needed": net_corpus_needed,
        "required_sip": required_sip,
        "monthly_investment_capacity": round(monthly_investment_capacity),
        "sip_surplus_or_deficit": sip_surplus_or_deficit,
        "has_capacity_shortfall": has_capacity_shortfall,
        "sip_target_already_achieved": sip_target_already_achieved,
        "alternatives": alternatives
    }


def solve_reverse_sip(
    target_amount: float,
    horizon_years: int,
    annual_return: float = 0.12,
    current_savings: float = 0.0,
    monthly_investment_capacity: float = 0.0
) -> Dict[str, Any]:
    """
    Authoritative deterministic Reverse SIP solver.
    Computes exact monthly contribution needed to reach target_amount in horizon_years,
    accounting for compounding on initial savings.
    Handles edge cases: zero return, target already achieved, zero horizon.
    """
    target = max(0.0, float(target_amount))
    years = max(1, int(horizon_years))
    ret = float(annual_return)
    if ret > 1.0:
        ret = ret / 100.0
    r = max(0.0, min(0.50, ret))
    savings = max(0.0, float(current_savings))
    capacity = max(0.0, float(monthly_investment_capacity))

    total_months = years * 12
    r_month = r / 12.0

    # 1. Compounding of initial savings
    savings_fv = savings * math.pow(1.0 + r, years)
    net_needed = max(0.0, target - savings_fv)

    # 2. Reverse Annuity Calculation
    if net_needed <= 0.0:
        required_sip = 0
        status = "TARGET_ALREADY_ACHIEVED"
    elif r_month <= 0.0:
        # Zero return case: simple linear division
        required_sip = math.ceil(net_needed / total_months)
        status = "ZERO_RETURN_LINEAR"
    else:
        # Future value of annuity formula: FV = P * [((1+r)^n - 1)/r] * (1+r)
        denom = ((math.pow(1.0 + r_month, total_months) - 1.0) / r_month) * (1.0 + r_month)
        required_sip = math.ceil(net_needed / denom) if denom > 0 else 0
        status = "OK"

    total_contributed = round(savings + (required_sip * total_months))
    growth_gain = max(0, round(target - total_contributed)) if required_sip > 0 else max(0, round(savings_fv - savings))
    future_value = round(savings_fv + (required_sip * denom if (r_month > 0 and required_sip > 0) else required_sip * total_months))

    return {
        "target_amount": round(target),
        "horizon_years": years,
        "annual_return_pct": round(r * 100, 2),
        "initial_savings": round(savings),
        "initial_savings_fv": round(savings_fv),
        "net_needed_from_sip": round(net_needed),
        "required_monthly_sip": required_sip,
        "total_contributed": total_contributed,
        "growth_gain": growth_gain,
        "future_value_achieved": future_value,
        "monthly_capacity": round(capacity),
        "is_capacity_sufficient": capacity >= required_sip if required_sip > 0 else True,
        "capacity_deficit": max(0, round(required_sip - capacity)),
        "status": status
    }


def calculate_years_to_freedom(
    current_corpus: float,
    monthly_sip: float,
    return_rate: float,
    monthly_expense_today: float,
    inflation_rate: float,
    withdrawal_rate: float,
    max_years: int = 50
) -> Dict[str, Any]:
    """
    Month-by-month simulation determining the earliest timeline when projected wealth
    meets or exceeds the inflation-adjusted Financial Freedom Corpus.
    """
    current_corpus = max(0.0, current_corpus)
    monthly_sip = max(0.0, monthly_sip)
    return_rate = max(0.0, return_rate)
    monthly_expense_today = max(0.0, monthly_expense_today)
    inflation_rate = max(0.0, inflation_rate)
    withdrawal_rate = max(0.01, withdrawal_rate)

    r_month = return_rate / 12.0
    r_inflation_month = math.pow(1.0 + inflation_rate, 1.0 / 12.0) - 1.0

    corpus = current_corpus
    max_months = max_years * 12

    # Check if already free today
    target_today = (monthly_expense_today * 12.0) / withdrawal_rate
    if corpus >= target_today and target_today > 0:
        return {
            "years": 0,
            "months": 0,
            "total_months": 0,
            "achieved_corpus": round(corpus),
            "target_corpus_at_milestone": round(target_today),
            "achievable": True,
            "display_text": "Your existing investment corpus already supports your target living expenses today!"
        }

    for m in range(1, max_months + 1):
        # Grow previous corpus + add monthly SIP
        corpus = (corpus + monthly_sip) * (1.0 + r_month)

        # Target corpus at month m
        # t in years = m / 12
        t_years = m / 12.0
        exp_m = monthly_expense_today * math.pow(1.0 + inflation_rate, t_years)
        target_at_m = (exp_m * 12.0) / withdrawal_rate

        if corpus >= target_at_m:
            y = m // 12
            rem_m = m % 12
            time_str = f"{y} years and {rem_m} months" if rem_m > 0 else f"{y} years"
            return {
                "years": y,
                "months": rem_m,
                "total_months": m,
                "achieved_corpus": round(corpus),
                "target_corpus_at_milestone": round(target_at_m),
                "achievable": True,
                "display_text": f"Under these assumptions, your projection reaches the target in approximately {time_str}."
            }

    return {
        "years": max_years,
        "months": 0,
        "total_months": max_months,
        "achieved_corpus": round(corpus),
        "target_corpus_at_milestone": round((monthly_expense_today * math.pow(1.0 + inflation_rate, max_years) * 12) / withdrawal_rate),
        "achievable": False,
        "display_text": f"Target not reached within {max_years} years under current assumptions. Consider stepping up monthly SIP or moderating the target."
    }


def calculate_scenarios(
    monthly_expense_today: float,
    inflation_rate: float,
    horizon_years: int,
    withdrawal_rate: float,
    existing_investments: float,
    monthly_sip: float
) -> List[Dict[str, Any]]:
    """
    Computes Conservative (8%), Base (10%), and Optimistic (12%) illustrative scenarios.
    """
    scenario_configs = [
        {"name": "Conservative", "return_rate": 0.08, "label": "8% p.a. Assumed Return", "badge": "Defensive"},
        {"name": "Base", "return_rate": 0.10, "label": "10% p.a. Assumed Return", "badge": "Balanced"},
        {"name": "Optimistic", "return_rate": 0.12, "label": "12% p.a. Assumed Return", "badge": "Growth"}
    ]

    results = []
    for sc in scenario_configs:
        r = sc["return_rate"]
        # Required SIP for this scenario
        ff_calc = calculate_financial_freedom(
            monthly_expense_today=monthly_expense_today,
            inflation_rate=inflation_rate,
            horizon_years=horizon_years,
            withdrawal_rate=withdrawal_rate,
            existing_investments=existing_investments,
            return_assumption=r,
            monthly_investment_capacity=monthly_sip
        )
        # Years to freedom under this scenario's return rate with current SIP
        y_calc = calculate_years_to_freedom(
            current_corpus=existing_investments,
            monthly_sip=monthly_sip,
            return_rate=r,
            monthly_expense_today=monthly_expense_today,
            inflation_rate=inflation_rate,
            withdrawal_rate=withdrawal_rate
        )

        # Projected corpus at target date
        total_months = horizon_years * 12
        r_m = r / 12.0
        fv_sip = (monthly_sip * ((math.pow(1.0 + r_m, total_months) - 1.0) / r_m) * (1.0 + r_m)) if r_m > 0 else (monthly_sip * total_months)
        fv_exist = existing_investments * math.pow(1.0 + r, horizon_years)
        projected_corpus = round(fv_sip + fv_exist)

        results.append({
            "scenario": sc["name"],
            "badge": sc["badge"],
            "return_rate_pct": round(r * 100),
            "label": sc["label"],
            "freedom_corpus": ff_calc["freedom_corpus"],
            "required_sip": ff_calc["required_sip"],
            "projected_corpus": projected_corpus,
            "years_to_target": f"{y_calc['years']}y {y_calc['months']}m" if y_calc["achievable"] else f">{y_calc['years']}y",
            "achievable": y_calc["achievable"]
        })

    return results


def calculate_readiness_score(
    emergency_fund_months: float,
    emi_burden_pct: float,
    savings_rate_pct: float,
    capacity_to_sip_ratio: float,
    horizon_years: int
) -> Dict[str, Any]:
    """
    Calculates an explainable 0-100 Financial Freedom Readiness Score.
    Points allocation:
    - Emergency Fund Readiness: up to 25 pts (6+ months = 25 pts)
    - Debt Burden: up to 25 pts (EMI < 20% = 25 pts, >50% = 0 pts)
    - Savings Rate: up to 20 pts (Surplus >= 35% = 20 pts)
    - Investment Capacity vs SIP: up to 20 pts (Ratio >= 1.0 = 20 pts)
    - Horizon Resilience: up to 10 pts (>= 10 yrs = 10 pts)
    """
    # 1. Emergency Fund (0-25)
    score_emergency = min(25.0, (emergency_fund_months / 6.0) * 25.0)

    # 2. Debt Burden (0-25)
    if emi_burden_pct <= 15.0:
        score_debt = 25.0
    elif emi_burden_pct <= 30.0:
        score_debt = 20.0
    elif emi_burden_pct <= 45.0:
        score_debt = 12.0
    elif emi_burden_pct <= 60.0:
        score_debt = 5.0
    else:
        score_debt = 0.0

    # 3. Savings Rate (0-20)
    score_savings = min(20.0, max(0.0, (savings_rate_pct / 35.0) * 20.0))

    # 4. Capacity Ratio (0-20)
    score_capacity = min(20.0, max(0.0, capacity_to_sip_ratio * 20.0))

    # 5. Horizon (0-10)
    score_horizon = min(10.0, max(2.0, (horizon_years / 10.0) * 10.0))

    total_score = round(score_emergency + score_debt + score_savings + score_capacity + score_horizon)
    total_score = max(5, min(98, total_score))

    if total_score >= 80:
        category = "Strong"
        color = "var(--fin-green)"
        summary = "Your cash flow foundation, low debt burden, and savings discipline put you on an enviable trajectory."
    elif total_score >= 60:
        category = "Progressing"
        color = "var(--accent-gold)"
        summary = "Solid financial fundamentals with healthy surplus; focusing on emergency reserve and debt reduction will accelerate your freedom milestone."
    elif total_score >= 40:
        category = "Building"
        color = "var(--fin-blue)"
        summary = "You have active surplus and investment intent. Prioritizing liquidity buffer and optimizing discretionary spending will dramatically boost resilience."
    else:
        category = "Starting"
        color = "var(--fin-amber)"
        summary = "Your journey begins with cash flow clarity. Taming monthly obligations and establishing a 3-month safety buffer is your highest-impact immediate win."

    explanations = [
        f"Emergency reserve provides {emergency_fund_months:.1f} months of protection ({round(score_emergency)}/25 pts).",
        f"EMI commitments consume {emi_burden_pct:.1f}% of monthly income ({round(score_debt)}/25 pts).",
        f"Monthly surplus savings rate is {savings_rate_pct:.1f}% of income ({round(score_savings)}/20 pts).",
        f"Safe investment capacity matches {round(capacity_to_sip_ratio * 100)}% of the recommended SIP target ({round(score_capacity)}/20 pts).",
        f"Planning time horizon is {horizon_years} years ({round(score_horizon)}/10 pts)."
    ]

    return {
        "score": total_score,
        "category": category,
        "color": color,
        "summary": summary,
        "breakdown": {
            "emergency_score": round(score_emergency),
            "debt_score": round(score_debt),
            "savings_score": round(score_savings),
            "capacity_score": round(score_capacity),
            "horizon_score": round(score_horizon)
        },
        "explanations": explanations
    }
