# -*- coding: utf-8 -*-
"""
run.py
------
Main entry point for the FinGuard Appium E2E test suite.

Usage:
    python run.py [--mock]

Options:
    --mock   Generate a mock Excel report without connecting to Appium.
             Useful for verifying the report format without a device.

Pre-requisites (for live run):
    1. Install Appium 2.x:
           npm install -g appium
           appium driver install uiautomator2

    2. Start Appium server in a separate terminal:
           appium

    3. Build the Flutter APK:
           flutter build apk --debug

    4. Connect a device / start an emulator and verify:
           adb devices
"""

import os
import io

# Force UTF-8 output on Windows to support Unicode characters in print()
import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import time
import argparse
from datetime import datetime

# ------------------------------------------------------------------
# Ensure this file's directory is on sys.path so imports work
# when the script is called from any working directory.
# ------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from test_suite import FinGuardTestSuite
from excel_reporter import ExcelReporter


# ================================================================
# STEP REGISTRY — defines execution order and skip dependencies
# ================================================================
ALL_STEPS = [
    # 1. Onboarding & Splash (3 TC)
    ("TC_001_LAUNCH", "Verify Splash screen logo and app title"),
    ("TC_002_LAUNCH_BACK", "Verify back button does not exit onboarding"),
    ("TC_003_GET_STARTED", "Verify Get Started button redirects to Login"),
    
    # 2. User Signup Validation & Success (17 TC)
    ("TC_004_SIGNUP_NAV", "Navigate to Sign Up screen from Login"),
    ("TC_005_SIGNUP_EMPTY", "Sign up with all fields empty (error verification)"),
    ("TC_006_SIGNUP_SHORT_PWD", "Sign up with password too short (< 6 chars)"),
    ("TC_007_SIGNUP_PWD_MISMATCH", "Sign up with mismatching password confirmation"),
    ("TC_008_SIGNUP_INVALID_EMAIL", "Sign up with invalid email format (missing @)"),
    ("TC_009_SIGNUP_INVALID_EMAIL_DOMAIN", "Sign up with invalid email domain (missing extension)"),
    ("TC_010_SIGNUP_EMPTY_NAME", "Sign up with name field empty"),
    ("TC_011_SIGNUP_EMPTY_EMAIL", "Sign up with email field empty"),
    ("TC_012_SIGNUP_EMPTY_MOBILE", "Sign up with mobile field empty"),
    ("TC_013_SIGNUP_EMPTY_PASSWORD", "Sign up with password field empty"),
    ("TC_014_SIGNUP_SHORT_MOBILE", "Sign up with invalid mobile number (< 10 digits)"),
    ("TC_015_SIGNUP_SPECIAL_CHAR_NAME", "Sign up with special characters in name"),
    ("TC_016_SIGNUP_NUMERIC_NAME", "Sign up with numeric characters in name"),
    ("TC_017_SIGNUP_LONG_NAME", "Sign up with an extremely long name"),
    ("TC_018_SIGNUP_DUPLICATE_EMAIL", "Sign up with an already registered email"),
    ("TC_019_SIGNUP_BACK_NAV", "Cancel signup and navigate back to Login"),
    ("TC_020_SIGNUP_SUCCESS", "Successfully sign up a new user with valid details"),

    # 3. User Login Validation & Success (15 TC)
    ("TC_021_LOGIN_NAV", "Verify Login page displays correctly"),
    ("TC_022_LOGIN_EMPTY_FIELDS", "Login validation with empty email and password fields"),
    ("TC_023_LOGIN_EMPTY_EMAIL", "Login validation with empty email field"),
    ("TC_024_LOGIN_EMPTY_PASSWORD", "Login validation with empty password field"),
    ("TC_025_LOGIN_WRONG_PASSWORD", "Login validation with unregistered email and password"),
    ("TC_026_LOGIN_WRONG_EMAIL_FORMAT", "Login validation with invalid email format (missing @)"),
    ("TC_027_LOGIN_WRONG_EMAIL_DOMAIN", "Login validation with invalid email domain"),
    ("TC_028_LOGIN_SHORT_PASSWORD", "Login validation with password too short (< 6 chars)"),
    ("TC_029_LOGIN_SQL_INJECTION", "Login validation with SQL injection pattern in email"),
    ("TC_030_LOGIN_SPECIAL_CHARS", "Login validation with special characters in password"),
    ("TC_031_LOGIN_LONG_EMAIL", "Login validation with extremely long email input"),
    ("TC_032_LOGIN_LONG_PASSWORD", "Login validation with extremely long password input"),
    ("TC_033_LOGIN_SPACES_EMAIL", "Login validation with leading/trailing spaces in email"),
    ("TC_034_LOGIN_CASE_INSENSITIVE", "Login validation checking case insensitivity of email"),
    ("TC_035_LOGIN_SUCCESS", "Successfully log in with valid credentials and verify redirect to Dashboard"),

    # 4. Dashboard Metrics & Navigation (10 TC)
    ("TC_036_DASHBOARD_LOAD", "Verify Dashboard screen loads successfully"),
    ("TC_037_DASHBOARD_TITLE", "Verify Dashboard App Bar title and profile icon"),
    ("TC_038_DASHBOARD_CARD_ASSETS", "Verify Assets financial summary card"),
    ("TC_039_DASHBOARD_CARD_LIABILITIES", "Verify Liabilities financial summary card"),
    ("TC_040_DASHBOARD_CARD_RUNWAY", "Verify Runway financial summary card"),
    ("TC_041_DASHBOARD_CARD_EXPENSE_RATIO", "Verify Expense Ratio financial summary card"),
    ("TC_042_DASHBOARD_CARD_DEBT_RATIO", "Verify Debt Ratio financial summary card"),
    ("TC_043_DASHBOARD_CARD_SURPLUS", "Verify Surplus financial summary card"),
    ("TC_044_DASHBOARD_QUICK_ACTIONS", "Verify Quick Actions grid layout"),
    ("TC_045_DASHBOARD_SCROLL", "Verify scrolling behavior on Dashboard screen"),

    # 5. Quick Action Navigation (5 TC)
    ("TC_046_QA_ADD_INCOME_NAV", "Verify Quick Action 'Add Income' tile navigates to Financial Entry Screen"),
    ("TC_047_QA_ADD_EXPENSE_NAV", "Verify Quick Action 'Add Expense' tile navigates to Financial Entry Screen"),
    ("TC_048_QA_ADD_DEBT_NAV", "Verify Quick Action 'Add Debt' tile navigates to Financial Entry Screen"),
    ("TC_049_QA_FORECAST_NAV", "Verify Quick Action 'Forecast' tile navigates to Predictions Screen"),
    ("TC_050_QA_BACK_TO_DASHBOARD", "Verify navigating back to Dashboard from Quick Action screens"),

    # 6. Add Income Records (15 TC)
    ("TC_051_INCOME_FORM_LOAD", "Verify Income form fields are present"),
    ("TC_052_INCOME_SAVE_EMPTY", "Try to save Income with empty fields"),
    ("TC_053_INCOME_SAVE_NO_CATEGORY", "Try to save Income with empty category"),
    ("TC_054_INCOME_SAVE_NO_AMOUNT", "Try to save Income with empty amount"),
    ("TC_055_INCOME_INVALID_AMOUNT", "Try to save Income with alphabetic characters in amount"),
    ("TC_056_INCOME_NEGATIVE_AMOUNT", "Try to save Income with a negative amount"),
    ("TC_057_INCOME_ZERO_AMOUNT", "Try to save Income with zero amount"),
    ("TC_058_INCOME_SPECIAL_CHAR_CATEGORY", "Save Income with special characters in category"),
    ("TC_059_INCOME_LONG_NOTES", "Save Income with extremely long notes text"),
    ("TC_060_INCOME_EMOJI_NOTES", "Save Income with emoji in notes field"),
    ("TC_061_INCOME_SUCCESS_SALARY", "Save valid Salary income record"),
    ("TC_062_INCOME_SUCCESS_BUSINESS", "Save valid Business income record"),
    ("TC_063_INCOME_SUCCESS_INVESTMENT", "Save valid Investment income record"),
    ("TC_064_INCOME_SUCCESS_GIFT", "Save valid Gift income record"),
    ("TC_065_INCOME_SUCCESS_OTHER", "Save valid Other income record"),

    # 7. Add Expense Records (15 TC)
    ("TC_066_EXPENSE_FORM_LOAD", "Verify Expense form tab loads correctly"),
    ("TC_067_EXPENSE_SAVE_EMPTY", "Try to save Expense with empty fields"),
    ("TC_068_EXPENSE_SAVE_NO_CATEGORY", "Try to save Expense with empty category"),
    ("TC_069_EXPENSE_SAVE_NO_AMOUNT", "Try to save Expense with empty amount"),
    ("TC_070_EXPENSE_INVALID_AMOUNT", "Try to save Expense with alphabetic characters in amount"),
    ("TC_071_EXPENSE_NEGATIVE_AMOUNT", "Try to save Expense with a negative amount"),
    ("TC_072_EXPENSE_ZERO_AMOUNT", "Try to save Expense with zero amount"),
    ("TC_073_EXPENSE_SPECIAL_CHAR_CATEGORY", "Save Expense with special characters in category"),
    ("TC_074_EXPENSE_LONG_NOTES", "Save Expense with extremely long notes text"),
    ("TC_075_EXPENSE_EMOJI_NOTES", "Save Expense with emoji in notes field"),
    ("TC_076_EXPENSE_SUCCESS_FOOD", "Save valid Food expense record"),
    ("TC_077_EXPENSE_SUCCESS_RENT", "Save valid Rent expense record"),
    ("TC_078_EXPENSE_SUCCESS_UTILITIES", "Save valid Utilities expense record"),
    ("TC_079_EXPENSE_SUCCESS_ENTERTAINMENT", "Save valid Entertainment expense record"),
    ("TC_080_EXPENSE_SUCCESS_OTHER", "Save valid Other expense record"),

    # 8. Add Debt Records (15 TC)
    ("TC_081_DEBT_FORM_LOAD", "Verify Debt form tab loads correctly"),
    ("TC_082_DEBT_SAVE_EMPTY", "Try to save Debt with empty fields"),
    ("TC_083_DEBT_SAVE_NO_NAME", "Try to save Debt with empty name"),
    ("TC_084_DEBT_SAVE_NO_OUTSTANDING", "Try to save Debt with empty outstanding amount"),
    ("TC_085_DEBT_SAVE_NO_PAYMENT", "Try to save Debt with empty monthly payment"),
    ("TC_086_DEBT_SAVE_NO_INTEREST", "Try to save Debt with empty interest rate"),
    ("TC_087_DEBT_INVALID_OUTSTANDING", "Try to save Debt with alphabetic characters in outstanding"),
    ("TC_088_DEBT_NEGATIVE_OUTSTANDING", "Try to save Debt with a negative outstanding amount"),
    ("TC_089_DEBT_NEGATIVE_PAYMENT", "Try to save Debt with negative monthly payment"),
    ("TC_090_DEBT_NEGATIVE_INTEREST", "Try to save Debt with negative interest rate"),
    ("TC_091_DEBT_ZERO_INTEREST", "Save Debt with 0% interest rate"),
    ("TC_092_DEBT_HIGH_INTEREST", "Save Debt with extremely high interest rate (e.g. 99%)"),
    ("TC_093_DEBT_SPECIAL_CHAR_NAME", "Save Debt with special characters in name"),
    ("TC_094_DEBT_SUCCESS_CC", "Save valid Credit Card debt record"),
    ("TC_095_DEBT_SUCCESS_LOAN", "Save valid Personal Loan debt record"),

    # 9. Risk Analysis Screen Validation (7 TC)
    ("TC_096_RISK_NAV", "Navigate to Risk Analysis via bottom nav"),
    ("TC_097_RISK_TITLE", "Verify Risk Analysis title and layout"),
    ("TC_098_RISK_DISTRESS", "Verify Financial Distress index card"),
    ("TC_099_RISK_DRIVERS", "Verify Risk Drivers section details"),
    ("TC_100_RISK_WHY_SCORE", "Verify 'Why this score' explanation"),
    ("TC_101_RISK_SUGGESTIONS", "Verify Recommendations & Suggestions section"),
    ("TC_102_RISK_SCROLL", "Verify scrolling on Risk Analysis screen"),

    # 10. Predictions & Forecast Screen Validation (6 TC)
    ("TC_103_PRED_NAV", "Navigate to Predictions via bottom nav"),
    ("TC_104_PRED_TITLE", "Verify Predictions screen header"),
    ("TC_105_PRED_CARDS", "Verify 30, 60, 90 days forecast cards"),
    ("TC_106_PRED_CHART", "Verify Trend chart rendering"),
    ("TC_107_PRED_DATA_ACCURACY", "Verify projected values consistency"),
    ("TC_108_PRED_SCROLL", "Verify scrolling on Predictions screen"),

    # 11. Drawer Recommendations (6 TC)
    ("TC_109_DRAWER_OPEN", "Open Navigation Drawer from Dashboard"),
    ("TC_110_DRAWER_ITEMS", "Verify all menu items in Drawer"),
    ("TC_111_DRAWER_REC_NAV", "Navigate to Recommendations from Drawer"),
    ("TC_112_REC_TITLE", "Verify Recommendations screen title"),
    ("TC_113_REC_SECTIONS", "Verify Priority Action Items and Recommendations sections"),
    ("TC_114_REC_BACK", "Navigate back to Dashboard from Recommendations"),

    # 12. Bottom Navigation Traversal & State (3 TC)
    ("TC_115_NAV_TRAVERSAL", "Verify navigating Home -> Risk -> Predictions -> Profile"),
    ("TC_116_NAV_STATE_PRESERVATION", "Verify state is preserved when switching tabs"),
    ("TC_117_PROFILE_LOAD", "Navigate to Profile tab and verify details"),

    # 13. Profile Management & Edit Dialog (5 TC)
    ("TC_118_PROFILE_EDIT_OPEN", "Open Edit Profile dialog"),
    ("TC_119_PROFILE_EDIT_EMPTY", "Try saving profile with empty name"),
    ("TC_120_PROFILE_EDIT_SUCCESS", "Update name successfully and verify change"),
    ("TC_121_PROFILE_EDIT_CANCEL", "Cancel profile edit dialog and verify no change"),
    ("TC_122_LOGOUT_CANCEL", "Click Logout and cancel the operation"),

    # 14. User Logout (1 TC)
    ("TC_123_LOGOUT_SUCCESS", "Perform logout and verify redirection to Login screen"),
]

# Steps that require a logged-in session (skip if login fails)
POST_LOGIN_STEPS = [s for s in ALL_STEPS if s[0] not in (
    "TC_001_LAUNCH", "TC_002_LAUNCH_BACK", "TC_003_GET_STARTED",
    "TC_004_SIGNUP_NAV", "TC_005_SIGNUP_EMPTY", "TC_006_SIGNUP_SHORT_PWD",
    "TC_007_SIGNUP_PWD_MISMATCH", "TC_008_SIGNUP_INVALID_EMAIL",
    "TC_009_SIGNUP_INVALID_EMAIL_DOMAIN", "TC_010_SIGNUP_EMPTY_NAME",
    "TC_011_SIGNUP_EMPTY_EMAIL", "TC_012_SIGNUP_EMPTY_MOBILE",
    "TC_013_SIGNUP_EMPTY_PASSWORD", "TC_014_SIGNUP_SHORT_MOBILE",
    "TC_015_SIGNUP_SPECIAL_CHAR_NAME", "TC_016_SIGNUP_NUMERIC_NAME",
    "TC_017_SIGNUP_LONG_NAME", "TC_018_SIGNUP_DUPLICATE_EMAIL",
    "TC_019_SIGNUP_BACK_NAV", "TC_020_SIGNUP_SUCCESS",
    "TC_021_LOGIN_NAV", "TC_022_LOGIN_EMPTY_FIELDS",
    "TC_023_LOGIN_EMPTY_EMAIL", "TC_024_LOGIN_EMPTY_PASSWORD",
    "TC_025_LOGIN_WRONG_PASSWORD", "TC_026_LOGIN_WRONG_EMAIL_FORMAT",
    "TC_027_LOGIN_WRONG_EMAIL_DOMAIN", "TC_028_LOGIN_SHORT_PASSWORD",
    "TC_029_LOGIN_SQL_INJECTION", "TC_030_LOGIN_SPECIAL_CHARS",
    "TC_031_LOGIN_LONG_EMAIL", "TC_032_LOGIN_LONG_PASSWORD",
    "TC_033_LOGIN_SPACES_EMAIL", "TC_034_LOGIN_CASE_INSENSITIVE",
    "TC_035_LOGIN_SUCCESS",
)]


# ================================================================
# Helpers
# ================================================================
def print_banner(text: str):
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  {text}")
    print(bar)


def check_apk_exists() -> bool:
    apk = config.DESIRED_CAPS.get("app", "")
    return bool(apk) and os.path.exists(apk)


def print_setup_guide():
    print_banner("SETUP GUIDE — PREREQUISITES NOT MET")
    apk = config.DESIRED_CAPS.get("app", "<unknown>")
    guide = f"""
  1. Install Node.js then Appium 2.x:
       > npm install -g appium
       > appium driver install uiautomator2

  2. Start Appium server (in a separate terminal):
       > appium

  3. Build the Flutter debug APK:
       > flutter build apk --debug
       Expected path: {apk}

  4. Connect device / start emulator and verify:
       > adb devices
"""
    print(guide)


# ================================================================
# Live test run
# ================================================================
def run_live():
    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    print_banner("FinGuard Mobile E2E Automation — LIVE RUN")

    # --- APK check ---
    if not check_apk_exists():
        print(f"\n[ERROR] APK not found: {config.DESIRED_CAPS.get('app')}")
        print_setup_guide()
        sys.exit(1)

    start_time = datetime.now()
    driver = None
    suite  = None

    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(config.REPORT_DIR,     exist_ok=True)

    options = UiAutomator2Options().load_capabilities(config.DESIRED_CAPS)

    # --- Connect to Appium ---
    print("\nConnecting to Appium server...")
    for url in [config.APPIUM_LOCAL_URL, config.APPIUM_SERVER_URL]:
        try:
            print(f"  Attempting {url} ...", end=" ")
            driver = webdriver.Remote(url, options=options)
            print("✅  Connected!")
            break
        except Exception as exc:
            print(f"❌  Failed ({exc})")

    if not driver:
        print("\n[ERROR] Could not connect to any Appium server.")
        print_setup_guide()
        sys.exit(1)

    driver.implicitly_wait(config.IMPLICIT_WAIT)
    print("\nAppium session established. Starting test suite...\n")

    try:
        suite = FinGuardTestSuite(driver, screenshot_dir=config.SCREENSHOT_DIR)

        launch_ok = True
        login_ok  = True

        post_login_ids = [s[0] for s in POST_LOGIN_STEPS]

        for tc_id, tc_name in ALL_STEPS:
            # Check skip constraints
            if not launch_ok:
                suite.log_step(tc_id, tc_name, "SKIP", 0.0, error="Launch failed")
                continue
            if tc_id in post_login_ids and not login_ok:
                suite.log_step(tc_id, tc_name, "SKIP", 0.0, error="Login failed")
                continue

            # Run test case via unified dispatcher
            ok = suite.run_step(tc_id, tc_name)

            # Update state variables
            if tc_id == "TC_001_LAUNCH" and not ok:
                launch_ok = False
            if tc_id == "TC_035_LOGIN_SUCCESS" and not ok:
                login_ok = False

    except Exception as exc:
        print(f"\n[FATAL] Unexpected error during test execution: {exc}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("\nClosing Appium session...")
            try:
                driver.quit()
            except Exception:
                pass

    steps_log = suite.steps_log if suite else []
    return steps_log, start_time


# ================================================================
# Mock run (no device needed)
# ================================================================
def run_mock():
    import random
    from datetime import timedelta
    print_banner("FinGuard E2E — MOCK REPORT GENERATION (no device needed)")

    start = datetime.now()
    mock_steps = []
    
    # Predefine a few realistic mock failures to simulate bug scenarios
    MOCK_FAILURES = {
        "TC_010_SIGNUP_EMPTY_NAME": "AssertionError: Validation message 'Name is required' was not displayed on empty form submission.",
        "TC_055_INCOME_INVALID_AMOUNT": "TimeoutException: Save button remained disabled after entering invalid non-numeric amount 'abc'.",
        "TC_088_DEBT_NEGATIVE_OUTSTANDING": "NoSuchElementException: Error tooltip not found for negative outstanding input (-200).",
        "TC_120_PROFILE_EDIT_SUCCESS": "TimeoutException: Profile update PUT API request timed out after 30 seconds wait limit."
    }

    # We will generate mock logs for all 123 test cases.
    for i, s in enumerate(ALL_STEPS):
        # Generate some slight variability in durations to make the charts look interesting
        duration = round(random.uniform(1.2, 4.8), 2)
        if s[0] == "TC_001_LAUNCH":
            duration = round(random.uniform(5.5, 8.2), 2)
        elif s[0] == "TC_035_LOGIN_SUCCESS":
            duration = round(random.uniform(6.0, 9.5), 2)
            
        status = "PASS"
        error = None
        
        if s[0] in MOCK_FAILURES:
            status = "FAIL"
            error = MOCK_FAILURES[s[0]]

        mock_steps.append({
            "id": s[0],
            "name": s[1],
            "status": status,
            "duration": duration,
            "timestamp": start + timedelta(seconds=i * 5),
            "screenshot": None,
            "error": error
        })

    return mock_steps, start


# ================================================================
# Report & summary
# ================================================================
def compile_and_print_report(steps_log, start_time):
    end_time = datetime.now()

    print("\nCompiling Excel report...")
    reporter = ExcelReporter(
        report_dir=config.REPORT_DIR,
        screenshot_dir=config.SCREENSHOT_DIR,
    )
    report_path = reporter.generate_report(steps_log, start_time, end_time)

    passed  = sum(1 for s in steps_log if s["status"] == "PASS")
    failed  = sum(1 for s in steps_log if s["status"] == "FAIL")
    skipped = sum(1 for s in steps_log if s["status"] == "SKIP")
    total   = len(steps_log)
    pct     = (passed / total * 100) if total else 0

    print_banner("TEST RUN COMPLETE")
    print(f"  Start Time   : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  End Time     : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    dur = (end_time - start_time).total_seconds()
    print(f"  Duration     : {int(dur // 60)}m {int(dur % 60)}s")
    print(f"  {'─' * 50}")
    print(f"  Total Steps  : {total}")
    print(f"  ✅ Passed    : {passed}")
    print(f"  ❌ Failed    : {failed}")
    print(f"  ⏭️  Skipped   : {skipped}")
    print(f"  Pass Rate    : {pct:.1f}%")
    print(f"\n  📄 Main Report saved to:\n     {report_path}")
    
    # Automatically categorize and export passed test cases
    try:
        from categorize_report import extract_passed_test_cases, generate_categorized_report
        passed_cases = extract_passed_test_cases(report_path)
        if passed_cases:
            cat_path = generate_categorized_report(passed_cases, report_path, config.REPORT_DIR)
            print(f"  🗂️  Categorized Passed Report saved to:\n     {cat_path}")
    except Exception as e:
        print(f"  ⚠️  Failed to generate categorized report: {e}")
        
    print("=" * 70)
    return report_path


# ================================================================
# Main
# ================================================================
def main():
    parser = argparse.ArgumentParser(
        description="FinGuard Appium E2E test runner"
    )
    parser.add_argument(
        "--mock", action="store_true",
        help="Generate a mock report without a real device/Appium server",
    )
    args = parser.parse_args()

    if args.mock:
        steps_log, start_time = run_mock()
    else:
        steps_log, start_time = run_live()

    compile_and_print_report(steps_log, start_time)


if __name__ == "__main__":
    main()


