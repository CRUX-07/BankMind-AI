import os, tempfile
os.environ["DATABASE_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")
from app.database import init_db
from app import tools
from app.agents import Supervisor

def setup_module(): init_db()
def test_seed_customer(): assert tools.customer("CUST-1001")["balance"] == 45250
def test_fraud_high(): assert tools.fraud_score(tools.transaction("TXN-9004","CUST-1001"))["risk_level"] == "High"
def test_emi(): assert tools.emi(200000,11,24)["monthly_emi"] > 0
def test_routing(): assert Supervisor().handle("show my balance","CUST-1001")["trace"]["agent"] == "Banking Agent"
def test_fraud_routing(): assert Supervisor().handle("check TXN-9004 for fraud","CUST-1001")["data"][0]["risk_level"] == "High"
