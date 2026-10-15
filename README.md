# BankMind AI — Multi-Agent Banking MVP

A simulated banking app with a supervisor/orchestrator and three specialized agents: Banking, Risk & Fraud, and Credit & Loan. Uses synthetic data only.

## Features
- Natural-language chat and agent routing.
- Account balance, transaction history, and spending summary.
- Rule-based suspicious-transaction scoring with explanations.
- Simulated loan eligibility and EMI calculator.
- Optional OpenAI intent classification; local routing works without an API key.
- React dashboard, execution traces, SQLite database, FastAPI API, and pytest tests.

## Architecture
React UI → FastAPI Supervisor → Banking / Fraud / Loan agents → deterministic tools → SQLite demo data.
The optional LLM classifies intent only. Banking facts and calculations come from backend tools.

## Run

### Backend (Python 3.11+)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### Frontend (Node.js 18+)
In another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

### Optional LLM
Copy `backend/.env.example` to `backend/.env`, set `OPENAI_API_KEY`, and restart the backend. Without a key, local intent routing is used. Never commit API keys.

### Tests
```bash
cd backend
pytest -q
```

## Demo prompts
- Show my account balance
- Show my recent transactions
- Summarize my spending
- Check TXN-9004 for fraud
- Am I eligible for a personal loan?
- Calculate EMI for a ₹200000 loan at 11% for 24 months

## Demo video outline (5–10 minutes)
1. Introduce the synthetic-data dashboard.
2. Ask for balance and recent transactions.
3. Check TXN-9004 and explain its risk factors.
4. Ask for loan eligibility and EMI.
5. Show the execution trace and `/docs` API page.
6. Explain the optional LLM and limitations.

## Limitations
Fraud alerts, loan eligibility, and all customer data are simulated. No real banking service is connected and no real transactions can be performed. The rule-based fraud score is an explainable MVP, not a production detector.
