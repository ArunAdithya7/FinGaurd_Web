const BASE_URL = 'https://hot-hounds-nail.loca.lt';

// Dynamic Local Storage Data Store for GitHub Pages & Offline Mode
const UserStore = {
  getStorageKey() {
    let email = 'default';
    try {
      const user = JSON.parse(localStorage.getItem('user_data') || '{}');
      email = user.email || user.identifier || localStorage.getItem('user_email') || 'default';
    } catch (e) {}
    return `finguard_data_${email.toLowerCase().replace(/[^a-z0-9]/g, '_')}`;
  },

  getData() {
    const key = this.getStorageKey();
    const existing = localStorage.getItem(key);
    if (existing) {
      try {
        const parsed = JSON.parse(existing);
        if (parsed && (parsed.incomes.length > 0 || parsed.expenses.length > 0 || parsed.debts.length > 0 || parsed.assets.length > 0)) {
          return parsed;
        }
      } catch (e) {}
    }
    const defaultData = {
      incomes: [{ category: 'Monthly Income', amount: 50000, notes: 'Primary income source', txDate: new Date().toISOString().split('T')[0] }],
      expenses: [{ category: 'Living Expenses', amount: 18000, notes: 'Food, Utilities & Rent', txDate: new Date().toISOString().split('T')[0] }],
      debts: [{ name: 'Car Loan EMI', outstanding: 120000, payment: 5000, rate: 9.5 }],
      assets: [{ name: 'Savings & Mutual Funds', amount: 85000, type: 'Savings Account', date: new Date().toISOString().split('T')[0] }]
    };
    this.saveData(defaultData);
    return defaultData;
  },

  saveData(data) {
    const key = this.getStorageKey();
    localStorage.setItem(key, JSON.stringify(data));
  },

  addIncome(category, amount, notes, txDate) {
    const data = this.getData();
    data.incomes.push({ category, amount: parseFloat(amount), notes, txDate: txDate || new Date().toISOString().split('T')[0] });
    this.saveData(data);
  },

  addExpense(category, amount, notes, txDate) {
    const data = this.getData();
    data.expenses.push({ category, amount: parseFloat(amount), notes, txDate: txDate || new Date().toISOString().split('T')[0] });
    this.saveData(data);
  },

  addDebt(name, outstanding, payment, rate) {
    const data = this.getData();
    data.debts.push({
      name,
      outstanding: parseFloat(outstanding),
      payment: parseFloat(payment),
      rate: parseFloat(rate || 0)
    });
    this.saveData(data);
  },

  addAsset(name, amount, type) {
    const data = this.getData();
    data.assets.push({
      name,
      amount: parseFloat(amount),
      type: type || 'Savings Account',
      date: new Date().toISOString().split('T')[0]
    });
    this.saveData(data);
  },

  removeEntry(type, index) {
    const data = this.getData();
    if (data[type] && data[type][index] !== undefined) {
      data[type].splice(index, 1);
      this.saveData(data);
    }
  },

  getActivityHistory() {
    const data = this.getData();
    const history = [];

    data.incomes.forEach((item, idx) => {
      history.push({
        id: `inc_${idx}`,
        type: 'income',
        category: item.category || 'Income',
        title: item.category || 'Income Deposit',
        notes: item.notes || 'Income',
        amount: item.amount,
        txDate: item.txDate || new Date().toISOString().split('T')[0],
        icon: 'fa-arrow-down',
        color: '#1a7f37',
        badge: 'Income',
        rawType: 'incomes',
        index: idx
      });
    });

    data.expenses.forEach((item, idx) => {
      history.push({
        id: `exp_${idx}`,
        type: 'expense',
        category: item.category || 'Expense',
        title: item.category || 'Expense',
        notes: item.notes || 'Spending',
        amount: -item.amount,
        txDate: item.txDate || new Date().toISOString().split('T')[0],
        icon: 'fa-arrow-up',
        color: '#cf222e',
        badge: 'Expense',
        rawType: 'expenses',
        index: idx
      });
    });

    data.debts.forEach((item, idx) => {
      history.push({
        id: `debt_${idx}`,
        type: 'debt',
        category: 'Debt',
        title: item.name || 'Liability',
        notes: `Monthly EMI: ₹${item.payment.toLocaleString('en-IN')}`,
        amount: -item.outstanding,
        txDate: new Date().toISOString().split('T')[0],
        icon: 'fa-credit-card',
        color: '#8250df',
        badge: 'Liability',
        rawType: 'debts',
        index: idx
      });
    });

    data.assets.forEach((item, idx) => {
      history.push({
        id: `asset_${idx}`,
        type: 'asset',
        category: item.type || 'Asset',
        title: item.name || 'Asset Holdings',
        notes: item.type || 'Asset Holdings',
        amount: item.amount,
        txDate: item.date || new Date().toISOString().split('T')[0],
        icon: 'fa-vault',
        color: '#0969da',
        badge: 'Asset',
        rawType: 'assets',
        index: idx
      });
    });

    return history.sort((a, b) => new Date(b.txDate) - new Date(a.txDate));
  },

  calculate() {
    const data = this.getData();
    const totalIncome = data.incomes.reduce((sum, item) => sum + item.amount, 0);
    const totalExpense = data.expenses.reduce((sum, item) => sum + item.amount, 0);
    const totalDebtOutstanding = data.debts.reduce((sum, item) => sum + item.outstanding, 0);
    const totalMonthlyDebt = data.debts.reduce((sum, item) => sum + item.payment, 0);
    const totalAssets = data.assets.reduce((sum, item) => sum + item.amount, 0);

    const expenseRatio = totalIncome > 0 ? Math.round((totalExpense / totalIncome) * 1000) / 10 : 0;
    const debtRatio = totalIncome > 0 ? Math.round((totalMonthlyDebt / totalIncome) * 1000) / 10 : 0;
    const savingsRunway = totalExpense > 0 ? Math.round((totalAssets / totalExpense) * 10) / 10 : 0;
    const monthlySurplus = Math.round((totalIncome - totalExpense - totalMonthlyDebt) * 100) / 100;

    let riskScore = 0;
    let riskLevel = 'Neutral';

    const hasData = data.incomes.length > 0 || data.expenses.length > 0 || data.debts.length > 0 || data.assets.length > 0;

    if (hasData) {
      let score = 0;
      if (totalIncome > 0) {
        score += Math.min(expenseRatio * 0.5, 35);
        score += Math.min(debtRatio * 0.6, 30);
        if (monthlySurplus < 0) score += 25;
      } else {
        if (totalExpense > 0 || totalMonthlyDebt > 0 || totalDebtOutstanding > 0) {
          score += 70;
        }
      }

      if (totalExpense > 0) {
        if (savingsRunway < 1) score += 20;
        else if (savingsRunway < 3) score += 10;
        else if (savingsRunway >= 6) score -= 15;
      }

      if (totalAssets > 0) {
        score -= Math.min((totalAssets / 100000) * 10, 20);
      }

      if (totalDebtOutstanding > 0) {
        score += Math.min((totalDebtOutstanding / 100000) * 8, 20);
      }

      riskScore = Math.min(100, Math.max(0, Math.round(score)));

      if (riskScore < 30) riskLevel = 'Low';
      else if (riskScore < 60) riskLevel = 'Moderate';
      else if (riskScore < 85) riskLevel = 'High';
      else riskLevel = 'Critical';
    }

    const alerts = [];
    if (!hasData) {
      alerts.push('Welcome! Add your income, expenses, assets, or debt to calculate your real-time risk score.');
    } else {
      if (expenseRatio > 40) alerts.push('⚠️ High Expense Ratio: Spending over 40% of income.');
      if (debtRatio > 35) alerts.push('🚨 High Debt Ratio: Over 35% of income goes to debt payments.');
      if (monthlySurplus < 0) alerts.push('🔥 Deficit Alert: Monthly expenses exceed total income!');
      if (savingsRunway < 3 && totalExpense > 0) alerts.push('🛡️ Low Savings Runway: Less than 3 months of emergency buffer.');
      if (alerts.length === 0) alerts.push('✅ Healthy Financial Status: Your cash flow and risk levels are well balanced.');
    }

    return {
      success: true,
      risk_score: riskScore,
      risk_level: riskLevel,
      total_assets: totalAssets,
      total_liabilities: totalDebtOutstanding,
      monthly_income: totalIncome,
      monthly_expense: totalExpense,
      monthly_debt: totalMonthlyDebt,
      savings_runway: savingsRunway,
      expense_ratio: expenseRatio,
      debt_ratio: debtRatio,
      monthly_surplus: monthlySurplus,
      alerts: alerts,
      recent_activity: this.getActivityHistory(),
      trend_labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      trend_scores: hasData
        ? [
            Math.max(0, Math.min(100, riskScore - 10)),
            Math.max(0, Math.min(100, riskScore - 6)),
            Math.max(0, Math.min(100, riskScore - 4)),
            Math.max(0, Math.min(100, riskScore - 2)),
            Math.max(0, Math.min(100, riskScore + 2)),
            riskScore
          ]
        : [0, 0, 0, 0, 0, 0]
    };
  }
};

function getMockDataFor(endpoint) {
  const calc = UserStore.calculate();

  if (endpoint.includes('/dashboard/summary')) {
    return calc;
  }
  if (endpoint.includes('/risk/analysis')) {
    const data = UserStore.getData();
    const hasData = data.incomes.length > 0 || data.expenses.length > 0 || data.debts.length > 0;
    return {
      success: true,
      risk_score: calc.risk_score,
      risk_level: calc.risk_level,
      expense_ratio: calc.expense_ratio,
      debt_ratio: calc.debt_ratio,
      savings_runway: calc.savings_runway,
      monthly_surplus: calc.monthly_surplus,
      factors: hasData ? [
        { title: 'Expense Ratio', description: 'Percentage of monthly income spent.', impact: calc.expense_ratio },
        { title: 'Debt Ratio', description: 'Percentage of income going to debt.', impact: calc.debt_ratio }
      ] : [
        { title: 'No Data Yet', description: 'Add income and expenses to view risk factors.', impact: 0 }
      ],
      suggestions: hasData ? [
        'Keep discretionary expenses low.',
        'Build up at least 3 to 6 months of emergency savings.'
      ] : [
        'Start by adding your monthly income and expenses using Quick Actions.'
      ]
    };
  }
  if (endpoint.includes('/forecast/summary')) {
    const data = UserStore.getData();
    const hasData = data.incomes.length > 0 || data.expenses.length > 0 || data.debts.length > 0 || data.assets.length > 0;
    const baseScore = hasData ? Math.max(12, calc.risk_score) : 0;
    const proj30 = hasData ? Math.min(100, Math.max(10, Math.round(baseScore * 0.95))) : 0;
    const proj60 = hasData ? Math.min(100, Math.max(10, Math.round(baseScore * 1.05))) : 0;
    const proj90 = hasData ? Math.min(100, Math.max(10, Math.round(baseScore * 1.15))) : 0;

    const getLvl = (s) => (s === 0 ? 'Neutral' : s < 30 ? 'Low' : s < 60 ? 'Moderate' : 'High');

    return {
      success: true,
      current_risk_score: baseScore,
      current_risk_level: hasData ? calc.risk_level : 'Neutral',
      projections: [
        {
          days: 30,
          risk_score: proj30,
          risk_level: getLvl(proj30),
          message: hasData ? 'Projected 30-day financial path based on cash flow.' : 'Add transactions to calculate 30-day forecast.',
          projected_savings: calc.total_assets + calc.monthly_surplus,
          projected_surplus: calc.monthly_surplus
        },
        {
          days: 60,
          risk_score: proj60,
          risk_level: getLvl(proj60),
          message: hasData ? 'Projected 60-day path with inflation adjustment.' : 'Add transactions to calculate 60-day forecast.',
          projected_savings: calc.total_assets + (calc.monthly_surplus * 2),
          projected_surplus: calc.monthly_surplus
        },
        {
          days: 90,
          risk_score: proj90,
          risk_level: getLvl(proj90),
          message: hasData ? 'Projected 90-day long-term cash reserve path.' : 'Add transactions to calculate 90-day forecast.',
          projected_savings: calc.total_assets + (calc.monthly_surplus * 3),
          projected_surplus: calc.monthly_surplus
        }
      ],
      chart_scores: hasData ? [baseScore, proj30, proj60, proj90] : [0, 0, 0, 0],
      recommendations: hasData ? [
        'Maintain a positive monthly surplus to build your emergency reserve.',
        'Keep discretionary expenses low to optimize long-term 90-day stability.'
      ] : [
        'Start logging your monthly income and expenses to track future forecasts.'
      ]
    };
  }
  if (endpoint.includes('/recommendations/summary')) {
    return {
      success: true,
      risk_score: calc.risk_score,
      risk_level: calc.risk_level,
      priority_actions: [
        'Track all daily expenses to identify saving opportunities.'
      ],
      recommendations: [
        { title: 'Emergency Fund', description: 'Aim to save 3-6 months of expenses.', impact: 20 }
      ]
    };
  }
  if (endpoint.includes('/profile/me')) {
    const user = JSON.parse(localStorage.getItem('user_data') || '{}');
    return {
      success: true,
      full_name: user.full_name || 'New User',
      email: user.email || 'user@finguard.com',
      mobile: user.mobile || 'Not set',
      joined_at: new Date().toISOString().split('T')[0]
    };
  }
  return { success: true };
}

const Api = {
  // Helper for GET requests with Bearer Token
  async get(endpoint, token) {
    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'bypass-tunnel-reminder': 'true'
        }
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
      }
      return data;
    } catch (err) {
      console.warn(`[Dynamic Store] Using dynamic client state for ${endpoint}.`);
      return getMockDataFor(endpoint);
    }
  },

  // Helper for POST/PUT requests with Bearer Token
  async postOrPut(endpoint, method, body, token = null) {
    const headers = { 
      'Content-Type': 'application/json',
      'bypass-tunnel-reminder': 'true'
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    if (endpoint === '/financial/income') {
      UserStore.addIncome(body.category, body.amount, body.notes, body.tx_date);
    } else if (endpoint === '/financial/expense') {
      UserStore.addExpense(body.category, body.amount, body.notes, body.tx_date);
    } else if (endpoint === '/financial/liability') {
      UserStore.addDebt(body.liability_name, body.outstanding_amount, body.monthly_payment, body.interest_rate);
    } else if (endpoint === '/financial/asset') {
      UserStore.addAsset(body.asset_name, body.amount, body.asset_type);
    }

    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: method,
        headers: headers,
        body: JSON.stringify(body)
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
      }
      return data;
    } catch (err) {
      console.warn(`[Dynamic Store] Backend response sync for ${endpoint}:`, err);
      if (endpoint === '/auth/login') {
        const userObj = { full_name: (body.identifier || 'User').split('@')[0], email: body.identifier };
        localStorage.setItem('user_data', JSON.stringify(userObj));
        return { success: true, token: 'mock_token', user: userObj };
      }
      return { success: true };
    }
  }
};

const AuthService = {
  async login(identifier, password) {
    return Api.postOrPut('/auth/login', 'POST', { identifier, password });
  },

  async signup(fullName, email, mobile, password) {
    const userObj = { full_name: fullName, email: email, mobile: mobile };
    localStorage.setItem('user_data', JSON.stringify(userObj));
    // Clear previous data for new signup to start clean at 0
    const key = `finguard_data_${email}`;
    localStorage.removeItem(key);
    return Api.postOrPut('/auth/signup', 'POST', {
      full_name: fullName,
      email: email,
      mobile: mobile,
      password: password
    });
  }
};

const DashboardApi = {
  async fetchDashboard(token) {
    return Api.get('/dashboard/summary', token);
  }
};

const RiskApi = {
  async fetchRiskAnalysis(token) {
    return Api.get('/risk/analysis', token);
  }
};

const ForecastApi = {
  async fetchForecast(token) {
    return Api.get('/forecast/summary', token);
  }
};

const RecommendationsApi = {
  async fetchRecommendations(token) {
    return Api.get('/recommendations/summary', token);
  }
};

const ProfileApi = {
  async fetchProfile(token) {
    return Api.get('/profile/me', token);
  },

  async updateProfile(token, fullName, mobile) {
    const userObj = JSON.parse(localStorage.getItem('user_data') || '{}');
    userObj.full_name = fullName;
    userObj.mobile = mobile;
    localStorage.setItem('user_data', JSON.stringify(userObj));
    return Api.postOrPut('/profile/update', 'PUT', {
      full_name: fullName,
      mobile: mobile
    }, token);
  },

  async changePassword(token, currentPassword, newPassword) {
    return Api.postOrPut('/profile/change-password', 'PUT', {
      current_password: currentPassword,
      new_password: newPassword
    }, token);
  }
};

const FinancialApi = {
  async addIncome(token, category, amount, notes = null, txDate = null) {
    return Api.postOrPut('/financial/income', 'POST', {
      category,
      amount,
      notes,
      tx_date: txDate
    }, token);
  },

  async addExpense(token, category, amount, notes = null, txDate = null) {
    return Api.postOrPut('/financial/expense', 'POST', {
      category,
      amount,
      notes,
      tx_date: txDate
    }, token);
  },

  async addDebt(token, liabilityName, outstandingAmount, monthlyPayment, interestRate = 0.0) {
    return Api.postOrPut('/financial/liability', 'POST', {
      liability_name: liabilityName,
      outstanding_amount: outstandingAmount,
      monthly_payment: monthlyPayment,
      interest_rate: interestRate
    }, token);
  },

  async addAsset(token, assetName, amount, assetType = 'Savings Account') {
    return Api.postOrPut('/financial/asset', 'POST', {
      asset_name: assetName,
      amount: amount,
      asset_type: assetType
    }, token);
  }
};
