# FinGuard — Appium E2E Test Suite

End-to-end mobile automation for the **FinGuard** Flutter Android application using Appium 2.x + Python.

---

## 📁 Folder Structure

```
appium_tests/
├── config.py           ← Appium capabilities, timeouts, test data
├── locators.py         ← All UI element locators (9 screens)
├── test_suite.py       ← 16 test case implementations
├── run.py              ← Main runner (live + mock modes)
├── excel_reporter.py   ← 3-sheet Excel report generator
├── requirements.txt    ← Python dependencies
├── screenshots/        ← Auto-created; stores PNG screenshots per step
└── reports/            ← Auto-created; stores timestamped .xlsx reports
```

---

## ⚡ Quick Start

### 1. Install Python dependencies
```bash
cd appium_tests
pip install -r requirements.txt
```

### 2. Install Appium 2.x
```bash
npm install -g appium
appium driver install uiautomator2
```

### 3. Start Appium server
```bash
appium
```

### 4. Build Flutter APK
```bash
# From the project root (finguard/)
flutter build apk --debug
```

### 5. Connect a device or start an Android Emulator
```bash
adb devices    # Should list your device/emulator
```

### 6. Run the tests
```bash
cd appium_tests
python run.py
```

### 7. Generate a mock report (no device needed)
```bash
python run.py --mock
```

---

## 🧪 Test Cases (16 total)

| #  | ID                        | Description                                              |
|----|---------------------------|----------------------------------------------------------|
| 1  | TC_001_LAUNCH             | Verify Launch & Splash / Get Started screen              |
| 2  | TC_002_SIGNUP             | Sign up a new user account                               |
| 3  | TC_003_LOGIN_INVALID_CREDS| Login validation — wrong credentials                     |
| 4  | TC_004_LOGIN_EMPTY_FIELDS | Login validation — empty email & password fields         |
| 5  | TC_005_LOGIN_SUCCESS      | Login with valid credentials and reach Dashboard         |
| 6  | TC_006_DASHBOARD_CARDS    | Verify all financial summary cards on Dashboard          |
| 7  | TC_007_QUICK_ACTIONS      | Verify quick action tiles are present on Dashboard       |
| 8  | TC_008_ADD_INCOME         | Add a monthly income record (category, amount, notes)    |
| 9  | TC_009_ADD_EXPENSE        | Add a monthly expense record (category, amount, notes)   |
| 10 | TC_010_ADD_DEBT           | Add a debt record (name, outstanding, payment, interest) |
| 11 | TC_011_RISK_ANALYSIS      | Verify Risk Analysis screen sections & metric cards      |
| 12 | TC_012_PREDICTIONS        | Verify Predictions/Forecast screen & 30/60/90-day cards  |
| 13 | TC_013_RECOMMENDATIONS    | Open Recommendations via Drawer and verify sections      |
| 14 | TC_014_NAVIGATION         | Traverse all bottom navigation tabs (Home→Risk→...)      |
| 15 | TC_015_EDIT_PROFILE       | Open Edit Profile dialog and update name                 |
| 16 | TC_016_LOGOUT             | Logout from Profile and verify return to Login           |

---

## 📊 Excel Report

Each run generates a timestamped `.xlsx` file in `reports/` with **3 sheets**:

| Sheet             | Contents                                                              |
|-------------------|-----------------------------------------------------------------------|
| **Dashboard**     | Navy banner, execution metadata, statistics, mini result table        |
| **Detailed Logs** | Full step log with PASS/FAIL colouring, screenshot links, error text  |
| **Analysis & Charts** | Bar chart (result distribution) + horizontal bar chart (durations) |

---

## ⚙️ Configuration (`config.py`)

| Key              | Default                        | Description                        |
|------------------|--------------------------------|------------------------------------|
| `APPIUM_LOCAL_URL`| `http://127.0.0.1:4723`       | Appium server URL                  |
| `IMPLICIT_WAIT`  | `10`                           | Implicit wait (seconds)            |
| `EXPLICIT_WAIT`  | `20`                           | Explicit wait per element (seconds)|
| `LONG_WAIT`      | `30`                           | Wait for slow API responses        |
| `TEST_USER`      | `appiumtest@finguard.com`      | Credentials used for sign-up/login |
| `INCOME_DATA`    | Salary / 75000                 | Test income record data            |
| `EXPENSE_DATA`   | Rent / 22000                   | Test expense record data           |
| `DEBT_DATA`      | Home Loan / 500000             | Test debt record data              |

---

## 📌 Notes

- Tests run in sequential order with **smart skip logic**: if TC_001 (Launch) fails, all remaining steps are marked as `SKIP`. If TC_005 (Login) fails, all post-login steps are skipped.
- Screenshots are captured on **both PASS and FAIL**, named `{TC_ID}_{HHMMSS}.png`.
- The test user email (`appiumtest@finguard.com`) is used consistently across runs; the app's `noReset: false` ensures a clean install each time.
