from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .database import init_db
from . import tools
from .agents import Supervisor

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app=FastAPI(title="BankMind AI API",version="1.0.0",description="Simulated multi-agent banking MVP",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
supervisor=Supervisor()

class ChatRequest(BaseModel):
    message: str=Field(min_length=1,max_length=2000)
    customer_id: str="CUST-1001"
class EMIRequest(BaseModel):
    principal: float=Field(gt=0,le=100000000)
    annual_rate: float=Field(ge=0,le=100)
    tenure_months: int=Field(gt=0,le=600)

@app.get("/api/health")
def health(): return {"status":"ok","application":"BankMind AI","mode":"simulated"}
@app.get("/api/customers")
def get_customers(): return {"customers":tools.customers()}
@app.get("/api/dashboard")
def dashboard(customer_id:str="CUST-1001"):
    c=tools.customer(customer_id)
    if not c: raise HTTPException(404,"Demo customer not found")
    tx=tools.transactions(customer_id,8)
    risks=[tools.fraud_score(t) for t in tools.transactions(customer_id,100)]
    return {"customer":c,"transactions":tx,"spending":tools.spending(customer_id),"risk_alerts":[r for r in risks if r["risk_level"]!="Low"]}
@app.get("/api/transactions")
def get_transactions(customer_id:str="CUST-1001",limit:int=10):
    if not tools.customer(customer_id): raise HTTPException(404,"Demo customer not found")
    return {"transactions":tools.transactions(customer_id,limit)}
@app.post("/api/chat")
def chat(req:ChatRequest):
    try: return supervisor.handle(req.message.strip(),req.customer_id)
    except ValueError as e: raise HTTPException(404,str(e))
@app.post("/api/loan/emi")
def calculate(req:EMIRequest):
    try: return tools.emi(req.principal,req.annual_rate,req.tenure_months)
    except ValueError as e: raise HTTPException(400,str(e))
