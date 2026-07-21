const BASE_URL = 'http://localhost:8000';

// Dynamic Local Storage Data Store for GitHub Pages & Offline Mode
const UserStore = {
  getStorageKey() {
    const user = JSON.parse(localStorage.getItem('user_data') || '{}');
    return `finguard_data_${user.email || 'default'}`;
  },

  getData() {
    const key = this.getStorageKey();
    const existing = localStorage.getItem(key);
    if (existing) {
      try { return JSON.parse(existing); } catch (e) {}
    }
    // Default initial 0-data state for NEW users
    return {
      incomes: [],
      expenses: [],
      debts: [],
      assets: []
    };
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
      let score = (expenseRatio * 0.4) + (debtRatio * 0.4);
      if (monthlySurplus < 0) score += 30;
      if (savingsRunway > 3) score -= 15;
      riskScore = Math.min(100, Math.max(0, Math.round(score)));

      if (riskScore < 30) riskLevel = 'Low';
      else if (riskScore < 60) riskLevel = 'Moderate';
      else if (riskScore < 85) riskLevel = 'High';
      else riskLevel = 'Critical';
    }

    const alerts = [];
    if (!hasData) {
      alerts.push('Welcome! Add your income, expenses, or debt to calculate your real-time risk score.');
    } else {
      if (expenseRatio > 40) alerts.push('High Expense Ratio: Spending over 40% of income.');
      if (debtRatio > 35) alerts.push('High Debt Ratio: Over 35% of income goes to debt payments.');
      if (monthlySurplus < 0) alerts.push('Deficit Alert: Monthly expenses exceed total income.');
      if (alerts.length === 0) alerts.push('Your financial status is currently healthy.');
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
      trend_labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      trend_scores: hasData ? [riskScore, riskScore, riskScore, riskScore, riskScore, riskScore] : [0, 0, 0, 0, 0, 0]
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
    return {
      success: true,
      current_risk_score: calc.risk_score,
      current_risk_level: calc.risk_level,
      projections: [
        { days: 30, risk_score: calc.risk_score, risk_level: calc.risk_level, message: 'Projected 30-day outlook based on current activity.', projected_savings: calc.total_assets + calc.monthly_surplus, projected_surplus: calc.monthly_surplus },
        { days: 60, risk_score: calc.risk_score, risk_level: calc.risk_level, message: 'Projected 60-day outlook.', projected_savings: calc.total_assets + (calc.monthly_surplus * 2), projected_surplus: calc.monthly_surplus },
        { days: 90, risk_score: calc.risk_score, risk_level: calc.risk_level, message: 'Projected 90-day outlook.', projected_savings: calc.total_assets + (calc.monthly_surplus * 3), projected_surplus: calc.monthly_surplus }
      ],
      chart_scores: [calc.risk_score, calc.risk_score, calc.risk_score, calc.risk_score],
      recommendations: [
        'Maintain positive monthly surplus to grow your emergency fund.'
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
          'Authorization': `Bearer ${token}`
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
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

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
      console.warn(`[Dynamic Store] Using dynamic client state for ${endpoint}.`);
      if (endpoint === '/auth/login') {
        const userObj = { full_name: body.identifier.split('@')[0] || 'User', email: body.identifier };
        localStorage.setItem('user_data', JSON.stringify(userObj));
        return { success: true, token: 'mock_token', user: userObj };
      }
      if (endpoint === '/financial/income') {
        UserStore.addIncome(body.category, body.amount, body.notes, body.tx_date);
        return { success: true, message: 'Income added successfully' };
      }
      if (endpoint === '/financial/expense') {
        UserStore.addExpense(body.category, body.amount, body.notes, body.tx_date);
        return { success: true, message: 'Expense added successfully' };
      }
      if (endpoint === '/financial/liability') {
        UserStore.addDebt(body.liability_name, body.outstanding_amount, body.monthly_payment, body.interest_rate);
        return { success: true, message: 'Debt added successfully' };
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
  }
};
