import os

# ============================================================
#  FinGuard Appium E2E Configuration
# ============================================================

# Appium Server URLs
APPIUM_LOCAL_URL = "http://127.0.0.1:4723"
APPIUM_SERVER_URL = "http://10.0.2.2:4723"  # For connections from inside emulator

# ----------------------------------------------------------------
# APK path  (auto-resolved relative to this file)
# ----------------------------------------------------------------
_APK_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "build",
        "app",
        "outputs",
        "flutter-apk",
        "app-debug.apk",
    )
)

# ----------------------------------------------------------------
# Android UiAutomator2 Desired Capabilities
# ----------------------------------------------------------------
DESIRED_CAPS = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "Android Emulator",
    "app": _APK_PATH,
    "appPackage": "com.example.finguard",
    "appActivity": ".MainActivity",
    # --- Reset strategy ---
    "noReset": False,           # Always install fresh APK
    "fullReset": False,
    # --- Permissions & stability ---
    "autoGrantPermissions": True,
    "newCommandTimeout": 300,
    "adbExecTimeout": 60000,
    "androidInstallTimeout": 120000,
    # --- Flutter / Dart specific ---
    "ensureWebviewsHavePages": True,
    "nativeWebScreenshot": True,
}

# ----------------------------------------------------------------
# Wait Timeouts  (seconds)
# ----------------------------------------------------------------
IMPLICIT_WAIT    = 10
EXPLICIT_WAIT    = 20
LONG_WAIT        = 30   # For slow network responses (API calls)
ANIMATION_SLEEP  = 1.5  # Short pause after UI animations
API_SLEEP        = 3.0  # After mutating API calls (save/submit)

# ----------------------------------------------------------------
# Test Credentials
# ----------------------------------------------------------------
TEST_USER = {
    "full_name":     "Test Appium User",
    "email":         "appiumtest@finguard.com",
    "mobile":        "9876543210",
    "password":      "Password123!",
    "new_password":  "NewPassword123!",
    # Revert password to original after the change test so re-runs work
    "revert_password": True,
}

# ----------------------------------------------------------------
# Test Data for Financial Entries
# ----------------------------------------------------------------
INCOME_DATA = {
    "category": "Salary",
    "amount":   "75000",
    "notes":    "Primary employment income",
}

EXPENSE_DATA = {
    "category": "Rent",
    "amount":   "22000",
    "notes":    "Monthly apartment rent",
}

DEBT_DATA = {
    "name":        "Home Loan",
    "outstanding": "500000",
    "payment":     "18000",
    "interest":    "8.5",
}

# ----------------------------------------------------------------
# Report / Screenshot directories (relative to this file)
# ----------------------------------------------------------------
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")
REPORT_DIR     = os.path.join(BASE_DIR, "reports")
