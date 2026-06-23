// Global Dashboard State
let currentToken = localStorage.getItem('auth_token');
let currentTab = 'home';
let dashboardData = null;
let riskData = null;
let forecastData = null;
let recommendationsData = null;
let profileData = null;

// Chart Instances
let homeChartInstance = null;
let forecastChartInstance = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  loadCurrentTab();
});

// Sidebar Navigation
function setupNavigation() {
  const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const tabName = item.getAttribute('data-tab');
      switchTab(tabName);
    });
  });
}

function switchTab(tabName) {
  currentTab = tabName;

  // Update navbar title
  const navTitle = document.getElementById('navTitle');
  const titleMap = {
    'home': 'Dashboard',
    'risk': 'Risk Analysis',
    'forecast': 'Predictions',
    'recommendations': 'Recommendations',
    'pipeline': 'CI/CD Pipeline',
    'profile': 'Profile'
  };
  navTitle.textContent = titleMap[tabName] || 'Dashboard';

  // Toggle active nav-item class
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    if (item.getAttribute('data-tab') === tabName) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Toggle active tab-pane
  document.querySelectorAll('.content-container .tab-pane').forEach(pane => {
    if (pane.id === `tab-${tabName}`) {
      pane.classList.add('active');
    } else {
      pane.classList.remove('active');
    }
  });

  loadCurrentTab();
}

// Load Tab Data
async function loadCurrentTab() {
  showLoader(true);
  try {
    if (currentTab === 'home') {
      await fetchHomeData();
    } else if (currentTab === 'risk') {
      await fetchRiskData();
    } else if (currentTab === 'forecast') {
      await fetchForecastData();
    } else if (currentTab === 'recommendations') {
      await fetchRecommendationsData();
    } else if (currentTab === 'pipeline') {
      await initPipelineTab();
    } else if (currentTab === 'profile') {
      await fetchProfileData();
    }
  } catch (err) {
    showToast(err.message || 'Failed to load tab details', 'error');
  } finally {
    showLoader(false);
  }
}

// 1. Home Dashboard API Loader
async function fetchHomeData() {
  dashboardData = await DashboardApi.fetchDashboard(currentToken);
  
  if (!dashboardData.success) {
    throw new Error('Failed to load dashboard data');
  }

  // Populate Risk Score
  const score = dashboardData.risk_score || 0;
  document.getElementById('homeRiskScore').textContent = Math.round(score);
  document.getElementById('homeRiskLevel').textContent = dashboardData.risk_level || 'Low';
  
  // Set risk text description
  const riskDescEl = document.getElementById('homeRiskDesc');
  riskDescEl.textContent = getRiskDescription(dashboardData.risk_level);
  
  // Risk meter circle update
  updateProgressCircle('homeProgressCircle', score, dashboardData.risk_level);

  // Populate Metrics
  document.getElementById('valAssets').textContent = formatCurrency(dashboardData.total_assets);
  document.getElementById('valLiabilities').textContent = formatCurrency(dashboardData.total_liabilities);
  document.getElementById('valRunway').textContent = `${dashboardData.savings_runway || 0} mo`;
  document.getElementById('valExpenseRatio').textContent = `${dashboardData.expense_ratio || 0}%`;
  document.getElementById('valDebtRatio').textContent = `${dashboardData.debt_ratio || 0}%`;
  
  const surplus = dashboardData.monthly_surplus || 0;
  const surplusEl = document.getElementById('valSurplus');
  surplusEl.textContent = formatCurrency(surplus);
  if (surplus < 0) {
    surplusEl.style.color = 'var(--danger)';
  } else {
    surplusEl.style.color = 'var(--success)';
  }

  // Set subRunway and sub ratios colors/notes
  updateMetricSubtitle('subRunway', dashboardData.savings_runway, 'runway');
  updateMetricSubtitle('subExpenseRatio', dashboardData.expense_ratio, 'expense');
  updateMetricSubtitle('subDebtRatio', dashboardData.debt_ratio, 'debt');

  // Populate Line Graph (Chart.js)
  renderHomeChart(dashboardData.trend_labels || [], dashboardData.trend_scores || []);

  // Populate Alerts
  const alertsList = document.getElementById('homeAlertsList');
  alertsList.innerHTML = '';
  
  const alerts = dashboardData.alerts || [];
  if (alerts.length === 0 || (alerts.length === 1 && alerts[0].includes('stable'))) {
    alertsList.innerHTML = `
      <div class="alert-item">
        <div class="alert-icon-box" style="background-color: var(--success-bg); color: var(--success);">
          <i class="fa-regular fa-circle-check"></i>
        </div>
        <div class="alert-details">
          <div class="alert-title">No alerts found</div>
          <div class="alert-subtitle">Your current financial status looks stable.</div>
        </div>
      </div>
    `;
  } else {
    alerts.forEach(alertText => {
      alertsList.innerHTML += `
        <div class="alert-item">
          <div class="alert-icon-box" style="background-color: var(--warning-bg); color: var(--warning);">
            <i class="fa-solid fa-triangle-exclamation"></i>
          </div>
          <div class="alert-details">
            <div class="alert-title">${alertText}</div>
            <div class="alert-subtitle">Generated from your latest financial data.</div>
          </div>
        </div>
      `;
    });
  }
}

// 2. Risk Analysis API Loader
async function fetchRiskData() {
  riskData = await RiskApi.fetchRiskAnalysis(currentToken);

  if (!riskData.success) {
    throw new Error('Failed to load risk analysis');
  }

  // Populate header risk info
  const score = riskData.risk_score || 0;
  document.getElementById('riskRiskScore').textContent = Math.round(score);
  document.getElementById('riskRiskLevel').textContent = riskData.risk_level || 'Low';
  document.getElementById('riskRiskDesc').textContent = getRiskDescription(riskData.risk_level);
  updateProgressCircle('riskProgressCircle', score, riskData.risk_level);

  // Metrics
  document.getElementById('riskExpenseRatio').textContent = `${riskData.expense_ratio || 0}%`;
  document.getElementById('riskDebtRatio').textContent = `${riskData.debt_ratio || 0}%`;
  document.getElementById('riskRunway').textContent = `${riskData.savings_runway || 0} mo`;
  
  const surplus = riskData.monthly_surplus || 0;
  const surplusEl = document.getElementById('riskSurplus');
  surplusEl.textContent = formatCurrency(surplus);
  surplusEl.style.color = surplus < 0 ? 'var(--danger)' : 'var(--success)';

  updateMetricSubtitle('riskSubExpenseRatio', riskData.expense_ratio, 'expense');
  updateMetricSubtitle('riskSubDebtRatio', riskData.debt_ratio, 'debt');
  updateMetricSubtitle('riskSubRunway', riskData.savings_runway, 'runway');

  // Populate Factor Drivers list
  const factorsContainer = document.getElementById('riskFactorsContainer');
  factorsContainer.innerHTML = '';
  const factors = riskData.factors || [];

  if (factors.length === 0) {
    factorsContainer.innerHTML = `
      <div class="factor-card">
        <div class="factor-info">
          <div class="factor-title">No factor details available</div>
          <div class="factor-desc">Add more financial data to get deeper analysis.</div>
        </div>
      </div>
    `;
  } else {
    factors.forEach(factor => {
      const impact = factor.impact || 0;
      const factorColor = getImpactColor(impact);
      factorsContainer.innerHTML += `
        <div class="factor-card">
          <div class="alert-icon-box" style="background-color: ${factorColor}1a; color: ${factorColor}; flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
            <i class="fa-solid fa-chart-line"></i>
          </div>
          <div class="factor-info">
            <div class="factor-title">${factor.title || 'Factor'}</div>
            <div class="factor-desc">${factor.description || ''}</div>
          </div>
          <div class="factor-score" style="color: ${factorColor}; font-weight: 800;">${Math.round(impact)}</div>
        </div>
      `;
    });
  }

  // Suggested Actions list
  const suggestionsContainer = document.getElementById('riskSuggestionsContainer');
  suggestionsContainer.innerHTML = '';
  const suggestions = riskData.suggestions || [];

  if (suggestions.length === 0) {
    suggestionsContainer.innerHTML = `
      <div class="alert-item">
        <div class="alert-icon-box" style="background-color: var(--success-bg); color: var(--success);">
          <i class="fa-regular fa-circle-check"></i>
        </div>
        <div class="alert-details">
          <div class="alert-title">No suggestions available</div>
        </div>
      </div>
    `;
  } else {
    suggestions.forEach(sug => {
      suggestionsContainer.innerHTML += `
        <div class="alert-item">
          <div class="alert-icon-box" style="background-color: var(--success-bg); color: var(--success);">
            <i class="fa-regular fa-circle-check"></i>
          </div>
          <div class="alert-details">
            <div class="alert-title" style="font-weight: 600;">${sug}</div>
          </div>
        </div>
      `;
    });
  }
}

// 3. Predictions (Forecast) API Loader
async function fetchForecastData() {
  forecastData = await ForecastApi.fetchForecast(currentToken);

  if (!forecastData.success) {
    throw new Error('Failed to load forecast data');
  }

  // Populate header risk info
  const score = forecastData.current_risk_score || 0;
  document.getElementById('forecastRiskScore').textContent = Math.round(score);
  document.getElementById('forecastRiskLevel').textContent = forecastData.current_risk_level || 'Low';
  updateProgressCircle('forecastProgressCircle', score, forecastData.current_risk_level);

  // Projections list
  const projectionsContainer = document.getElementById('forecastProjectionsContainer');
  projectionsContainer.innerHTML = '';
  const projections = forecastData.projections || [];

  if (projections.length === 0) {
    projectionsContainer.innerHTML = `
      <div class="alert-item">
        <div class="alert-details">
          <div class="alert-title">No forecast data available</div>
          <div class="alert-subtitle">Add more financial data to generate predictions.</div>
        </div>
      </div>
    `;
  } else {
    projections.forEach(proj => {
      const levelColor = getRiskLevelColor(proj.risk_level);
      const projProgress = (proj.risk_score / 100).toFixed(2);
      
      projectionsContainer.innerHTML += `
        <div class="factor-card" style="align-items: flex-start; padding: 18px;">
          <div class="progress-circle-wrapper" style="width: 74px; height: 74px; flex-shrink: 0; margin-top: 4px;">
            <svg class="progress-svg" style="width: 74px; height: 74px;">
              <circle class="progress-bg-circle" cx="37" cy="37" r="32" style="stroke-width: 6;"></circle>
              <circle class="progress-bar-circle" cx="37" cy="37" r="32" style="stroke-width: 6; stroke: ${levelColor}; stroke-dasharray: 201; stroke-dashoffset: ${201 - (proj.risk_score/100)*201}"></circle>
            </svg>
            <div class="progress-text">
              <span class="progress-val" style="font-size: 18px;">${Math.round(proj.risk_score)}</span>
            </div>
          </div>
          <div class="factor-info" style="margin-left: 8px;">
            <div class="factor-title" style="font-size: 16px;">${proj.days} Days (${proj.risk_level} Risk)</div>
            <div class="factor-desc" style="margin-bottom: 8px; font-size: 13px;">${proj.message || ''}</div>
            <div style="display: flex; gap: 14px; font-size: 13px; font-weight: 600;">
              <span>Projected Savings: <span style="color: var(--primary);">${formatCurrency(proj.projected_savings)}</span></span>
              <span>Projected Cashflow: <span style="color: ${proj.projected_surplus < 0 ? 'var(--danger)' : 'var(--success)'};">${formatCurrency(proj.projected_surplus)}</span></span>
            </div>
          </div>
        </div>
      `;
    });
  }

  // Draw chart graph
  renderForecastChart(forecastData.chart_scores || []);

  // Recommendations actions list
  const recContainer = document.getElementById('forecastRecContainer');
  recContainer.innerHTML = '';
  const recommendations = forecastData.recommendations || [];

  if (recommendations.length === 0) {
    recContainer.innerHTML = `
      <div class="alert-item">
        <div class="alert-icon-box" style="background-color: var(--warning-bg); color: var(--warning);">
          <i class="fa-regular fa-lightbulb"></i>
        </div>
        <div class="alert-details">
          <div class="alert-title">No recommendations available</div>
        </div>
      </div>
    `;
  } else {
    recommendations.forEach(rec => {
      recContainer.innerHTML += `
        <div class="alert-item">
          <div class="alert-icon-box" style="background-color: var(--warning-bg); color: var(--warning);">
            <i class="fa-regular fa-lightbulb"></i>
          </div>
          <div class="alert-details">
            <div class="alert-title" style="font-weight: 600;">${rec}</div>
          </div>
        </div>
      `;
    });
  }
}

// 4. Recommendations API Loader
async function fetchRecommendationsData() {
  recommendationsData = await RecommendationsApi.fetchRecommendations(currentToken);

  if (!recommendationsData.success) {
    throw new Error('Failed to load recommendations');
  }

  // Populate header risk info
  const score = recommendationsData.risk_score || 0;
  document.getElementById('recRiskScore').textContent = Math.round(score);
  document.getElementById('recRiskLevel').textContent = recommendationsData.risk_level || 'Low';
  updateProgressCircle('recProgressCircle', score, recommendationsData.risk_level);

  // Priority actions list
  const priorityContainer = document.getElementById('recPriorityContainer');
  priorityContainer.innerHTML = '';
  const priorities = recommendationsData.priority_actions || [];

  if (priorities.length === 0) {
    priorityContainer.innerHTML = `
      <div class="alert-item">
        <div class="alert-icon-box" style="background-color: var(--success-bg); color: var(--success);">
          <i class="fa-regular fa-circle-check"></i>
        </div>
        <div class="alert-details">
          <div class="alert-title">Maintain your current spending discipline.</div>
        </div>
      </div>
    `;
  } else {
    priorities.forEach(action => {
      priorityContainer.innerHTML += `
        <div class="alert-item">
          <div class="alert-icon-box" style="background-color: var(--warning-bg); color: var(--warning);">
            <i class="fa-solid fa-circle-exclamation"></i>
          </div>
          <div class="alert-details">
            <div class="alert-title" style="font-weight: 600;">${action}</div>
          </div>
        </div>
      `;
    });
  }

  // Detailed Recommendations list
  const detailedContainer = document.getElementById('recDetailedContainer');
  detailedContainer.innerHTML = '';
  const detailed = recommendationsData.recommendations || [];

  if (detailed.length === 0) {
    detailedContainer.innerHTML = `
      <div class="factor-card">
        <div class="factor-info">
          <div class="factor-title">No recommendations available</div>
          <div class="factor-desc">Add more financial data to generate personalized suggestions.</div>
        </div>
      </div>
    `;
  } else {
    detailed.forEach(item => {
      const impact = item.impact || 0;
      const impactColor = getImpactColor(impact);
      
      detailedContainer.innerHTML += `
        <div class="factor-card">
          <div class="alert-icon-box" style="background-color: ${impactColor}1a; color: ${impactColor}; flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
            <i class="fa-regular fa-lightbulb"></i>
          </div>
          <div class="factor-info">
            <div class="factor-title">${item.title || 'Recommendation'}</div>
            <div class="factor-desc">${item.description || ''}</div>
          </div>
          <div class="factor-score" style="color: ${impactColor}; font-weight: 800;">${Math.round(impact)}</div>
        </div>
      `;
    });
  }
}

// 5. Profile API Loader
async function fetchProfileData() {
  profileData = await ProfileApi.fetchProfile(currentToken);

  if (!profileData.success) {
    throw new Error('Failed to load profile details');
  }

  const name = profileData.full_name || '';
  const email = profileData.email || '';
  const mobile = profileData.mobile || '';
  const joinedAt = profileData.joined_at || 'N/A';

  // Fill Avatar initials
  const initials = name.length > 0 ? name[0].toUpperCase() : 'U';
  document.getElementById('profAvatar').textContent = initials;
  document.getElementById('profName').textContent = name;
  document.getElementById('profEmail').textContent = email;

  // Fill Tile Fields
  document.getElementById('tileFullName').textContent = name;
  document.getElementById('tileEmail').textContent = email;
  document.getElementById('tileMobile').textContent = mobile;
  document.getElementById('tileJoined').textContent = joinedAt;

  // Prep the edit form values
  document.getElementById('profEditName').value = name;
  document.getElementById('profEditMobile').value = mobile;
}

// Open Edit Profile modal with preloaded text values
function openProfileEditModal() {
  if (profileData) {
    document.getElementById('profEditName').value = profileData.full_name || '';
    document.getElementById('profEditMobile').value = profileData.mobile || '';
  }
  openModal('modalProfile');
}

// Action Submissions
async function submitExpense(e) {
  e.preventDefault();
  const category = document.getElementById('expCategory').value.trim();
  const amount = parseFloat(document.getElementById('expAmount').value.trim());
  const notes = document.getElementById('expNotes').value.trim() || null;
  const txDate = document.getElementById('expDate').value || null;

  showLoader(true);
  try {
    const res = await FinancialApi.addExpense(currentToken, category, amount, notes, txDate);
    if (res.success) {
      showToast('Expense added successfully!', 'success');
      closeModal('modalExpense');
      document.getElementById('expenseForm').reset();
      await fetchHomeData();
    } else {
      showToast(res.message || 'Failed to add expense', 'error');
    }
  } catch (err) {
    showToast(err.message || 'Failed to add expense', 'error');
  } finally {
    showLoader(false);
  }
}

async function submitIncome(e) {
  e.preventDefault();
  const category = document.getElementById('incCategory').value.trim();
  const amount = parseFloat(document.getElementById('incAmount').value.trim());
  const notes = document.getElementById('incNotes').value.trim() || null;
  const txDate = document.getElementById('incDate').value || null;

  showLoader(true);
  try {
    const res = await FinancialApi.addIncome(currentToken, category, amount, notes, txDate);
    if (res.success) {
      showToast('Income added successfully!', 'success');
      closeModal('modalIncome');
      document.getElementById('incomeForm').reset();
      await fetchHomeData();
    } else {
      showToast(res.message || 'Failed to add income', 'error');
    }
  } catch (err) {
    showToast(err.message || 'Failed to add income', 'error');
  } finally {
    showLoader(false);
  }
}

async function submitDebt(e) {
  e.preventDefault();
  const name = document.getElementById('debtName').value.trim();
  const outstanding = parseFloat(document.getElementById('debtOutstanding').value.trim());
  const payment = parseFloat(document.getElementById('debtPayment').value.trim());
  const interest = parseFloat(document.getElementById('debtInterest').value.trim()) || 0.0;

  showLoader(true);
  try {
    const res = await FinancialApi.addDebt(currentToken, name, outstanding, payment, interest);
    if (res.success) {
      showToast('Debt added successfully!', 'success');
      closeModal('modalDebt');
      document.getElementById('debtForm').reset();
      await fetchHomeData();
    } else {
      showToast(res.message || 'Failed to add debt', 'error');
    }
  } catch (err) {
    showToast(err.message || 'Failed to add debt', 'error');
  } finally {
    showLoader(false);
  }
}

async function submitProfileEdit(e) {
  e.preventDefault();
  const fullName = document.getElementById('profEditName').value.trim();
  const mobile = document.getElementById('profEditMobile').value.trim();

  showLoader(true);
  try {
    const res = await ProfileApi.updateProfile(currentToken, fullName, mobile);
    if (res.success) {
      showToast('Profile updated successfully!', 'success');
      closeModal('modalProfile');
      await fetchProfileData();
    } else {
      showToast('Failed to update profile', 'error');
    }
  } catch (err) {
    showToast(err.message || 'Failed to update profile', 'error');
  } finally {
    showLoader(false);
  }
}

async function submitChangePassword(e) {
  e.preventDefault();
  const currentPass = document.getElementById('passCurrent').value.trim();
  const newPass = document.getElementById('passNew').value.trim();

  showLoader(true);
  try {
    const res = await ProfileApi.changePassword(currentToken, currentPass, newPass);
    if (res.success) {
      showToast('Password updated successfully!', 'success');
      closeModal('modalPassword');
      document.getElementById('passwordForm').reset();
    } else {
      showToast('Failed to change password', 'error');
    }
  } catch (err) {
    showToast(err.message || 'Failed to change password', 'error');
  } finally {
    showLoader(false);
  }
}

// Chart Helpers
function renderHomeChart(labels, data) {
  const ctx = document.getElementById('riskTrendChart').getContext('2d');
  
  if (homeChartInstance) {
    homeChartInstance.destroy();
  }

  homeChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Risk Score',
        data: data,
        borderColor: '#2457f5',
        backgroundColor: 'rgba(36, 87, 245, 0.05)',
        borderWidth: 3,
        pointBackgroundColor: '#2457f5',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.35,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          grid: { color: '#eaeaf1' },
          ticks: { font: { family: 'Outfit', weight: 600 } }
        },
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Outfit', weight: 600 } }
        }
      }
    }
  });
}

function renderForecastChart(data) {
  const ctx = document.getElementById('forecastTrendChart').getContext('2d');

  if (forecastChartInstance) {
    forecastChartInstance.destroy();
  }

  forecastChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Current', '30 Days', '60 Days', '90 Days'],
      datasets: [{
        label: 'Forecasted Risk',
        data: data,
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.05)',
        borderWidth: 3,
        pointBackgroundColor: '#f97316',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          grid: { color: '#eaeaf1' },
          ticks: { font: { family: 'Outfit', weight: 600 } }
        },
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Outfit', weight: 600 } }
        }
      }
    }
  });
}

// Utility functions
function updateProgressCircle(elementId, score, level) {
  const circle = document.getElementById(elementId);
  if (!circle) return;

  // Circumference = 2 * PI * r = 2 * 3.14159 * 45 = 282.74
  const circumference = 282.74;
  const offset = circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference;
  circle.style.strokeDashoffset = offset;
  
  // Update color
  circle.style.stroke = getRiskLevelColor(level);
}

function getRiskLevelColor(level = '') {
  switch (level.toLowerCase()) {
    case 'low':
      return '#16a34a';
    case 'moderate':
      return '#f59e0b';
    case 'high':
      return '#f97316';
    case 'critical':
      return '#ef4444';
    default:
      return '#64748b';
  }
}

function getImpactColor(impact) {
  if (impact < 25) return '#16a34a';
  if (impact < 50) return '#f59e0b';
  if (impact < 75) return '#f97316';
  return '#ef4444';
}

function getRiskDescription(level = '') {
  switch (level.toLowerCase()) {
    case 'low':
      return 'Your financial health looks stable. Keep tracking your savings and spending.';
    case 'moderate':
      return 'Your spending pattern is getting tighter. Reduce expenses and improve savings.';
    case 'high':
      return 'Your finances need attention. Control debt and reduce monthly expenses soon.';
    case 'critical':
      return 'Immediate action is needed. Your financial stress level is very high.';
    default:
      return 'Loading your financial health data...';
  }
}

function formatCurrency(val) {
  const num = parseFloat(val) || 0;
  return `₹${num.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
}

function updateMetricSubtitle(elementId, value, type) {
  const el = document.getElementById(elementId);
  if (!el) return;

  const num = parseFloat(value) || 0;
  if (type === 'runway') {
    if (num < 1.0) {
      el.textContent = 'Very low runway';
      el.style.color = 'var(--danger)';
    } else if (num < 3.0) {
      el.textContent = 'Tight runway';
      el.style.color = 'var(--warning)';
    } else {
      el.textContent = 'Healthy savings runway';
      el.style.color = 'var(--success)';
    }
  } else if (type === 'expense') {
    if (num > 40) {
      el.textContent = 'High spending ratio';
      el.style.color = 'var(--danger)';
    } else {
      el.textContent = 'Stable spending ratio';
      el.style.color = 'var(--success)';
    }
  } else if (type === 'debt') {
    if (num > 35) {
      el.textContent = 'Heavy debt payments';
      el.style.color = 'var(--danger)';
    } else {
      el.textContent = 'Manageable debt load';
      el.style.color = 'var(--success)';
    }
  }
}

// Modal Helpers
function openModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

// Loader Helpers
function showLoader(show) {
  const overlay = document.getElementById('loadingOverlay');
  if (show) {
    overlay.classList.add('active');
  } else {
    overlay.classList.remove('active');
  }
}

// Toast Notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  if (type === 'error') {
    toast.style.backgroundColor = 'var(--danger)';
  } else {
    toast.style.backgroundColor = 'var(--success)';
  }
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.4s ease-out';
    setTimeout(() => {
      container.removeChild(toast);
    }, 400);
  }, 3000);
}

// Logout handler
function handleLogout() {
  localStorage.clear();
  window.location.href = 'login.html';
}

// ==================================================================
// CI/CD PIPELINE DASHBOARD & SIMULATOR LOGIC
// ==================================================================
let pipelineState = {
  isSimulating: false,
  selectedJobId: 'android',
  workflowDuration: 0,
  workflowTimer: null,
  activeLogsInterval: null,
  jobs: {
    android: { id: 'android', name: 'Android App Build & Test', duration: '2m 14s', status: 'success', logs: [] },
    appium: { id: 'appium', name: 'Appium E2E Tests', duration: '15m 5s', status: 'success', logs: [] },
    react: { id: 'react', name: 'React Web App Build & Test', duration: '1m 45s', status: 'success', logs: [] },
    selenium: { id: 'selenium', name: 'Selenium Web Tests', duration: '1m 22s', status: 'success', logs: [] },
    pages: { id: 'pages', name: 'Pages-Build-Development', duration: '48s', status: 'success', logs: [] },
    load: { id: 'load', name: 'Load Tests', duration: '1m 0s', status: 'success', logs: [] },
    staging: { id: 'staging', name: 'Deploy Staging', duration: '30s', status: 'success', logs: [] },
    production: { id: 'production', name: 'Deploy Production', duration: '1m 15s', status: 'success', logs: [] }
  }
};

const precomputedLogs = {
  android: [
    { type: 'cmd', text: '$ flutter test' },
    { type: 'info', text: 'Retrieving flutter dependencies...' },
    { type: 'info', text: 'Running unit and widget tests for FinGuard APK...' },
    { type: 'success', text: '✓ test/auth_test.dart - Sign up validations' },
    { type: 'success', text: '✓ test/dashboard_test.dart - Metric cards load' },
    { type: 'success', text: '✓ test/risk_test.dart - Distress formula bounds' },
    { type: 'success', text: 'All 42 tests passed!' },
    { type: 'cmd', text: '$ flutter build apk --debug' },
    { type: 'info', text: 'Compiling Android application in debug mode...' },
    { type: 'info', text: 'Running Gradle assembleDebug task...' },
    { type: 'success', text: '✓ Built apk successfully (24.8 MB)' },
    { type: 'success', text: 'Output APK: build/app/outputs/flutter-apk/app-debug.apk' }
  ],
  appium: [
    { type: 'cmd', text: '$ pip install -r appium_tests/requirements.txt' },
    { type: 'info', text: 'Installing Appium-Python-Client, pandas, openpyxl...' },
    { type: 'success', text: 'Successfully installed dependencies.' },
    { type: 'cmd', text: '$ python appium_tests/run.py' },
    { type: 'info', text: 'Starting FinGuard Appium Mobile E2E Suite...' },
    { type: 'info', text: 'Connecting to local Appium Server at http://127.0.0.1:4723...' },
    { type: 'success', text: '✓ Appium Session connected successfully!' },
    { type: 'info', text: 'Running 304 automated test cases...' },
    { type: 'info', text: 'TC_001_LAUNCH - Splash Screen Logo: PASS (6.74s)' },
    { type: 'info', text: 'TC_002_LAUNCH_BACK - Prevent Exit: PASS (2.77s)' },
    { type: 'info', text: 'TC_020_SIGNUP_SUCCESS - Valid Signup Flow: PASS (4.39s)' },
    { type: 'info', text: 'TC_035_LOGIN_SUCCESS - Valid Login Redirect: PASS (9.11s)' },
    { type: 'info', text: 'TC_051_INCOME_FORM_LOAD - Form Fields: PASS (1.68s)' },
    { type: 'info', text: 'TC_096_RISK_NAV - Tab Redirection: PASS (3.77s)' },
    { type: 'success', text: '✓ All 304 Appium Mobile E2E tests executed successfully.' },
    { type: 'success', text: 'Generated Excel report: appium_tests/reports/FinGuard_E2E_Report.xlsx' },
    { type: 'success', text: 'Generated Step Summary: appium_tests/reports/appium_e2e_report.md' }
  ],
  react: [
    { type: 'cmd', text: '$ flutter build web' },
    { type: 'info', text: 'Compiling React web application modules...' },
    { type: 'info', text: 'Bundling production assets using standard compilers...' },
    { type: 'success', text: '✓ Web application compiled successfully.' },
    { type: 'success', text: 'Build directory populated at build/web/' }
  ],
  selenium: [
    { type: 'cmd', text: '$ npx http-server website -p 8080 &' },
    { type: 'info', text: 'Starting local static web server...' },
    { type: 'info', text: 'Local web server running at http://localhost:8080' },
    { type: 'cmd', text: '$ npm install && npm test' },
    { type: 'info', text: 'Installing selenium-webdriver, mocha, wait-on...' },
    { type: 'info', text: 'Running Selenium E2E Web Tests in Headless Chrome...' },
    { type: 'info', text: 'FG-TC-001 - Index Logo Display: PASS (0.12s)' },
    { type: 'info', text: 'FG-TC-002 - Get Started Route: PASS (0.23s)' },
    { type: 'info', text: 'FG-TC-004 - Authentication Session: PASS (0.45s)' },
    { type: 'info', text: 'FG-TC-013 - Grid Layout Responsiveness: PASS (0.09s)' },
    { type: 'info', text: 'FG-TC-035 - Latency under 2.0s: PASS (1.45s)' },
    { type: 'info', text: 'FG-TC-068 - Database Handshake: PASS (0.19s)' },
    { type: 'success', text: '✓ 304 Web E2E Test Cases completed successfully.' },
    { type: 'success', text: 'Saved Excel sheet: selenium_tests/reports/finguard_passed_report.xlsx' },
    { type: 'success', text: 'Saved Step Summary: selenium_tests/reports/finguard_selenium_e2e_report.md' }
  ],
  pages: [
    { type: 'cmd', text: '$ upload-pages-artifact website/' },
    { type: 'info', text: 'Uploading static website artifacts to GitHub Pages store...' },
    { type: 'success', text: '✓ Artifact upload complete (3.2 MB)' },
    { type: 'cmd', text: '$ deploy-pages' },
    { type: 'info', text: 'Deploying pages deployment branch...' },
    { type: 'success', text: '✓ Deployment successful! Live URL: https://ArunAdithya7.github.io/FinGaurd_Web' }
  ],
  load: [
    { type: 'cmd', text: '$ python load_tests/load_test.py --mock --duration 60 --users 100' },
    { type: 'info', text: 'Initializing Locust load runner with 100 concurrent mock clients...' },
    { type: 'info', text: 'Target host: https://api.finguard.internal' },
    { type: 'info', text: 'Simulating requests to endpoints: /auth/login, /dashboard/summary, /risk/analysis' },
    { type: 'info', text: 'Time: 15s | Active Users: 100 | RPS: 42.4 | Avg Latency: 120ms' },
    { type: 'info', text: 'Time: 30s | Active Users: 100 | RPS: 58.1 | Avg Latency: 132ms' },
    { type: 'info', text: 'Time: 45s | Active Users: 100 | RPS: 61.2 | Avg Latency: 141ms' },
    { type: 'success', text: '✓ Load tests completed. Total Requests: 3418 | Failed: 0 (0.0% failure rate)' },
    { type: 'success', text: 'Performance benchmark criteria: MET (Avg Latency < 300ms)' }
  ],
  staging: [
    { type: 'info', text: 'Initializing deployment to Staging Environment...' },
    { type: 'cmd', text: '$ aws s3 sync build/ s3://finguard-staging-env/' },
    { type: 'info', text: 'Uploading production assets to staging cloud bucket...' },
    { type: 'info', text: 'Verifying staging service health status at https://staging.finguard.internal/health...' },
    { type: 'success', text: '✓ Health check returned 200 OK.' },
    { type: 'success', text: 'Staging deployment completed successfully.' }
  ],
  production: [
    { type: 'info', text: 'Initiating Production Release Workflow...' },
    { type: 'warning', text: 'Production requires active session validation checks...' },
    { type: 'cmd', text: '$ promote-build --from staging --to production' },
    { type: 'info', text: 'Promoting verified staging build to production bucket...' },
    { type: 'info', text: 'Invalidating CDN cache edge nodes (distribution ID: E1A2B3C4D5E6F)...' },
    { type: 'info', text: 'Checking production deployment health at https://finguard.internal/health...' },
    { type: 'success', text: '✓ Production site is live and healthy.' }
  ]
};

// Initialize Pipeline Tab
async function initPipelineTab() {
  if (pipelineState.isSimulating) {
    // Keep simulation running, just redraw connectors
    renderJobsSidebarList();
    setTimeout(drawPipelineConnections, 100);
    return;
  }

  // Set all jobs to default completed success state initially (realistic final execution view)
  for (const key in pipelineState.jobs) {
    pipelineState.jobs[key].status = 'success';
    pipelineState.jobs[key].logs = [...precomputedLogs[key]];
  }
  
  pipelineState.workflowDuration = 105; // 1m 45s
  updateWorkflowStatsUI('success');

  renderJobsSidebarList();
  selectPipelineJob(pipelineState.selectedJobId);

  // Setup Event Listeners
  const btnRun = document.getElementById('btnRunWorkflow');
  btnRun.onclick = triggerWorkflowSimulation;
  
  const btnClear = document.getElementById('btnClearLogs');
  btnClear.onclick = () => {
    document.getElementById('logsContent').innerHTML = '';
    pipelineState.jobs[pipelineState.selectedJobId].logs = [];
  };

  // Node Card Click Handling
  document.querySelectorAll('.pipeline-node-card').forEach(card => {
    card.onclick = () => {
      const jobId = card.getAttribute('data-job');
      selectPipelineJob(jobId);
    };
  });

  // Wait for layout rendering, then draw connections
  setTimeout(drawPipelineConnections, 100);

  // Redraw lines on window resize
  window.addEventListener('resize', drawPipelineConnections);
}

// Select a job
function selectPipelineJob(jobId) {
  pipelineState.selectedJobId = jobId;

  // Active status in Sidebar List
  document.querySelectorAll('.pipeline-job-item').forEach(item => {
    if (item.getAttribute('data-job') === jobId) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Active status in Graph nodes
  document.querySelectorAll('.pipeline-node-card').forEach(card => {
    if (card.getAttribute('data-job') === jobId) {
      card.classList.add('active');
    } else {
      card.classList.remove('active');
    }
  });

  // Update Logs panel header
  const jobTitle = pipelineState.jobs[jobId].name;
  document.getElementById('currentJobLogTitle').textContent = jobTitle;

  // Update Logs content
  renderJobLogs(jobId);

  // Highlight connections connected to this node
  highlightConnectorLines(jobId);
}

// Highlight lines connected to active job
function highlightConnectorLines(jobId) {
  document.querySelectorAll('.connector-line').forEach(line => {
    const from = line.getAttribute('data-from');
    const to = line.getAttribute('data-to');
    if (from === jobId || to === jobId) {
      line.classList.add('active');
      line.style.strokeWidth = '3px';
    } else {
      line.classList.remove('active');
      line.style.strokeWidth = '2px';
    }
  });
}

// Render Job Logs in console
function renderJobLogs(jobId) {
  const container = document.getElementById('logsContent');
  container.innerHTML = '';
  
  const logs = pipelineState.jobs[jobId].logs || [];
  if (logs.length === 0) {
    container.innerHTML = '<span class="log-line-info">No logs recorded. Run the workflow to see execution outputs.</span>';
    return;
  }

  logs.forEach(line => {
    const timeStr = new Date().toLocaleTimeString();
    let classStyle = 'log-line-info';
    if (line.type === 'cmd') classStyle = 'log-line-cmd';
    else if (line.type === 'success') classStyle = 'log-line-success';
    else if (line.type === 'error') classStyle = 'log-line-error';
    else if (line.type === 'warning') classStyle = 'log-line-warning';

    container.innerHTML += `<div class="${classStyle}"><span style="color: #8b949e; font-size: 11px;">[${timeStr}]</span> ${line.text}</div>`;
  });
  
  // Auto-scroll logs
  container.scrollTop = container.scrollHeight;
}

// Render Sidebar jobs list
function renderJobsSidebarList() {
  const list = document.getElementById('pipelineJobsList');
  list.innerHTML = '';

  for (const key in pipelineState.jobs) {
    const job = pipelineState.jobs[key];
    const statusIcon = getJobStatusIcon(job.status);
    const activeClass = job.id === pipelineState.selectedJobId ? 'active' : '';
    
    list.innerHTML += `
      <div class="pipeline-job-item ${activeClass}" data-job="${job.id}" onclick="selectPipelineJob('${job.id}')">
        <div class="job-item-info">
          <span class="job-item-status-icon status-${job.status}">${statusIcon}</span>
          <span class="job-item-name">${job.name}</span>
        </div>
        <span class="job-item-time">${job.status === 'queued' ? 'queued' : (job.status === 'running' ? 'running...' : job.duration)}</span>
      </div>
    `;
  }
}

// Get status icon html
function getJobStatusIcon(status) {
  switch (status) {
    case 'success':
      return '<i class="fa-solid fa-circle-check" style="color: #1a7f37;"></i>';
    case 'failed':
      return '<i class="fa-solid fa-circle-xmark" style="color: #cf222e;"></i>';
    case 'running':
      return '<i class="fa-solid fa-circle-notch fa-spin" style="color: #0969da;"></i>';
    case 'queued':
    default:
      return '<i class="fa-regular fa-circle" style="color: #8c959f;"></i>';
  }
}

// Update general workflow summary metadata UI
function updateWorkflowStatsUI(status) {
  const badge = document.getElementById('workflowStatusBadge');
  badge.className = `workflow-status-badge status-${status}`;
  
  if (status === 'success') {
    badge.innerHTML = '<i class="fa-solid fa-circle-check"></i> Success';
  } else if (status === 'running') {
    badge.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Running';
  } else {
    badge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Failed';
  }

  // Format Duration text
  const m = Math.floor(pipelineState.workflowDuration / 60);
  const s = pipelineState.workflowDuration % 60;
  const durationText = m > 0 ? `${m}m ${s}s` : `${s}s`;
  document.getElementById('workflowDurationText').textContent = durationText;

  // Generate random commit hash
  if (status === 'running') {
    const chars = '0123456789abcdef';
    let newHash = '';
    for (let i = 0; i < 7; i++) newHash += chars[Math.floor(Math.random() * 16)];
    document.getElementById('workflowCommitHash').textContent = newHash;
  }
}

// Draw connection lines on SVG overlay
function drawPipelineConnections() {
  const overlay = document.getElementById('pipelineSvgOverlay');
  const viewport = document.getElementById('pipelineViewport');
  if (!overlay || !viewport) return;

  // Clear existing lines
  overlay.innerHTML = '';

  // Get viewport bounding box
  const viewRect = viewport.getBoundingClientRect();

  // Define connection paths
  const connections = [
    { from: 'android', to: 'appium' },
    { from: 'appium', to: 'load' },
    { from: 'react', to: 'selenium' },
    { from: 'selenium', to: 'load' },
    { from: 'pages', to: 'load' },
    { from: 'load', to: 'staging' },
    { from: 'staging', to: 'production' }
  ];

  // Draw curves
  connections.forEach(conn => {
    const fromNode = document.getElementById(`node-${conn.from}`);
    const toNode = document.getElementById(`node-${conn.to}`);
    if (!fromNode || !toNode) return;

    const fromRect = fromNode.getBoundingClientRect();
    const toRect = toNode.getBoundingClientRect();

    // Coordinates relative to overlay
    const startX = fromRect.right - viewRect.left + viewport.scrollLeft;
    const startY = fromRect.top + fromRect.height / 2 - viewRect.top + viewport.scrollTop;
    const endX = toRect.left - viewRect.left + viewport.scrollLeft;
    const endY = toRect.top + toRect.height / 2 - viewRect.top + viewport.scrollTop;

    // S-curve Bezier control points
    const deltaX = endX - startX;
    const cp1X = startX + deltaX / 2;
    const cp1Y = startY;
    const cp2X = startX + deltaX / 2;
    const cp2Y = endY;

    // Determine path state color
    let lineClass = 'connector-line';
    const fromStatus = pipelineState.jobs[conn.from].status;
    const toStatus = pipelineState.jobs[conn.to].status;
    
    if (fromStatus === 'success' && toStatus === 'success') {
      lineClass += ' completed';
    } else if (fromStatus === 'success' && toStatus === 'running') {
      lineClass += ' active';
    }

    // Append SVG path
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M ${startX} ${startY} C ${cp1X} ${cp1Y}, ${cp2X} ${cp2Y}, ${endX} ${endY}`);
    path.setAttribute('class', lineClass);
    path.setAttribute('data-from', conn.from);
    path.setAttribute('data-to', conn.to);
    overlay.appendChild(path);
  });
}

// Trigger Interactive Workflow Simulation
function triggerWorkflowSimulation() {
  if (pipelineState.isSimulating) return;

  pipelineState.isSimulating = true;
  document.getElementById('btnRunWorkflow').disabled = true;

  // Set initial status queued
  for (const key in pipelineState.jobs) {
    pipelineState.jobs[key].status = 'queued';
    pipelineState.jobs[key].logs = [];
    updateNodeUI(key, 'queued');
  }

  pipelineState.workflowDuration = 0;
  updateWorkflowStatsUI('running');
  renderJobsSidebarList();
  renderJobLogs(pipelineState.selectedJobId);
  drawPipelineConnections();

  // Start duration timer
  pipelineState.workflowTimer = setInterval(() => {
    pipelineState.workflowDuration++;
    updateWorkflowStatsUI('running');
  }, 1000);

  // Workflow Stages Simulation Queue
  // We model steps sequentially and parallelly
  let step = 0;
  
  // Simulation timelines
  const runNextSimulationStep = () => {
    if (!pipelineState.isSimulating) return;

    if (step === 0) {
      // Parallel Build: Android, React Web, Pages
      startJobExecution('android', 4000, () => {
        // Android finished -> Appium starts
        startJobExecution('appium', 6000, checkMiddleStageComplete);
      });
      
      startJobExecution('react', 3000, () => {
        // React finished -> Selenium starts
        startJobExecution('selenium', 5000, checkMiddleStageComplete);
      });
      
      startJobExecution('pages', 5000, checkMiddleStageComplete);
      
      step = 1;
    }
  };

  const checkMiddleStageComplete = () => {
    // Check if appium, selenium, and pages are all completed successfully
    const appiumDone = pipelineState.jobs.appium.status === 'success';
    const seleniumDone = pipelineState.jobs.selenium.status === 'success';
    const pagesDone = pipelineState.jobs.pages.status === 'success';

    if (appiumDone && seleniumDone && pagesDone && step === 1) {
      // Move to Load testing
      step = 2;
      startJobExecution('load', 4000, () => {
        // Load testing done -> Deploy Staging
        step = 3;
        startJobExecution('staging', 3000, () => {
          // Staging done -> Deploy Production
          step = 4;
          startJobExecution('production', 4000, () => {
            // All complete!
            clearInterval(pipelineState.workflowTimer);
            pipelineState.isSimulating = false;
            document.getElementById('btnRunWorkflow').disabled = false;
            updateWorkflowStatsUI('success');
            showToast('CI/CD Pipeline workflow execution completed successfully!', 'success');
          });
        });
      });
    }
  };

  // Run initial step
  runNextSimulationStep();
}

// Start simulation on a single job
function startJobExecution(jobId, durationMs, onComplete) {
  pipelineState.jobs[jobId].status = 'running';
  updateNodeUI(jobId, 'running');
  renderJobsSidebarList();
  drawPipelineConnections();

  if (pipelineState.selectedJobId === jobId) {
    selectPipelineJob(jobId);
  }

  // Simulate log outputs typing line-by-line
  const logLines = precomputedLogs[jobId];
  let currentLineIndex = 0;
  
  const intervalTime = Math.floor(durationMs / (logLines.length + 1));
  const logInterval = setInterval(() => {
    if (!pipelineState.isSimulating) {
      clearInterval(logInterval);
      return;
    }

    if (currentLineIndex < logLines.length) {
      pipelineState.jobs[jobId].logs.push(logLines[currentLineIndex]);
      currentLineIndex++;
      
      if (pipelineState.selectedJobId === jobId) {
        renderJobLogs(jobId);
      }
    } else {
      clearInterval(logInterval);
    }
  }, intervalTime);

  // Complete job callback
  setTimeout(() => {
    if (!pipelineState.isSimulating) return;

    pipelineState.jobs[jobId].status = 'success';
    updateNodeUI(jobId, 'success');
    renderJobsSidebarList();
    drawPipelineConnections();
    
    if (pipelineState.selectedJobId === jobId) {
      selectPipelineJob(jobId);
    }

    onComplete();
  }, durationMs);
}

// Update classes and icons on graph node elements
function updateNodeUI(jobId, status) {
  const node = document.getElementById(`node-${jobId}`);
  if (!node) return;

  node.className = `pipeline-node-card status-${status}`;
  if (jobId === pipelineState.selectedJobId) {
    node.classList.add('active');
  }

  const iconContainer = node.querySelector('.node-status-icon');
  
  let iconHtml = '';
  if (status === 'success') {
    iconHtml = '<i class="fa-solid fa-circle-check"></i>';
  } else if (status === 'failed') {
    iconHtml = '<i class="fa-solid fa-circle-xmark"></i>';
  } else if (status === 'running') {
    iconHtml = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
  } else {
    iconHtml = '<i class="fa-regular fa-circle"></i>';
  }
  
  iconContainer.innerHTML = iconHtml;
}
