import re
from .config import OPENAI_API_KEY, OPENAI_MODEL
from . import tools

INTENTS = {"balance","transactions","spending","fraud","loan_eligibility","emi","help"}

def local_intent(message):
    t = message.lower()
    if any(x in t for x in ("emi","monthly installment","monthly payment","calculate payment")): return "emi"
    if any(x in t for x in ("loan","eligible","eligibility","credit score")): return "loan_eligibility"
    if any(x in t for x in ("fraud","suspicious","risk","flagged","scam")): return "fraud"
    if any(x in t for x in ("spending","spent","expense","category","summary")): return "spending"
    if any(x in t for x in ("transaction","recent activity","history","purchase")): return "transactions"
    if any(x in t for x in ("balance","account","customer profile","my details")): return "balance"
    return "help"

def classify(message):
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            r = OpenAI(api_key=OPENAI_API_KEY).responses.create(
                model=OPENAI_MODEL,
                input=[{"role":"system","content":"Classify this banking demo request into exactly one token: balance, transactions, spending, fraud, loan_eligibility, emi, help. Return only the token."},
                       {"role":"user","content":message}])
            intent = re.sub(r"[^a-z_]","",r.output_text.strip().lower())
            if intent in INTENTS: return intent, "LLM intent classifier"
        except Exception:
            pass
    return local_intent(message), "Local intent router"

def txn_id(message):
    m = re.search(r"\bTXN-\d+\b", message.upper())
    return m.group(0) if m else None

def emi_params(message):
    nums = [float(n.replace(",","")) for n in re.findall(r"\d[\d,]*(?:\.\d+)?",message)]
    nums = [n for n in nums if n < 100000000]
    if len(nums)>=3: return nums[-3],nums[-2],int(nums[-1])
    if len(nums)==2: return nums[0],11,int(nums[1])
    if len(nums)==1: return nums[0],11,24
    return 200000,11,24

class Supervisor:
    def handle(self, message, cid):
        intent, classifier = classify(message)
        customer = tools.customer(cid)
        if not customer: raise ValueError("Demo customer not found")
        if intent == "balance":
            data = {k:customer[k] for k in ("customer_id","name","account_type","balance","email")}
            response, agent, tool = f"{customer['name']}'s simulated balance is ₹{customer['balance']:,.2f}.","Banking Agent","get_customer"
        elif intent == "transactions":
            data=tools.transactions(cid,8); response=f"Found {len(data)} recent transaction(s)."; agent,tool="Banking Agent","get_transactions"
        elif intent == "spending":
            data=tools.spending(cid); response=f"Recorded spending totals ₹{data['total_spending']:,.2f}."; agent,tool="Banking Agent","spending_summary"
        elif intent == "fraud":
            tid=txn_id(message); txns=[tools.transaction(tid,cid)] if tid else tools.transactions(cid,100)
            txns=[t for t in txns if t]
            data=sorted([tools.fraud_score(t) for t in txns],key=lambda x:x["risk_score"],reverse=True)
            response=(f"{data[0]['transaction_id']} has a simulated {data[0]['risk_level'].lower()} risk score of {data[0]['risk_score']}/100." if tid and data else f"Reviewed {len(data)} transaction(s); {sum(x['risk_level']=='High' for x in data)} are high risk.")
            if not data: response="No matching transaction found. Try TXN-9004."
            agent,tool="Risk & Fraud Agent","fraud_score"
        elif intent in ("loan_eligibility","emi"):
            if intent=="emi":
                amount,rate,months=emi_params(message); data=tools.emi(amount,rate,months)
                response=f"Estimated EMI is ₹{data['monthly_emi']:,.2f} per month for {months} months."
                tool="calculate_emi"
            else:
                data=tools.loan_check(cid)
                response=f"Profile {'meets' if data['eligible'] else 'does not meet'} the demo loan rules. Estimated EMI: ₹{data['estimated_emi']:,.2f}."
                tool="loan_check"
            agent="Credit & Loan Agent"
        else:
            data={"supported_intents":sorted(INTENTS-{"help"})}
            response="I can check balances, transactions, spending, suspicious transactions, loan eligibility, and EMI. Try: “Check TXN-9004 for fraud.”"
            agent,tool="Supervisor / Orchestrator","help_response"
        return {"message":response,"data":data,"trace":{"supervisor":"Supervisor / Orchestrator","classifier":classifier,"intent":intent,"agent":agent,"tool":tool,"status":"success"}}
