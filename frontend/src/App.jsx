import React, { useState, useEffect, useRef } from 'react';

// Roadmap lessons data mirroring
const ACADEMY_LESSONS = {
  beginner: [
    { id: 'l1', phase: '1. Stock Market Foundation', title: 'What is a stock?', desc: 'Understand what shares are and how companies divide ownership.', content: 'A stock represents fractional ownership of a corporation...' },
    { id: 'l2', phase: '1. Stock Market Foundation', title: 'Market Capitalization & Prices', desc: 'Understand market cap groups and price movements.', content: 'Market cap = Share Price x Outstanding Shares...' }
  ],
  basics: [
    { id: 'l3', phase: '2. Investment Products', title: 'Mutual Funds & Index Funds', desc: 'Discover pooled investments and index trackers.', content: 'Mutual funds pool investor money under active management...' },
    { id: 'l4', phase: '3. Smart Investing', title: 'Compounding & Inflation', desc: 'Learn about the power of compounding and inflation risks.', content: 'Compounding is generating returns on accumulated interest...' }
  ],
  intermediate: [
    { id: 'l7', phase: '1. Portfolio Optimization', title: 'Risk-Adjusted Returns & Sharpe Ratio', desc: 'Understand portfolio metrics, volatility, and ratios.', content: 'Sharpe ratio measures returns adjusted for deviation risk...' }
  ]
};

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('finpilot_token') || '');
  const [user, setUser] = useState(null);
  const [view, setView] = useState('home');
  const [financialIQ, setFinancialIQ] = useState(340);
  const [completedLessons, setCompletedLessons] = useState([]);
  
  // Auth Form State
  const [authMode, setAuthMode] = useState('signin'); // signin or signup
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authName, setAuthName] = useState('');
  const [authConfirm, setAuthConfirm] = useState('');
  const [authError, setAuthError] = useState('');

  // Academy roadmap States
  const [knowledgeLevel, setKnowledgeLevel] = useState(null);
  const [activeLesson, setActiveLesson] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [customQuery, setCustomQuery] = useState('');

  // Advisor States
  const [advAge, setAdvAge] = useState(28);
  const [advGoal, setAdvGoal] = useState('retirement');
  const [advIncome, setAdvIncome] = useState(75000);
  const [advExpenses, setAdvExpenses] = useState(35000);
  const [advCapacity, setAdvCapacity] = useState(15000);
  const [advSavings, setAdvSavings] = useState(150000);
  const [advDuration, setAdvDuration] = useState(10);
  const [advRisk, setAdvRisk] = useState('moderate');
  const [agentStatus, setAgentStatus] = useState('idle'); // idle, running, finished
  const [agentLogs, setAgentLogs] = useState([]);
  const [rebalanceAlerts, setRebalanceAlerts] = useState([]);
  const [portfolioHoldings, setPortfolioHoldings] = useState([]);
  const [activePortVal, setActivePortVal] = useState(0);

  // Simulator States
  const [simMode, setSimMode] = useState('sip');
  const [simAmount, setSimAmount] = useState(5000);
  const [simRate, setSimRate] = useState(12);
  const [simYears, setSimYears] = useState(15);
  const [simInflation, setSimInflation] = useState(6);
  const [goalTarget, setGoalTarget] = useState(5000000);
  const [solverResult, setSolverResult] = useState('');

  const canvasRef = useRef(null);

  // Load profile on start
  useEffect(() => {
    if (token) {
      fetchProfile();
    }
  }, [token]);

  // Redraw simulator canvas when parameters change
  useEffect(() => {
    if (view === 'simulator') {
      drawSimulationChart();
    }
  }, [view, simMode, simAmount, simRate, simYears, simInflation]);

  const fetchProfile = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/user/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 401) {
        handleLogout();
        return;
      }
      const data = await res.json();
      setUser(data);
      setFinancialIQ(data.financial_iq);
      setCompletedLessons(data.completed_lessons);
      
      if (data.goals) {
        setAdvAge(28);
        setAdvGoal(data.goals.goal_type);
        setAdvIncome(data.goals.monthly_capacity * 5); // back estimate
        setAdvRisk(data.goals.risk_appetite);
        setAdvDuration(data.goals.duration_years);
        setActivePortVal(data.goals.savings_amount + data.goals.monthly_capacity);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setAuthError('');
    if (authPassword !== authConfirm) {
      setAuthError('Passwords do not match.');
      return;
    }
    try {
      const res = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: authName, email: authEmail, password: authPassword })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Signup failed.');
      localStorage.setItem('finpilot_token', data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleSignin = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, password: authPassword })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Login failed.');
      localStorage.setItem('finpilot_token', data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('finpilot_token');
    setToken('');
    setUser(null);
    setCompletedLessons([]);
    setView('home');
  };

  const markLessonCompleted = async (lessonId) => {
    try {
      const res = await fetch('http://localhost:8000/api/user/lesson', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ lesson_id: lessonId })
      });
      const data = await res.json();
      setFinancialIQ(data.financial_iq);
      setCompletedLessons(prev => [...new Set([...prev, lessonId])]);
    } catch (err) {
      console.error(err);
    }
  };

  const triggerRebalancing = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/portfolio/rebalance', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ current_value: activePortVal, risk_appetite: advRisk })
      });
      const data = await res.json();
      setActivePortVal(data.total_value);
      setPortfolioHoldings(data.holdings);
      setRebalanceAlerts([{ title: 'Rebalanced successfully', desc: data.message }]);
    } catch (err) {
      console.error(err);
    }
  };

  const drawSimulationChart = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Simple drawing routine using state parameters
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#10b981';
    ctx.beginPath();
    ctx.moveTo(10, canvas.height - 10);
    ctx.quadraticCurveTo(canvas.width / 2, canvas.height / 2, canvas.width - 10, 10);
    ctx.stroke();
  };

  if (!token) {
    return (
      <div className="auth-overlay">
        <div className="auth-box glass-card">
          <h2>FinPilot AI</h2>
          <div className="auth-tabs">
            <button onClick={() => setAuthMode('signin')} className={authMode === 'signin' ? 'active' : ''}>Sign In</button>
            <button onClick={() => setAuthMode('signup')} className={authMode === 'signup' ? 'active' : ''}>Sign Up</button>
          </div>
          {authMode === 'signin' ? (
            <form onSubmit={handleSignin}>
              <input type="email" placeholder="Email" value={authEmail} onChange={e => setAuthEmail(e.target.value)} required />
              <input type="password" placeholder="Password" value={authPassword} onChange={e => setAuthPassword(e.target.value)} required />
              {authError && <div className="auth-error-msg">{authError}</div>}
              <button type="submit" className="btn btn-primary">Sign In</button>
            </form>
          ) : (
            <form onSubmit={handleSignup}>
              <input type="text" placeholder="Full Name" value={authName} onChange={e => setAuthName(e.target.value)} required />
              <input type="email" placeholder="Email" value={authEmail} onChange={e => setAuthEmail(e.target.value)} required />
              <input type="password" placeholder="Password" value={authPassword} onChange={e => setAuthPassword(e.target.value)} required />
              <input type="password" placeholder="Confirm Password" value={authConfirm} onChange={e => setAuthConfirm(e.target.value)} required />
              {authError && <div className="auth-error-msg">{authError}</div>}
              <button type="submit" className="btn btn-primary">Sign Up</button>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Dynamic React Panels matching sidebar switch routing */}
      <aside className="sidebar">
        <div className="logo-icon">Φ</div>
        <h2>FinPilot AI</h2>
        <nav>
          <button onClick={() => setView('home')}>Home</button>
          <button onClick={() => setView('academy')}>Academy</button>
          <button onClick={() => setView('advisor')}>Advisor</button>
          <button onClick={() => setView('simulator')}>Simulator</button>
        </nav>
        <div className="sidebar-iq-box">
          <span>Financial IQ: {financialIQ}</span>
        </div>
        <button onClick={handleLogout} className="btn-secondary">Log Out</button>
      </aside>

      <main className="main-content">
        <h1>Welcome, {user?.name || 'User'}</h1>
        {view === 'home' && <div>Hero dashboard content...</div>}
        {view === 'academy' && <div>Academy content...</div>}
        {view === 'advisor' && <div>Advisor content...</div>}
        {view === 'simulator' && (
          <div>
            <canvas ref={canvasRef} width="400" height="200" />
          </div>
        )}
      </main>
    </div>
  );
}
