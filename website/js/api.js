const BASE_URL = 'http://localhost:8000';

const Api = {
  // Helper for GET requests with Bearer Token
  async get(endpoint, token) {
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
  },

  // Helper for POST/PUT requests with Bearer Token
  async postOrPut(endpoint, method, body, token = null) {
    const headers = {
      'Content-Type': 'application/json'
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

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
  }
};

const AuthService = {
  async login(identifier, password) {
    return Api.postOrPut('/auth/login', 'POST', { identifier, password });
  },

  async signup(fullName, email, mobile, password) {
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
