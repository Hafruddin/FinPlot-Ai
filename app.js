// FinPilot AI - Client Application Logic

// --- STATE MANAGEMENT ---
let appState = {
  activeView: 'home',
  financialIQ: 340,
  knowledgeLevel: null,
  selectedRisk: 'moderate',
  portfolioAccepted: false,
  simulatorMode: 'sip', // sip or lumpsum
  activeLesson: null,
  completedLessons: new Set(),
  portfolioData: null
};

// --- ROADMAP LESSONS DATA ---
const academyLessons = {
  beginner: [
    {
      id: 'l1',
      phase: '1. Stock Market Foundation',
      title: 'What is a stock?',
      desc: 'Understand what shares are and how companies divide ownership.',
      content: `<h3>Lesson: What is a stock?</h3>
      <p>A <strong>stock</strong> (or share) represents fractional ownership of a corporation. When you buy a stock of a company like Apple or Reliance, you become a co-owner of that business.</p>
      <p><strong>How companies generate value:</strong> Companies sell products and earn profits. As profits grow, the company becomes more valuable, and the price of your shares increases.</p>
      <p><strong>NSE vs BSE:</strong> National Stock Exchange (NSE) and Bombay Stock Exchange (BSE) are India's primary stock exchanges, facilitating trade. NSE's benchmark index is <em>Nifty 50</em>; BSE's is <em>Sensex</em>.</p>`,
      explained15: `Imagine a large pizza cut into 100 slices. If you buy 1 slice, you own 1% of the pizza. If the pizza becomes more delicious (the company earns more), people are willing to pay more for your slice!`,
      example: `If you bought shares in a local bakery for ₹1,000 to help them buy an oven, and the bakery expands to 3 shops, your ownership stake might now be worth ₹5,000.`,
      compare: `A stock is owning a single business (high risk, high return). Mutual funds are like a basket containing small pieces of 50 different businesses (lower risk, diversified).`
    },
    {
      id: 'l2',
      phase: '1. Stock Market Foundation',
      title: 'Market Capitalization & Prices',
      desc: 'Understand market cap groups and what makes stock prices tick.',
      content: `<h3>Lesson: Market Capitalization</h3>
      <p><strong>Market Cap:</strong> The total value of a company's outstanding shares. It is calculated as: <code>Market Cap = Share Price × Total Number of Shares</code>.</p>
      <p><strong>Classifications:</strong>
      <ul>
        <li><strong>Large-Cap:</strong> Stable industry giants (e.g., Apple, TCS). Lower volatility, slower growth.</li>
        <li><strong>Mid-Cap:</strong> Mid-sized firms with high expansion potential. Moderate risk.</li>
        <li><strong>Small-Cap:</strong> Startups/young firms. High growth potential, but high failure rates.</li>
      </ul>
      <p><strong>Price Movement:</strong> Driven strictly by supply and demand. If news is good, buyers bid prices higher. If bad, sellers push prices down.</p>`,
      explained15: `Market Cap is the total price tag of a whole company. Price movement is like bidding at an auction: if a lot of people want the same toy, the seller raises the price.`,
      example: `Reliance Industries has a market cap of over ₹18 Lakh Crores. This makes it a massive large-cap stock, highly resilient to sudden collapse.`,
      compare: `Large cap stocks are like cruise ships (stable, slow-moving). Small cap stocks are like speedboats (fast, nimble, but easily capsizable in stormy markets).`
    },
    {
      id: 'l3',
      phase: '2. Investment Products',
      title: 'Mutual Funds & Index Funds',
      desc: 'Discover pooled investments and passive tracking index funds.',
      content: `<h3>Lesson: Mutual Funds & Index Funds</h3>
      <p><strong>Mutual Funds:</strong> A pool of money collected from many investors. A professional Fund Manager invests this money in stocks, bonds, or other assets.</p>
      <p><strong>Index Funds:</strong> A special type of mutual fund that automatically tracks a market index (like Nifty 50 or S&P 500). There is no active stock-picker, making expense fees extremely low.</p>
      <p><strong>Expense Ratio:</strong> The annual fee charged by the fund to manage your money. Index funds usually charge 0.1% to 0.3%, whereas active funds charge 1% to 2%.</p>`,
      explained15: `Instead of choosing which candies to buy, you put your money together with friends to buy a pre-made bag of assorted candies. That's a mutual fund!`,
      example: `Investing in a Nifty 50 Index Fund means your money is automatically spread across India's top 50 companies (HDFC, Reliance, Infosys, etc.) in exact proportion.`,
      compare: `Active mutual funds try to outperform the market (using analysts; high fees). Index funds simply copy the market (passive; ultra-low fees). Over 80% of active funds fail to beat index funds over 10 years.`
    },
    {
      id: 'l4',
      phase: '3. Smart Investing',
      title: 'Compounding & Inflation',
      desc: 'Learn about the power of compound interest and the silent tax of inflation.',
      content: `<h3>Lesson: Compounding & Inflation</h3>
      <p><strong>Compounding:</strong> Earning interest on top of interest. Over time, your returns generate their own returns, creating exponential growth.</p>
      <p><strong>Inflation:</strong> The rate at which general prices rise, reducing your purchasing power. If inflation is 6%, your savings must earn more than 6% to avoid losing real value.</p>
      <p><strong>Rule of 72:</strong> Quick way to estimate doubling time: <code>72 / Interest Rate = Years to double</code>.</p>`,
      explained15: `Compounding is like a snowball rolling down a hill: it picks up more snow faster and faster. Inflation is a warm breeze melting your snowball slowly.`,
      example: `Investing ₹5,000 monthly for 20 years at 12% grows to ₹49.9 Lakhs. The amount you put in was ₹12 Lakhs; compounding generated the remaining ₹37.9 Lakhs!`,
      compare: `SIP (Systematic Investment Plan) invests small amounts regularly (averages purchase price). Lumpsum is a one-time investment (great if the market is low, but higher timing risk).`
    }
  ],
  basics: [
    {
      id: 'l5',
      phase: '1. Advanced Products',
      title: 'ETFs & Bonds',
      desc: 'Learn about Exchange Traded Funds and government/corporate debt bonds.',
      content: `<h3>Lesson: ETFs & Bonds</h3>
      <p><strong>ETFs (Exchange Traded Funds):</strong> Similar to mutual funds, but they trade directly on stock exchanges like individual stocks. You can buy/sell them in real time during trading hours.</p>
      <p><strong>Bonds:</strong> You lend money to a government or company in exchange for regular interest payments (coupons) and the return of principal at maturity. They act as safe debt reserves.</p>`,
      explained15: `A bond is a formal I.O.U. from a company or government. They pay you interest as thanks for the loan, and then pay back the full loan when the timer ends.`,
      example: `RBI Treasury Bonds pay a guaranteed annual yield of ~7% and are backed by the Indian Government, making them virtually risk-free.`,
      compare: `Bonds provide fixed, guaranteed income (safe). ETFs trade on exchanges and typically track stock/gold indices (variable prices, higher potential growth).`
    },
    {
      id: 'l6',
      phase: '2. Asset Allocation',
      title: 'Diversification & Rebalancing',
      desc: 'Explore the only free lunch in finance: Portfolio Diversification.',
      content: `<h3>Lesson: Diversification & Rebalancing</h3>
      <p><strong>Diversification:</strong> Spreading investments across different asset classes (Equity, Debt, Gold, Cash) and sectors to manage risk. If one asset class drops, others may rise.</p>
      <p><strong>Rebalancing:</strong> Periodically selling assets that have grown and buying assets that have fallen to return your portfolio to its target allocation (e.g. 50/50 equity-debt).</p>`,
      explained15: `Don't put all your eggs in one basket. If the basket drops, all eggs break. Put some eggs in a metal container, some in wood, and some in a basket.`,
      example: `If tech stocks dip due to a global chip shortage, your tech holdings fall, but your gold assets rise due to safety-seeking investors, buffering the overall loss.`,
      compare: `SIP averages out market entry prices over time. Rebalancing adjusts your asset mixture weights (e.g., selling overvalued equity to buy undervalued debt).`
    }
  ],
  intermediate: [
    {
      id: 'l7',
      phase: '1. Portfolio Optimization',
      title: 'Risk-Adjusted Returns & Sharpe Ratio',
      desc: 'Understand portfolio metrics, volatility, and how to measure true performance.',
      content: `<h3>Lesson: Risk-Adjusted Returns</h3>
      <p><strong>Standard Deviation:</strong> Measures the volatility of a fund's returns. Higher volatility means wider price swings.</p>
      <p><strong>Sharpe Ratio:</strong> Measures excess return per unit of deviation risk. Calculated as: <code>(Portfolio Return - Risk-free Rate) / Volatility</code>. A ratio above 1 is considered good.</p>
      <p><strong>Beta:</strong> Measures stock volatility compared to the market. Beta > 1 is more volatile than market; Beta < 1 is more stable.</p>`,
      explained15: `If two players score the same average points, but player A is highly erratic and player B is extremely consistent, player B has a better risk-adjusted score.`,
      example: `Mutual Fund X yields 15% with a volatility of 10%. Fund Y yields 16% with a volatility of 18%. Fund X has a higher Sharpe ratio and is a more efficient risk choice.`,
      compare: `Nominal return is simple absolute growth. Risk-adjusted return measures if that growth was worth the stomach-churning price swings.`
    }
  ]
};

// --- INITIALIZE APP ---
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  switchView('home');
  runSimulation(); // Initial calculation & canvas setup
});

function checkAuth() {
  const session = localStorage.getItem('finpilot_session');
  if (session) {
    const user = JSON.parse(session);
    document.getElementById('auth-overlay').classList.add('fade-out');
    updateProfileUI(user.name);
  } else {
    document.getElementById('auth-overlay').classList.remove('fade-out');
  }
}

function updateProfileUI(name) {
  document.getElementById('header-user-name').innerText = name;
  const initial = name ? name.trim().charAt(0).toUpperCase() : 'U';
  document.getElementById('header-user-avatar').innerText = initial;
}

function switchAuthTab(tab) {
  const signinForm = document.getElementById('signin-form');
  const signupForm = document.getElementById('signup-form');
  const signinTab = document.getElementById('auth-tab-signin');
  const signupTab = document.getElementById('auth-tab-signup');

  if (tab === 'signin') {
    signinForm.classList.add('active');
    signupForm.classList.remove('active');
    signinTab.classList.add('active');
    signupTab.classList.remove('active');
  } else {
    signinForm.classList.remove('active');
    signupForm.classList.add('active');
    signinTab.classList.remove('active');
    signupTab.classList.add('active');
  }
}

function handleSignin(e) {
  e.preventDefault();
  const email = document.getElementById('signin-email').value.trim().toLowerCase();
  const password = document.getElementById('signin-password').value;
  const errorDiv = document.getElementById('signin-error');
  errorDiv.style.display = 'none';

  const userKey = `finpilot_user_${email}`;
  const userData = localStorage.getItem(userKey);

  if (!userData) {
    errorDiv.innerText = "No account found with this email. Please Sign Up!";
    errorDiv.style.display = 'block';
    return;
  }

  const user = JSON.parse(userData);
  if (user.password !== password) {
    errorDiv.innerText = "Incorrect password. Please try again.";
    errorDiv.style.display = 'block';
    return;
  }

  // Success
  localStorage.setItem('finpilot_session', JSON.stringify({ name: user.name, email: user.email }));
  updateProfileUI(user.name);
  document.getElementById('auth-overlay').classList.add('fade-out');
  
  // Clear forms
  document.getElementById('signin-email').value = '';
  document.getElementById('signin-password').value = '';
}

function handleSignup(e) {
  e.preventDefault();
  const name = document.getElementById('signup-name').value.trim();
  const email = document.getElementById('signup-email').value.trim().toLowerCase();
  const password = document.getElementById('signup-password').value;
  const confirm = document.getElementById('signup-confirm').value;
  const errorDiv = document.getElementById('signup-error');
  errorDiv.style.display = 'none';

  if (password !== confirm) {
    errorDiv.innerText = "Passwords do not match.";
    errorDiv.style.display = 'block';
    return;
  }

  if (password.length < 6) {
    errorDiv.innerText = "Password must be at least 6 characters long.";
    errorDiv.style.display = 'block';
    return;
  }

  const userKey = `finpilot_user_${email}`;
  if (localStorage.getItem(userKey)) {
    errorDiv.innerText = "An account with this email already exists. Please Sign In.";
    errorDiv.style.display = 'block';
    return;
  }

  // Create User
  const newUser = { name, email, password };
  localStorage.setItem(userKey, JSON.stringify(newUser));

  // Set Session
  localStorage.setItem('finpilot_session', JSON.stringify({ name, email }));
  updateProfileUI(name);
  document.getElementById('auth-overlay').classList.add('fade-out');

  // Clear forms
  document.getElementById('signup-name').value = '';
  document.getElementById('signup-email').value = '';
  document.getElementById('signup-password').value = '';
  document.getElementById('signup-confirm').value = '';
}

function handleLogout() {
  localStorage.removeItem('finpilot_session');
  checkAuth();
  
  // Reset app state
  appState.financialIQ = 340;
  appState.completedLessons.clear();
  appState.knowledgeLevel = null;
  appState.activeLesson = null;
  updateFinancialIQ(0);

  // Reset panels to default state
  resetAcademySetup();
  resetAdvisor();
}

// --- ROUTER VIEW SWITCHER ---
function switchView(viewName) {
  // Update view classes
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  const targetPanel = document.getElementById(`view-${viewName}`);
  if (targetPanel) {
    targetPanel.classList.add('active');
  }

  // Update nav highlights
  document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
  const targetNav = document.getElementById(`nav-${viewName}`);
  if (targetNav) {
    targetNav.classList.add('active');
  }

  // Update header text
  const titleMap = {
    'home': 'FinPilot AI Mentor Home',
    'academy': 'FinPilot AI Investment Academy',
    'advisor': 'FinPilot AI Wealth Advisor Agent',
    'simulator': 'FinPilot Investment Simulator & Life Planner'
  };
  document.getElementById('top-bar-title').innerText = titleMap[viewName] || 'FinPilot AI';
  appState.activeView = viewName;

  // Handle canvas resize on tab switch
  if (viewName === 'simulator') {
    setTimeout(runSimulation, 50);
  }
}

// --- UPDATE FINANCIAL IQ BAR ---
function updateFinancialIQ(change = 0) {
  appState.financialIQ = Math.max(0, Math.min(1000, appState.financialIQ + change));
  
  // Elements
  const scoreVal = document.getElementById('sidebar-iq-score');
  const progress = document.getElementById('sidebar-iq-progress');
  const levelLabel = document.getElementById('sidebar-iq-level');

  scoreVal.innerText = appState.financialIQ;
  const pct = (appState.financialIQ / 1000) * 100;
  progress.style.width = `${pct}%`;

  // Change level label
  if (appState.financialIQ < 400) {
    levelLabel.innerText = 'Beginner Rank';
  } else if (appState.financialIQ < 700) {
    levelLabel.innerText = 'Basics Scholar';
  } else if (appState.financialIQ < 900) {
    levelLabel.innerText = 'Intermediate Investor';
  } else {
    levelLabel.innerText = 'Wealth Commander';
  }
}

// --- ACADEMY: CHOOSE KNOWLEDGE LEVEL ---
function selectKnowledge(level) {
  appState.knowledgeLevel = level;
  document.querySelectorAll('.selector-card').forEach(c => c.classList.remove('selected'));
  document.getElementById(`know-${level}`).classList.add('selected');
}

function resetAcademySetup() {
  document.getElementById('academy-setup').style.display = 'block';
  document.getElementById('academy-roadmap').style.display = 'none';
  appState.knowledgeLevel = null;
  document.querySelectorAll('.selector-card').forEach(c => c.classList.remove('selected'));
}

function generateRoadmap() {
  if (!appState.knowledgeLevel) {
    alert('Please select a knowledge level first!');
    return;
  }

  document.getElementById('academy-setup').style.display = 'none';
  document.getElementById('academy-roadmap').style.display = 'grid';

  const container = document.getElementById('roadmap-nodes-container');
  container.innerHTML = '';

  // Get relevant lessons list
  let selectedLessons = [];
  if (appState.knowledgeLevel === 'beginner') {
    selectedLessons = [...academyLessons.beginner, ...academyLessons.basics, ...academyLessons.intermediate];
  } else if (appState.knowledgeLevel === 'basics') {
    // Basics has beginner set completed already, starts with basics
    academyLessons.beginner.forEach(l => appState.completedLessons.add(l.id));
    selectedLessons = [...academyLessons.beginner, ...academyLessons.basics, ...academyLessons.intermediate];
  } else {
    // Intermediate has beginner and basics completed
    academyLessons.beginner.forEach(l => appState.completedLessons.add(l.id));
    academyLessons.basics.forEach(l => appState.completedLessons.add(l.id));
    selectedLessons = [...academyLessons.beginner, ...academyLessons.basics, ...academyLessons.intermediate];
  }

  // Update starting Financial IQ accordingly
  let baseScore = 340;
  if (appState.knowledgeLevel === 'basics') baseScore = 540;
  if (appState.knowledgeLevel === 'intermediate') baseScore = 780;
  appState.financialIQ = baseScore;
  updateFinancialIQ(0);

  // Group by Phase to render headers
  let currentPhase = '';
  selectedLessons.forEach((lesson, index) => {
    if (lesson.phase !== currentPhase) {
      currentPhase = lesson.phase;
      const phaseEl = document.createElement('div');
      phaseEl.className = 'roadmap-phase-title';
      phaseEl.innerText = currentPhase;
      container.appendChild(phaseEl);
    }

    // Node wrapper
    const nodeEl = document.createElement('div');
    nodeEl.id = `node-${lesson.id}`;

    // Determine status
    let statusClass = 'locked';
    let statusBadge = 'Locked';

    if (appState.completedLessons.has(lesson.id)) {
      statusClass = 'completed';
      statusBadge = 'Completed';
    } else {
      // It is ready if it's the first uncompleted lesson
      const previousLessons = selectedLessons.slice(0, index);
      const allPrevCompleted = previousLessons.every(pl => appState.completedLessons.has(pl.id));
      if (allPrevCompleted) {
        statusClass = 'active';
        statusBadge = 'Ready';
      }
    }

    nodeEl.className = `roadmap-node ${statusClass}`;
    nodeEl.innerHTML = `
      <div class="node-title-row">
        <span class="node-title">${lesson.title}</span>
        <span class="node-status-badge status-${statusClass}">${statusBadge}</span>
      </div>
      <p class="node-desc">${lesson.desc}</p>
    `;

    // Click behavior
    if (statusClass !== 'locked') {
      nodeEl.onclick = () => loadLesson(lesson);
    }

    container.appendChild(nodeEl);
  });
}

function loadLesson(lesson) {
  appState.activeLesson = lesson;

  // Add user bubble
  appendChatBubble('user', `Please teach me: "${lesson.title}"`);

  // Build lesson display in chat
  setTimeout(() => {
    const lessonHTML = `
      <div class="academy-lesson-content">
        ${lesson.content}
        <div style="margin-top:1.25rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
          <button class="quick-prompt-btn" style="background:rgba(99,102,241,0.15); border-color:var(--accent-indigo);" onclick="completeLesson('${lesson.id}')">
            ✓ Mark Topic Completed (+50 IQ)
          </button>
        </div>
      </div>
    `;
    appendChatBubble('assistant', lessonHTML);
  }, 300);
}

function completeLesson(lessonId) {
  if (appState.completedLessons.has(lessonId)) {
    return; // Already completed
  }

  appState.completedLessons.add(lessonId);
  updateFinancialIQ(50);
  
  // Re-render roadmap to unlock next modules
  generateRoadmap();

  appendChatBubble('assistant', `<p style="color:var(--accent-green); font-weight:600;">✓ Milestones reached! Your Financial IQ increased by 50 points. The next module is now unlocked.</p>`);
}

// --- TUTOR MESSAGING ENGINE ---
function appendChatBubble(sender, content) {
  const history = document.getElementById('tutor-chat-history');
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${sender}`;
  bubble.innerHTML = content;
  history.appendChild(bubble);
  history.scrollTop = history.scrollHeight;
}

function sendTutorPreset(prompt) {
  if (!appState.activeLesson) {
    appendChatBubble('assistant', '<p>Please select an active topic from the Roadmap timeline first so I can contextualize my explanation!</p>');
    return;
  }

  appendChatBubble('user', prompt);

  let reply = '';
  if (prompt.includes('15 years old')) {
    reply = `<p><strong>Explain like you are 15:</strong></p><p>${appState.activeLesson.explained15}</p>`;
  } else if (prompt.includes('real-world example')) {
    reply = `<p><strong>Real-world Case Study:</strong></p><p>${appState.activeLesson.example}</p>`;
  } else {
    reply = `<p><strong>Comparison:</strong></p><p>${appState.activeLesson.compare}</p>`;
  }

  setTimeout(() => {
    appendChatBubble('assistant', reply);
  }, 400);
}

function sendTutorCustom() {
  const input = document.getElementById('tutor-input');
  const query = input.value.trim();
  if (!query) return;

  appendChatBubble('user', query);
  input.value = '';

  // Generate mock intelligent answer based on terms
  setTimeout(() => {
    let response = `<p>That is an excellent question! Here is how we should look at that:</p>`;
    
    const queryLower = query.toLowerCase();
    if (queryLower.includes('sip') || queryLower.includes('systematic')) {
      response += `<p>A Systematic Investment Plan (SIP) helps you average out cost price. Instead of trying to guess whether the stock market is high or low (market timing), you buy consistent amounts monthly. When markets are down, you get more mutual fund units; when markets are up, your existing units grow in value.</p>`;
    } else if (queryLower.includes('risk') || queryLower.includes('lose')) {
      response += `<p>Risk is unavoidable in wealth creation. The key is distinguishing between <em>volatility</em> (prices moving up and down) and <em>permanent loss of capital</em> (buying a bad business that goes bankrupt). Diversifying across index funds, debt bonds, and gold ensures you are never exposed to single-point failure.</p>`;
    } else if (queryLower.includes('house') || queryLower.includes('property')) {
      response += `<p>Buying property involves large lumpsum down-payments. For durations under 5 years, rely heavily on safe Debt funds and FDs. For longer-term plans (10+ years), compounding equity mutual funds is more efficient to accumulate the down-payment corpus.</p>`;
    } else if (queryLower.includes('tax') || queryLower.includes('elss')) {
      response += `<p>In India, Equity Linked Savings Schemes (ELSS) allow you to save taxes under Section 80C. Capital gains tax (LTCG) is 12.5% for equity investments held over 1 year exceeding ₹1.25 Lakh profit, which is still lower than income tax tax-slabs.</p>`;
    } else {
      response += `<p>To build wealth effectively, align your asset mixtures with the target years. For short term goals, prioritize safety (liquidity). For long term goals, focus on compounding (equity). Let me know if you would like me to compare this with a specific asset class like gold or indices!</p>`;
    }

    appendChatBubble('assistant', response);
  }, 600);
}

// --- WEALTH ADVISOR CORE ---
function updateDurationLabel(val) {
  document.getElementById('duration-label').innerText = `Investment Duration: ${val} Years`;
}

function selectRisk(risk) {
  appState.selectedRisk = risk;
  document.querySelectorAll('.btn-toggle').forEach(b => {
    if (b.id.includes('risk-')) b.classList.remove('active');
  });
  document.getElementById(`risk-${risk}`).classList.add('active');
}

function runAdvisorAgents() {
  // Show Agent Workspace Panel
  document.getElementById('advisor-step-form').style.display = 'none';
  document.getElementById('advisor-agent-workspace').style.display = 'block';

  // Grab data inputs
  const age = parseInt(document.getElementById('adv-age').value);
  const income = parseFloat(document.getElementById('adv-income').value);
  const expenses = parseFloat(document.getElementById('adv-expenses').value);
  const capacity = parseFloat(document.getElementById('adv-capacity').value);
  const savings = parseFloat(document.getElementById('adv-savings').value);
  const duration = parseInt(document.getElementById('adv-duration').value);
  const goal = document.getElementById('adv-goal').value;

  appState.portfolioData = { age, income, expenses, capacity, savings, duration, goal };

  // Run sequence of simulated terminal logs
  const terminal = document.getElementById('agent-terminal');
  terminal.innerHTML = '';

  const writeLine = (timestamp, tag, text, styleClass = 'info') => {
    const line = document.createElement('div');
    line.className = 'terminal-line';
    line.innerHTML = `
      <span class="timestamp">[${timestamp}]</span>
      <span class="agent-tag" style="color:${tag === 'SYSTEM' ? '#f3f4f6' : 'var(--accent-indigo)'};">[${tag}]</span>
      <span class="${styleClass}">${text}</span>
    `;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
  };

  const setAgentStatus = (agentId, status, styleClass = '') => {
    const card = document.getElementById(`agent-card-${agentId}`);
    const text = document.getElementById(`agent-status-${agentId}`);
    
    // reset classes
    card.classList.remove('active', 'completed');
    if (styleClass) card.classList.add(styleClass);
    text.innerText = status;
  };

  // Timeline schedule
  setTimeout(() => {
    writeLine('21:12:01', 'SYSTEM', 'Parsed financial profile variables.', 'info');
    writeLine('21:12:02', 'SYSTEM', `Age: ${age} | Goal: ${goal.toUpperCase()} | Savings: ₹${savings.toLocaleString()}`, 'info');
    setAgentStatus('market', 'Scanning Markets...', 'active');
    writeLine('21:12:03', 'MARKET ANALYST', 'Scraping NSE indices, current PE ratios and sector averages...', 'info');
  }, 200);

  setTimeout(() => {
    writeLine('21:12:05', 'MARKET ANALYST', 'Nifty 50 PE ratio sits at 22.8 (neutral-to-fair valuation). Sector rotation indicates strong momentum in Financials & Infrastructure.', 'success');
    setAgentStatus('market', 'Analysis Done', 'completed');
    setAgentStatus('fund', 'Inspecting Funds...', 'active');
    writeLine('21:12:06', 'FUND AGENT', 'Filtering active mutual funds with AUM > ₹5,000Cr and tracking error < 0.25%...', 'info');
  }, 1200);

  setTimeout(() => {
    writeLine('21:12:08', 'FUND AGENT', 'Selected Large Cap Index tracker, Midcap growth basket, and Short-term liquid debt instruments.', 'success');
    setAgentStatus('fund', 'Selection Done', 'completed');
    setAgentStatus('risk', 'Assessing Downside...', 'active');
    writeLine('21:12:09', 'RISK AGENT', `Stochastic simulation for risk profile: ${appState.selectedRisk.toUpperCase()} & horizon: ${duration} years...`, 'info');
    writeLine('21:12:10', 'RISK AGENT', `Maximum projected drawdown computed at 18.4% during tail-events. Establishing liquidity reserve buffer.`, 'warn');
  }, 2400);

  setTimeout(() => {
    setAgentStatus('risk', 'Risks Mapped', 'completed');
    setAgentStatus('builder', 'Optimizing Portfolios...', 'active');
    writeLine('21:12:12', 'PORTFOLIO BUILDER', 'Solving asset mix weights to maximize Sharpe Ratio target...', 'info');
    writeLine('21:12:13', 'PORTFOLIO BUILDER', 'Formulating final explainable investment strategy.', 'success');
  }, 3600);

  setTimeout(() => {
    setAgentStatus('builder', 'Compiled', 'completed');
    // Transition to Recommendations page
    document.getElementById('advisor-agent-workspace').style.display = 'none';
    renderRecommendations();
  }, 4500);
}

// --- RENDER PORTFOLIO RECOMMENDATIONS ---
function renderRecommendations() {
  const recPanel = document.getElementById('advisor-recommendation');
  recPanel.classList.add('active');

  const risk = appState.selectedRisk;
  const goal = appState.portfolioData.goal;

  let allocations = [];
  let whyPoints = [];
  let alternativePoints = [];
  let riskPoints = [];

  // Tailor based on risk profile
  if (risk === 'conservative') {
    allocations = [
      { name: 'Debt Mutual Funds', weight: 70, color: '#6366f1' },
      { name: 'Index Funds (Equity)', weight: 20, color: '#10b981' },
      { name: 'Sovereign Gold Bonds', weight: 10, color: '#f59e0b' }
    ];
    whyPoints = [
      "Capital protection is highly prioritized given your conservative stance.",
      "70% allocation to Debt Funds generates stable yields (7-8% returns) insulated from stock market swings.",
      "10% in Gold acts as a hedge against global financial crises and inflation."
    ];
    alternativePoints = [
      "Why not 100% Equity? Equity has high volatility. A sudden 20% crash would violate your risk tolerance.",
      "Why not 100% Fixed Deposits? FDs do not beat inflation. You require at least 20% Index equity to preserve purchasing power."
    ];
    riskPoints = [
      "Interest Rate Risk: If interest rates spike, the yields on debt funds may drop temporarily.",
      "Lower Growth: This portfolio is unlikely to achieve double-digit returns over 10 years, meaning you must invest a larger principal to hit target milestones."
    ];
  } else if (risk === 'moderate') {
    allocations = [
      { name: 'Equity Index Funds', weight: 50, color: '#10b981' },
      { name: 'Large Cap Stocks', weight: 30, color: '#f59e0b' },
      { name: 'Gold / Commodities', weight: 10, color: '#6366f1' },
      { name: 'Liquid Cash / Debt Reserve', weight: 10, color: '#ef4444' }
    ];
    whyPoints = [
      "Bridges stability and long-term growth. Evaluated Sharpe ratio: 1.45.",
      "50% in passive broad market Index funds catches country growth at ultra-low fees.",
      "10% emergency cash ensures you never sell your equity during temporary market corrections."
    ];
    alternativePoints = [
      "Why not 90% Equity? Mid-term corrections would force panic sales. The cash/gold buffer stabilizes portfolio values.",
      "Why not 90% Debt? Debt is highly tax-inefficient for long durations, yielding sub-optimal compounding compared to equity."
    ];
    riskPoints = [
      "Market Correction Risk: A standard 10-15% stock correction will drop your portfolio value by 6-8%. Keep holding; historical markets recovery time averages 14 months.",
      "Inflation exposure: High cash levels drag down compound efficiency if held idle for decades."
    ];
  } else {
    // Aggressive
    allocations = [
      { name: 'Large & Mid-Cap Equity Funds', weight: 70, color: '#10b981' },
      { name: 'Direct Growth Stocks', weight: 20, color: '#f59e0b' },
      { name: 'Alternative Assets / Smallcap', weight: 10, color: '#6366f1' }
    ];
    whyPoints = [
      "Maximizes compounding potential to build long-term capital for goals over 15+ years.",
      "90% equity exposure catches massive multi-bagger sector trends (Tech, Energy, Infrastructure).",
      "Tailored for high risk-capacity investors who won't flinch during steep market recessions."
    ];
    alternativePoints = [
      "Why not Conservative? Safe debt investments will cause you to fall short of your ₹50L+ goals unless you double your monthly savings capacity.",
      "Why not crypto or microcaps? Highly speculative assets expose you to complete loss of principal. We stick to fundamental-backed assets."
    ];
    riskPoints = [
      "Severe Drawdown: A recession can reduce this portfolio value by 30-40% in a single year.",
      "Concentration Risk: Smallcap/Growth stocks can experience prolonged sideways performance spanning 3-5 years."
    ];
  }

  // Draw Pie Chart SVG
  const donut = document.getElementById('allocation-donut');
  donut.innerHTML = '';
  
  let accumulatedPercent = 0;
  allocations.forEach(alloc => {
    // Stroke dash math for circle SVG circumference
    const r = 25; // radius
    const circ = 2 * Math.PI * r;
    const dashArray = `${(alloc.weight / 100) * circ} ${circ}`;
    const dashOffset = -((accumulatedPercent / 100) * circ);

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("class", "donut-segment");
    circle.setAttribute("cx", "50");
    circle.setAttribute("cy", "50");
    circle.setAttribute("r", r);
    circle.setAttribute("stroke", alloc.color);
    circle.setAttribute("stroke-dasharray", dashArray);
    circle.setAttribute("stroke-dashoffset", dashOffset);
    donut.appendChild(circle);

    accumulatedPercent += alloc.weight;
  });

  // Add Center labels
  const labelGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
  labelGroup.setAttribute("class", "donut-label-group");
  labelGroup.innerHTML = `
    <text x="50%" y="46%" class="donut-center-title">${risk.toUpperCase()}</text>
    <text x="50%" y="62%" class="donut-center-sub">${allocations[0].weight}% Equity+</text>
  `;
  donut.appendChild(labelGroup);

  // Render Table Breakdown
  const table = document.getElementById('rec-allocation-list');
  table.innerHTML = '';
  allocations.forEach(alloc => {
    const pill = document.createElement('div');
    pill.className = 'allocation-pill';
    pill.innerHTML = `
      <span class="pill-color-indicator" style="background-color:${alloc.color}"></span>
      <span class="pill-name">${alloc.name}</span>
      <span class="pill-weight">${alloc.weight}%</span>
    `;
    table.appendChild(pill);
  });

  // Render Explainable tabs
  const fillList = (id, arr) => {
    const listEl = document.getElementById(id);
    listEl.innerHTML = '';
    arr.forEach(txt => {
      const li = document.createElement('li');
      li.innerText = txt;
      listEl.appendChild(li);
    });
  };

  fillList('list-explain-why', whyPoints);
  fillList('list-explain-alternatives', alternativePoints);
  fillList('list-explain-risks', riskPoints);
}

function switchExplainTab(tabName) {
  document.querySelectorAll('.explain-tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.explain-content-pane').forEach(pane => pane.classList.remove('active'));

  document.getElementById(`tab-explain-${tabName}`).classList.add('active');
  document.getElementById(`pane-explain-${tabName}`).classList.add('active');
}

function resetAdvisor() {
  document.getElementById('advisor-step-form').style.display = 'grid';
  document.getElementById('advisor-agent-workspace').style.display = 'none';
  document.getElementById('advisor-recommendation').classList.remove('active');
  document.getElementById('advisor-active-portfolio').classList.remove('active');
  appState.portfolioAccepted = false;
}

// --- PORTFOLIO ACCEPT & MONITOR SIMULATION ---
function acceptRecommendation() {
  document.getElementById('advisor-recommendation').classList.remove('active');
  const activePort = document.getElementById('advisor-active-portfolio');
  activePort.classList.add('active');
  appState.portfolioAccepted = true;

  // Initialize Portfolio variables
  const details = appState.portfolioData;
  const initialCapital = details.savings + details.capacity;
  
  document.getElementById('port-total-val').innerText = `₹${initialCapital.toLocaleString()}`;
  document.getElementById('port-total-gain').innerText = `+₹0.00 (0.0%)`;
  document.getElementById('port-risk-rating').innerText = appState.selectedRisk.toUpperCase();

  // Populate active allocations
  const breakdown = document.getElementById('port-allocation-breakdown');
  breakdown.innerHTML = '';

  let allocations = [];
  if (appState.selectedRisk === 'conservative') {
    allocations = [
      { name: 'Debt Mutual Funds', weight: 70, color: '#6366f1' },
      { name: 'Index Funds (Equity)', weight: 20, color: '#10b981' },
      { name: 'Sovereign Gold Bonds', weight: 10, color: '#f59e0b' }
    ];
  } else if (appState.selectedRisk === 'moderate') {
    allocations = [
      { name: 'Equity Index Funds', weight: 50, color: '#10b981' },
      { name: 'Large Cap Stocks', weight: 30, color: '#f59e0b' },
      { name: 'Gold / Commodities', weight: 10, color: '#6366f1' },
      { name: 'Liquid Cash / Debt Reserve', weight: 10, color: '#ef4444' }
    ];
  } else {
    allocations = [
      { name: 'Large & Mid-Cap Equity Funds', weight: 70, color: '#10b981' },
      { name: 'Direct Growth Stocks', weight: 20, color: '#f59e0b' },
      { name: 'Alternative Assets / Smallcap', weight: 10, color: '#6366f1' }
    ];
  }

  allocations.forEach(alloc => {
    const value = (alloc.weight / 100) * initialCapital;
    const pill = document.createElement('div');
    pill.className = 'allocation-pill';
    pill.id = `port-pill-${alloc.name.replace(/[^a-zA-Z]/g, '')}`;
    pill.innerHTML = `
      <span class="pill-color-indicator" style="background-color:${alloc.color}"></span>
      <span class="pill-name">${alloc.name}</span>
      <span style="display:flex; flex-direction:column; align-items:flex-end;">
        <span class="pill-weight" id="val-${pill.id}">₹${Math.round(value).toLocaleString()}</span>
        <span style="font-size:0.75rem; color:var(--text-secondary);">${alloc.weight}% weight</span>
      </span>
    `;
    breakdown.appendChild(pill);
  });

  // Push Guardian alert
  const alertLogs = document.getElementById('portfolio-monitor-logs');
  alertLogs.innerHTML = `
    <div class="alert-item info">
      <div class="alert-icon">🛡️</div>
      <div class="alert-text-box">
        <h5>Guardian Scan Completed</h5>
        <p>All target weights align with risk mandates. Simulated active market monitoring is active.</p>
      </div>
    </div>
  `;
}

function simulateMarketShift() {
  if (!appState.portfolioAccepted) return;

  const logs = document.getElementById('portfolio-monitor-logs');

  // Trigger alert
  const alertItem = document.createElement('div');
  alertItem.className = 'alert-item';
  alertItem.style.borderLeft = '3px solid var(--accent-red)';
  alertItem.innerHTML = `
    <div class="alert-icon">⚠️</div>
    <div class="alert-text-box" style="width:100%;">
      <h5>IT Sector Heavy Drag Detected</h5>
      <p>Tech indices drop 6.2%. Your Large Cap Equity allocation is over-exposed to IT companies (35%).</p>
      <div style="display:flex; gap:0.5rem; margin-top:0.5rem;">
        <button class="btn btn-secondary alert-action-btn" onclick="rebalancePortfolio(this)">Rebalance Assets</button>
        <button class="btn btn-secondary alert-action-btn" style="background:transparent; border:none;" onclick="this.parentElement.parentElement.parentElement.remove()">Dismiss</button>
      </div>
    </div>
  `;
  logs.insertBefore(alertItem, logs.firstChild);

  // Update total portfolio value to simulate a loss
  const details = appState.portfolioData;
  const originalVal = details.savings + details.capacity;
  const lossVal = originalVal * 0.965; // 3.5% loss

  document.getElementById('port-total-val').innerText = `₹${Math.round(lossVal).toLocaleString()}`;
  document.getElementById('port-total-gain').className = 'stat-val text-red';
  document.getElementById('port-total-gain').innerText = `-₹${Math.round(originalVal - lossVal).toLocaleString()} (-3.5%)`;
}

function rebalancePortfolio(btn) {
  // Rebalance shifts 5% from Equity into Gold/Reserve to restore equilibrium and shows a success toast
  const alertBox = btn.parentElement.parentElement.parentElement;
  alertBox.className = 'alert-item info';
  alertBox.style.borderLeft = 'none';
  alertBox.innerHTML = `
    <div class="alert-icon">✓</div>
    <div class="alert-text-box">
      <h5>Portfolio Diversified & Rebalanced</h5>
      <p>Reduced Tech stock weight. Reallocated capital to Sovereign Gold bonds and Liquid Reserves.</p>
    </div>
  `;

  // Restore returns to positive simulated gain
  const details = appState.portfolioData;
  const originalVal = details.savings + details.capacity;
  const recoveredVal = originalVal * 1.012; // +1.2%

  document.getElementById('port-total-val').innerText = `₹${Math.round(recoveredVal).toLocaleString()}`;
  document.getElementById('port-total-gain').className = 'stat-val gain';
  document.getElementById('port-total-gain').innerText = `+₹${Math.round(recoveredVal - originalVal).toLocaleString()} (+1.2%)`;

  // Trigger brief Toast notification
  showToast('AI Advisor Rebalanced Your Assets successfully.');
}

function showToast(msg) {
  const toast = document.createElement('div');
  toast.className = 'toast-msg';
  toast.innerHTML = `
    <span style="font-size:1.25rem;">🔔</span>
    <div>
      <h5 style="font-size:0.85rem; margin-bottom:2px;">Guardian Alert</h5>
      <p style="font-size:0.75rem; color:var(--text-secondary);">${msg}</p>
    </div>
  `;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

// --- WEALTH PROJECTOR SIMULATOR & PLANNERS ---
function toggleSimType(type) {
  appState.simulatorMode = type;
  document.getElementById('sim-btn-sip').classList.toggle('active', type === 'sip');
  document.getElementById('sim-btn-lump').classList.toggle('active', type === 'lumpsum');

  // Change slider title text
  const label = document.getElementById('sim-amount-label');
  if (type === 'sip') {
    label.innerText = 'Monthly Investment: ₹' + parseInt(document.getElementById('sim-amount').value).toLocaleString();
  } else {
    label.innerText = 'One-time Investment: ₹' + parseInt(document.getElementById('sim-amount').value).toLocaleString();
  }

  runSimulation();
}

function runSimulation() {
  const type = appState.simulatorMode;
  const amount = parseFloat(document.getElementById('sim-amount').value);
  const rate = parseFloat(document.getElementById('sim-rate').value) / 100;
  const years = parseInt(document.getElementById('sim-years').value);
  const inflation = parseFloat(document.getElementById('sim-inflation').value) / 100;

  // Update slider display labels
  if (type === 'sip') {
    document.getElementById('sim-amount-label').innerText = `Monthly Investment: ₹${amount.toLocaleString()}`;
  } else {
    document.getElementById('sim-amount-label').innerText = `One-time Investment: ₹${amount.toLocaleString()}`;
  }
  document.getElementById('sim-rate-label').innerText = `Expected Annual Return: ${Math.round(rate * 100)}%`;
  document.getElementById('sim-years-label').innerText = `Duration: ${years} Years`;
  document.getElementById('sim-inflation-label').innerText = `Inflation Rate: ${Math.round(inflation * 100)}%`;

  // Compounding math
  let totalInvested = 0;
  let futureValue = 0;
  let inflationAdjustedValue = 0;

  const pointsInvested = [];
  const pointsNominal = [];
  const pointsInflation = [];

  for (let y = 0; y <= years; y++) {
    if (type === 'sip') {
      const months = y * 12;
      const monthlyRate = rate / 12;
      
      if (y === 0) {
        totalInvested = 0;
        futureValue = 0;
      } else {
        totalInvested = amount * months;
        // SIP future value formula
        futureValue = amount * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate) * (1 + monthlyRate);
      }
    } else {
      // Lumpsum
      totalInvested = amount;
      futureValue = amount * Math.pow(1 + rate, y);
    }

    // Inflation adjustment: divide future value by inflation power
    inflationAdjustedValue = futureValue / Math.pow(1 + inflation, y);

    pointsInvested.push({ year: y, value: totalInvested });
    pointsNominal.push({ year: y, value: futureValue });
    pointsInflation.push({ year: y, value: inflationAdjustedValue });
  }

  // Update UI totals
  document.getElementById('stat-invested').innerText = `₹${Math.round(totalInvested).toLocaleString()}`;
  document.getElementById('stat-future').innerText = `₹${Math.round(futureValue).toLocaleString()}`;
  document.getElementById('stat-inflation-adj').innerText = `₹${Math.round(inflationAdjustedValue).toLocaleString()}`;

  // Draw chart on Canvas
  drawChart(pointsInvested, pointsNominal, pointsInflation, years);
}

function drawChart(invested, nominal, inflation, years) {
  const canvas = document.getElementById('simulator-canvas');
  if (!canvas) return;

  // Make canvas responsive high-DPI crisp
  const rect = canvas.parentNode.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio;
  canvas.height = rect.height * window.devicePixelRatio;
  canvas.style.width = '100%';
  canvas.style.height = '100%';

  const ctx = canvas.getContext('2d');
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

  const w = rect.width;
  const h = rect.height;

  // Padding
  const padLeft = 60;
  const padRight = 20;
  const padTop = 30;
  const padBottom = 40;

  const chartW = w - padLeft - padRight;
  const chartH = h - padTop - padBottom;

  ctx.clearRect(0, 0, w, h);

  // Find max value for Y scale
  let maxVal = 0;
  nominal.forEach(pt => { if (pt.value > maxVal) maxVal = pt.value; });
  if (maxVal === 0) maxVal = 100000;

  // Draw grid lines
  const gridCount = 4;
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.fillStyle = '#64748b';
  ctx.font = '9px monospace';
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';

  for (let i = 0; i <= gridCount; i++) {
    const val = (maxVal / gridCount) * i;
    const yPos = padTop + chartH - (i / gridCount) * chartH;
    
    // Line
    ctx.beginPath();
    ctx.moveTo(padLeft, yPos);
    ctx.lineTo(padLeft + chartW, yPos);
    ctx.stroke();

    // Text Label
    let label = '';
    if (val >= 10000000) label = `₹${(val / 10000000).toFixed(1)}Cr`;
    else if (val >= 100000) label = `₹${(val / 100000).toFixed(0)}L`;
    else label = `₹${(val / 1000).toFixed(0)}k`;
    ctx.fillText(label, padLeft - 10, yPos);
  }

  // Draw X-axis years
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  const labelInterval = Math.max(1, Math.round(years / 5));
  for (let y = 0; y <= years; y += labelInterval) {
    const xPos = padLeft + (y / years) * chartW;
    ctx.fillText(`${y}Y`, xPos, padTop + chartH + 10);
  }

  // Helper function to plot lines
  const drawLine = (pts, strokeColor, fillColor = null) => {
    ctx.beginPath();
    pts.forEach((pt, index) => {
      const x = padLeft + (pt.year / years) * chartW;
      const y = padTop + chartH - (pt.value / maxVal) * chartH;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 2.5;
    ctx.stroke();

    if (fillColor) {
      // Create path down to bottom to fill area under curves
      const firstX = padLeft;
      const lastX = padLeft + chartW;
      ctx.lineTo(lastX, padTop + chartH);
      ctx.lineTo(firstX, padTop + chartH);
      ctx.closePath();
      ctx.fillStyle = fillColor;
      ctx.fill();
    }
  };

  // Draw lines
  drawLine(invested, '#64748b'); // Principal (Slate)
  drawLine(inflation, '#6366f1', 'rgba(99, 102, 241, 0.03)'); // Inflation-adjusted (Indigo)
  drawLine(nominal, '#10b981', 'rgba(16, 185, 129, 0.05)'); // Nominal total (Emerald)
}

// --- GOAL TARGET SOLVER ---
function solveGoalTarget() {
  const target = parseFloat(document.getElementById('goal-target').value);
  const years = parseInt(document.getElementById('sim-years').value);
  const rate = parseFloat(document.getElementById('sim-rate').value) / 100;
  
  if (isNaN(target) || target <= 0) {
    alert("Please enter a valid target amount.");
    return;
  }

  const months = years * 12;
  const monthlyRate = rate / 12;

  // SIP solver: P = target * r / (((1+r)^n - 1) * (1+r))
  const solvedSIP = target * monthlyRate / ((Math.pow(1 + monthlyRate, months) - 1) * (1 + monthlyRate));

  const resultEl = document.getElementById('goal-solver-result');
  resultEl.style.display = 'block';

  let displayStr = '';
  if (target >= 10000000) displayStr = `${(target / 10000000).toFixed(2)} Crores`;
  else displayStr = `${(target / 100000).toFixed(2)} Lakhs`;

  resultEl.innerHTML = `
    <div style="background:rgba(16,185,129,0.06); border:1px dashed var(--accent-green); border-radius:10px; padding:0.75rem;">
      <p style="color:var(--text-secondary); font-size:0.75rem; text-transform:uppercase;">Solved SIP Goal Target</p>
      <h4 style="font-size:1.15rem; color:#f3f4f6; margin-top:2px;">₹${Math.round(solvedSIP).toLocaleString()}<span style="font-size:0.8rem; font-weight:normal; color:var(--text-secondary);"> / month</span></h4>
      <p style="font-size:0.75rem; color:var(--text-secondary); margin-top:0.25rem;">Required at ${rate*100}% returns to reach ₹${displayStr} in ${years} years.</p>
    </div>
  `;

  // Set the calculator amount to the solved SIP and refresh graphs
  document.getElementById('sim-amount').value = Math.round(solvedSIP);
  runSimulation();
  showToast('Simulator values adjusted to hit your target goal.');
}
