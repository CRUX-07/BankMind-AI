import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .config import DATABASE_PATH

def _connect():
    path = Path(DATABASE_PATH)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def connection():
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with connection() as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS customers (
          customer_id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL,
          account_type TEXT NOT NULL, balance REAL NOT NULL, monthly_income REAL NOT NULL,
          credit_score INTEGER NOT NULL, existing_emi REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transactions (
          transaction_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, date TEXT NOT NULL,
          merchant TEXT NOT NULL, amount REAL NOT NULL, category TEXT NOT NULL,
          location TEXT NOT NULL, status TEXT NOT NULL
        );
        ''')
        if conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
            conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?)", [
              ("CUST-1001","Alex Morgan","alex.morgan@example.test","Premium Savings",45250,72000,742,8500),
              ("CUST-1002","Jamie Patel","jamie.patel@example.test","Everyday Savings",18640.5,48000,691,4200),
              ("CUST-1003","Taylor Chen","taylor.chen@example.test","Salary Account",91320.75,125000,781,12000)])
            conn.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", [
              ("TXN-9001","CUST-1001","2026-10-15","FreshMart Groceries",1840.5,"Groceries","Chennai","Completed"),
              ("TXN-9002","CUST-1001","2026-10-14","Metro Transit",120,"Transport","Chennai","Completed"),
              ("TXN-9003","CUST-1001","2026-10-13","StreamBox",499,"Subscriptions","Online","Completed"),
              ("TXN-9004","CUST-1001","2026-10-15","Overseas Electronics",78500,"Electronics","Unknown overseas location","Review"),
              ("TXN-9005","CUST-1001","2026-10-12","Cafe Corner",385,"Dining","Chennai","Completed"),
              ("TXN-9011","CUST-1002","2026-10-14","City Pharmacy",760,"Health","Chennai","Completed"),
              ("TXN-9012","CUST-1002","2026-10-13","Online Marketplace",3499,"Shopping","Online","Completed"),
              ("TXN-9021","CUST-1003","2026-10-15","Fuel Point",2200,"Transport","Chennai","Completed"),
              ("TXN-9022","CUST-1003","2026-10-12","TravelNow",14800,"Travel","Online","Completed")])
        conn.commit()

def dicts(rows):
    return [dict(row) for row in rows]
