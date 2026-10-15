from .database import connection, dicts

def customers():
    with connection() as c:
        return dicts(c.execute("SELECT * FROM customers ORDER BY customer_id").fetchall())

def customer(cid):
    with connection() as c:
        row = c.execute("SELECT * FROM customers WHERE customer_id=?", (cid,)).fetchone()
        return dict(row) if row else None

def transactions(cid, limit=10):
    with connection() as c:
        return dicts(c.execute("SELECT * FROM transactions WHERE customer_id=? ORDER BY date DESC, transaction_id DESC LIMIT ?", (cid, max(1,min(limit,100)))).fetchall())

def transaction(tid, cid):
    with connection() as c:
        row = c.execute("SELECT * FROM transactions WHERE transaction_id=? AND customer_id=?", (tid,cid)).fetchone()
        return dict(row) if row else None

def spending(cid):
    txns = transactions(cid, 100)
    totals = {}
    for t in txns:
        if t["status"] != "Reversed":
            totals[t["category"]] = totals.get(t["category"], 0) + float(t["amount"])
    return {"transaction_count":len(txns), "total_spending":round(sum(totals.values()),2),
            "by_category":[{"category":k,"amount":round(v,2)} for k,v in sorted(totals.items(),key=lambda x:x[1],reverse=True)]}

def fraud_score(t):
    score, reasons = 0, []
    amount, location, status = float(t["amount"]), t["location"].lower(), t["status"].lower()
    if amount >= 50000: score += 45; reasons.append("High-value transaction (₹50,000 or more)")
    elif amount >= 20000: score += 25; reasons.append("Large transaction (₹20,000 or more)")
    if "unknown" in location or "overseas" in location: score += 30; reasons.append("Unknown or overseas location")
    if status == "review": score += 20; reasons.append("Transaction already marked for review")
    score = min(score,100)
    return {"transaction_id":t["transaction_id"],"risk_score":score,"risk_level":"High" if score>=70 else "Medium" if score>=35 else "Low",
            "reasons":reasons or ["No configured risk rule triggered"],"disclaimer":"Simulated signal, not a verified fraud finding."}

def emi(principal, annual_rate, months):
    if principal <= 0 or annual_rate < 0 or months <= 0: raise ValueError("Enter a positive amount and tenure, and a non-negative rate.")
    r = annual_rate / 1200
    payment = principal/months if r == 0 else principal*r*(1+r)**months/((1+r)**months-1)
    total = payment*months
    return {"principal":round(principal,2),"annual_interest_rate":annual_rate,"tenure_months":months,
            "monthly_emi":round(payment,2),"total_payment":round(total,2),"total_interest":round(total-principal,2)}

def loan_check(cid, amount=200000, rate=11, months=24):
    c = customer(cid)
    if not c: return None
    payment = emi(amount,rate,months)["monthly_emi"]
    dti = (c["existing_emi"]+payment)/max(c["monthly_income"],1)
    factors = []
    eligible = True
    if c["credit_score"] < 650: eligible=False; factors.append("Credit score is below demo threshold 650")
    else: factors.append("Credit score meets demo threshold 650")
    if dti > .45: eligible=False; factors.append("Estimated monthly debt burden exceeds 45% of income")
    else: factors.append("Estimated monthly debt burden is within demo limit")
    return {"customer_id":cid,"eligible":eligible,"requested_amount":amount,"annual_interest_rate":rate,"tenure_months":months,
            "estimated_emi":payment,"debt_to_income_ratio":round(dti,3),"credit_score":c["credit_score"],"factors":factors,
            "disclaimer":"Illustrative eligibility only; not a lending decision."}
