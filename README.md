# FinPilot AI — Your Personal AI Wealth Mentor 🚀

> *"Before helping people invest money, help them understand money."*

FinPilot AI is an education-first personal wealth intelligence platform that combines **financial education**, **interactive goal planning**, **real-time market analytics**, **what-if wealth simulations**, and **AI-powered financial mentoring** into a single cohesive experience.

---

## ✨ Features

- 🧭 **Guide Mode & Solo Mode**: Choose between guided step-by-step financial roadmaps or independent exploratory planning.
- 🎓 **Financial Learn Hub & Modules**: 10 financial literacy chapters covering fundamental ratios, compounding, asset allocation, and market cycles.
- 🤖 **AI Financial Mentor & Copilot**: Interactive context-aware tutor that explains complex concepts (P/E ratios, risk management, inflation drag) with zero financial jargon.
- 📊 **Real-Time Markets & Candlestick Charts**: Live market status for NSE/BSE, indices (Nifty 50, Sensex), multi-timeframe interactive candlestick/line/bar charts with volume histograms and crosshair inspection.
- 💼 **Mutual Funds Explorer & Detail Modals**: Search and filter mutual funds by category (Index, Large Cap, Flexi Cap, Mid Cap, Hybrid, Debt) and risk level with NAV, AUM, expense ratios, and historical CAGR.
- 🎯 **Goal Feasibility & Gap Solver**: Calculate required SIPs and capital milestones for Retirement, Real Estate, Higher Education, and Vehicle purchases.
- 🔬 **Wealth Simulator & What-If Lab**: Simulate SIP, Lumpsum, and Combo wealth accumulation scenarios adjusted for inflation and real purchasing power.
- 🛡️ **Portfolio Guardian**: Automated portfolio health check alerting against asset concentration, equity-debt imbalances, and high expense drag.

---

## 🌐 Deploy to Netlify

FinPilot AI is fully optimized for **Netlify** out of the box with zero build steps required:

1. Push your code to GitHub (already configured with `netlify.toml` and `_redirects`).
2. Log in to [Netlify](https://www.netlify.com/) and click **"Add new site"** > **"Import an existing project"**.
3. Select your GitHub repository: `Hafruddin/FinPlot-Ai`.
4. Keep the default settings:
   - **Publish directory**: `.` (or leave blank)
   - **Build command**: *(none required)*
5. Click **"Deploy Site"**. Your application will be live in seconds!

---

## 💻 Local Development Setup

To run locally with the FastAPI Python backend for live database persistence and market simulations:

### 1. Clone the repository
```bash
git clone https://github.com/Hafruddin/FinPlot-Ai.git
cd FinPlot-Ai
```

### 2. Create and activate a Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: .\venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install fastapi uvicorn pydantic python-jose passlib[bcrypt]
```

### 4. Start the application
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🔒 Security & License

- Licensed under the MIT License.
