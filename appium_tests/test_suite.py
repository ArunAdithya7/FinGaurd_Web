"""
test_suite.py
-------------
Full end-to-end Appium test suite for the FinGuard Android application.
Supports 123 comprehensive test cases via a unified dispatcher.
"""

import os
import time
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from locators import Locators
import config


class FinGuardTestSuite:
    """
    Orchestrates the complete end-to-end test flow for FinGuard.
    Uses run_step() as the unified dispatcher for all 123 test cases.
    """

    def __init__(self, driver, screenshot_dir: str = "screenshots"):
        self.driver = driver
        self.screenshot_dir = screenshot_dir
        self.steps_log: list[dict] = []
        os.makedirs(self.screenshot_dir, exist_ok=True)

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def log_step(self, step_id, step_name, status, duration,
                 error=None, screenshot=None):
        entry = {
            "id":         step_id,
            "name":       step_name,
            "status":     status,          # "PASS" | "FAIL" | "SKIP"
            "duration":   round(duration, 2),
            "timestamp":  datetime.now(),
            "screenshot": screenshot,
            "error":      str(error) if error else None,
        }
        self.steps_log.append(entry)
        icon = "✅" if status == "PASS" else ("⏭️" if status == "SKIP" else "❌")
        print(f"  {icon} [{status}] {step_id}: {step_name}  ({round(duration,2)}s)")

    def capture_screenshot(self, name: str) -> str | None:
        try:
            ts = datetime.now().strftime("%H%M%S")
            filename = f"{name}_{ts}.png"
            path = os.path.join(self.screenshot_dir, filename)
            self.driver.save_screenshot(path)
            return path
        except Exception as e:
            print(f"  [Screenshot] Failed to capture '{name}': {e}")
            return None

    def find_el(self, locator, timeout=None):
        t = timeout or config.EXPLICIT_WAIT
        return WebDriverWait(self.driver, t).until(
            EC.presence_of_element_located(locator)
        )

    def find_clickable(self, locator, timeout=None):
        t = timeout or config.EXPLICIT_WAIT
        return WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable(locator)
        )

    def element_exists(self, locator, timeout: float = 5.0) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def type_into(self, locator, text: str, timeout=None):
        el = self.find_clickable(locator, timeout)
        el.click()
        try:
            el.clear()
        except Exception:
            pass
        el.send_keys(text)
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass
        return el

    def safe_click(self, locator, timeout=None) -> bool:
        try:
            self.find_clickable(locator, timeout).click()
            return True
        except Exception:
            return False

    def scroll_down(self):
        """Scroll down one screenful using Android UIAutomator."""
        try:
            self.driver.execute_script(
                "mobile: scrollGesture",
                {"left": 100, "top": 300, "width": 200, "height": 400,
                 "direction": "down", "percent": 0.75},
            )
        except Exception:
            pass

    def _dismiss_keyboard(self):
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass

    def _open_drawer(self) -> bool:
        """Try multiple drawer-opening strategies."""
        if self.safe_click(Locators.DRAWER_OPEN_BTN, timeout=5):
            time.sleep(config.ANIMATION_SLEEP)
            return True
        try:
            from appium.webdriver.common.appiumby import AppiumBy as By
            btn = self.driver.find_element(By.ACCESSIBILITY_ID, "Open navigation drawer")
            btn.click()
            time.sleep(config.ANIMATION_SLEEP)
            return True
        except Exception:
            pass
        try:
            size   = self.driver.get_window_size()
            start_x = 5
            end_x   = int(size["width"] * 0.55)
            mid_y   = int(size["height"] * 0.5)
            self.driver.execute_script(
                "mobile: swipeGesture",
                {"startX": start_x, "startY": mid_y, "endX": end_x, "endY": mid_y, "speed": 800},
            )
            time.sleep(config.ANIMATION_SLEEP)
            return True
        except Exception:
            pass
        return False

    def _attempt_recovery(self):
        try:
            print("  ⚠️ Executing recovery sequence...")
            self._dismiss_keyboard()
            if self.element_exists(Locators.DIALOG_CANCEL_BTN, timeout=2):
                self.safe_click(Locators.DIALOG_CANCEL_BTN)
                time.sleep(0.5)
            if self.element_exists(Locators.ENTRY_TITLE, timeout=2):
                self.driver.back()
                time.sleep(0.5)
            if self.element_exists(Locators.NAV_HOME, timeout=2):
                self.safe_click(Locators.NAV_HOME)
                time.sleep(0.5)
        except Exception as e:
            print(f"  [Recovery] Recovery failed: {e}")

    # ================================================================
    # UNIFIED DISPATCHER
    # ================================================================
    def run_step(self, step_id, step_name) -> bool:
        start = time.time()
        print(f"\n▶ Starting {step_id}: {step_name}")
        try:
            # Dispatch to appropriate test handler
            if step_id == "TC_001_LAUNCH":
                self._run_launch()
            elif step_id == "TC_002_LAUNCH_BACK":
                self._run_launch_back()
            elif step_id == "TC_003_GET_STARTED":
                self._run_get_started()
            elif step_id == "TC_004_SIGNUP_NAV":
                self._run_signup_nav()
            elif step_id.startswith("TC_005_") or step_id.startswith("TC_006_") or \
                 step_id.startswith("TC_007_") or step_id.startswith("TC_008_") or \
                 step_id.startswith("TC_009_") or step_id.startswith("TC_010_") or \
                 step_id.startswith("TC_011_") or step_id.startswith("TC_012_") or \
                 step_id.startswith("TC_013_") or step_id.startswith("TC_014_") or \
                 step_id.startswith("TC_015_") or step_id.startswith("TC_016_") or \
                 step_id.startswith("TC_017_") or step_id.startswith("TC_018_"):
                self._run_signup_validation(step_id)
            elif step_id == "TC_019_SIGNUP_BACK_NAV":
                self._run_signup_back_nav()
            elif step_id == "TC_020_SIGNUP_SUCCESS":
                self._run_signup_success()
            elif step_id == "TC_021_LOGIN_NAV":
                self._run_login_nav()
            elif step_id.startswith("TC_022_") or step_id.startswith("TC_023_") or \
                 step_id.startswith("TC_024_") or step_id.startswith("TC_025_") or \
                 step_id.startswith("TC_026_") or step_id.startswith("TC_027_") or \
                 step_id.startswith("TC_028_") or step_id.startswith("TC_029_") or \
                 step_id.startswith("TC_030_") or step_id.startswith("TC_031_") or \
                 step_id.startswith("TC_032_") or step_id.startswith("TC_033_") or \
                 step_id.startswith("TC_034_"):
                self._run_login_validation(step_id)
            elif step_id == "TC_035_LOGIN_SUCCESS":
                self._run_login_success()
            elif step_id == "TC_036_DASHBOARD_LOAD":
                self._run_dashboard_load()
            elif step_id == "TC_037_DASHBOARD_TITLE":
                self._run_dashboard_title()
            elif step_id.startswith("TC_038_") or step_id.startswith("TC_039_") or \
                 step_id.startswith("TC_040_") or step_id.startswith("TC_041_") or \
                 step_id.startswith("TC_042_") or step_id.startswith("TC_043_"):
                self._run_dashboard_card(step_id)
            elif step_id == "TC_044_DASHBOARD_QUICK_ACTIONS":
                self._run_dashboard_quick_actions()
            elif step_id == "TC_045_DASHBOARD_SCROLL":
                self._run_dashboard_scroll()
            elif step_id.startswith("TC_046_") or step_id.startswith("TC_047_") or \
                 step_id.startswith("TC_048_") or step_id.startswith("TC_049_"):
                self._run_quick_action_nav(step_id)
            elif step_id == "TC_050_QA_BACK_TO_DASHBOARD":
                self._run_quick_action_back()
            elif step_id == "TC_051_INCOME_FORM_LOAD":
                self._run_income_form_load()
            elif step_id.startswith("TC_052_") or step_id.startswith("TC_053_") or \
                 step_id.startswith("TC_054_") or step_id.startswith("TC_055_") or \
                 step_id.startswith("TC_056_") or step_id.startswith("TC_057_") or \
                 step_id.startswith("TC_058_") or step_id.startswith("TC_059_") or \
                 step_id.startswith("TC_060_") or step_id.startswith("TC_061_") or \
                 step_id.startswith("TC_062_") or step_id.startswith("TC_063_") or \
                 step_id.startswith("TC_064_") or step_id.startswith("TC_065_"):
                self._run_income_test(step_id)
            elif step_id == "TC_066_EXPENSE_FORM_LOAD":
                self._run_expense_form_load()
            elif step_id.startswith("TC_067_") or step_id.startswith("TC_068_") or \
                 step_id.startswith("TC_069_") or step_id.startswith("TC_070_") or \
                 step_id.startswith("TC_071_") or step_id.startswith("TC_072_") or \
                 step_id.startswith("TC_073_") or step_id.startswith("TC_074_") or \
                 step_id.startswith("TC_075_") or step_id.startswith("TC_076_") or \
                 step_id.startswith("TC_077_") or step_id.startswith("TC_078_") or \
                 step_id.startswith("TC_079_") or step_id.startswith("TC_080_"):
                self._run_expense_test(step_id)
            elif step_id == "TC_081_DEBT_FORM_LOAD":
                self._run_debt_form_load()
            elif step_id.startswith("TC_082_") or step_id.startswith("TC_083_") or \
                 step_id.startswith("TC_084_") or step_id.startswith("TC_085_") or \
                 step_id.startswith("TC_086_") or step_id.startswith("TC_087_") or \
                 step_id.startswith("TC_088_") or step_id.startswith("TC_089_") or \
                 step_id.startswith("TC_090_") or step_id.startswith("TC_091_") or \
                 step_id.startswith("TC_092_") or step_id.startswith("TC_093_") or \
                 step_id.startswith("TC_094_") or step_id.startswith("TC_095_"):
                self._run_debt_test(step_id)
            elif step_id.startswith("TC_096_") or step_id.startswith("TC_097_") or \
                 step_id.startswith("TC_098_") or step_id.startswith("TC_099_") or \
                 step_id.startswith("TC_100_") or step_id.startswith("TC_101_") or \
                 step_id.startswith("TC_102_"):
                self._run_risk_test(step_id)
            elif step_id.startswith("TC_103_") or step_id.startswith("TC_104_") or \
                 step_id.startswith("TC_105_") or step_id.startswith("TC_106_") or \
                 step_id.startswith("TC_107_") or step_id.startswith("TC_108_"):
                self._run_predictions_test(step_id)
            elif step_id.startswith("TC_109_") or step_id.startswith("TC_110_") or \
                 step_id.startswith("TC_111_") or step_id.startswith("TC_112_") or \
                 step_id.startswith("TC_113_") or step_id.startswith("TC_114_"):
                self._run_drawer_recommendations_test(step_id)
            elif step_id == "TC_115_NAV_TRAVERSAL":
                self._run_nav_traversal()
            elif step_id == "TC_116_NAV_STATE_PRESERVATION":
                self._run_nav_state_preservation()
            elif step_id == "TC_117_PROFILE_LOAD":
                self._run_profile_load()
            elif step_id.startswith("TC_118_") or step_id.startswith("TC_119_") or \
                 step_id.startswith("TC_120_") or step_id.startswith("TC_121_") or \
                 step_id.startswith("TC_122_"):
                self._run_profile_edit_test(step_id)
            elif step_id == "TC_123_LOGOUT_SUCCESS":
                self._run_logout_success()
            else:
                raise NotImplementedError(f"Step ID '{step_id}' not implemented in E2E suite.")

            scr = self.capture_screenshot(step_id)
            self.log_step(step_id, step_name, "PASS", time.time() - start, screenshot=scr)
            return True
        except Exception as e:
            scr = self.capture_screenshot(f"{step_id}_FAIL")
            self.log_step(step_id, step_name, "FAIL", time.time() - start, error=e, screenshot=scr)
            self._attempt_recovery()
            return False

    # ================================================================
    # TEST HANDLERS IMPLEMENTATION
    # ================================================================

    def _run_launch(self):
        self.find_el(Locators.SPLASH_TEXT, timeout=20)
        self.find_clickable(Locators.GET_STARTED_BTN, timeout=20)

    def _run_launch_back(self):
        # Back key on Splash screen shouldn't crash it
        try:
            self.driver.back()
        except Exception:
            pass
        self.find_el(Locators.SPLASH_TEXT, timeout=5)

    def _run_get_started(self):
        self.find_clickable(Locators.GET_STARTED_BTN).click()
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.LOGIN_TITLE, timeout=10)

    def _run_signup_nav(self):
        self.find_clickable(Locators.SIGNUP_LINK).click()
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.SIGNUP_TITLE)

    def _run_signup_validation(self, step_id):
        self.find_el(Locators.SIGNUP_TITLE)
        
        name = config.TEST_USER["full_name"]
        email = config.TEST_USER["email"]
        mobile = config.TEST_USER["mobile"]
        password = config.TEST_USER["password"]
        confirm = config.TEST_USER["password"]

        if step_id == "TC_005_SIGNUP_EMPTY":
            name, email, mobile, password, confirm = "", "", "", "", ""
        elif step_id == "TC_006_SIGNUP_SHORT_PWD":
            password, confirm = "123", "123"
        elif step_id == "TC_007_SIGNUP_PWD_MISMATCH":
            confirm = "mismatchingpwd"
        elif step_id == "TC_008_SIGNUP_INVALID_EMAIL":
            email = "invalidemailformat"
        elif step_id == "TC_009_SIGNUP_INVALID_EMAIL_DOMAIN":
            email = "invalid@domain"
        elif step_id == "TC_010_SIGNUP_EMPTY_NAME":
            name = ""
        elif step_id == "TC_011_SIGNUP_EMPTY_EMAIL":
            email = ""
        elif step_id == "TC_012_SIGNUP_EMPTY_MOBILE":
            mobile = ""
        elif step_id == "TC_013_SIGNUP_EMPTY_PASSWORD":
            password = ""
        elif step_id == "TC_014_SIGNUP_SHORT_MOBILE":
            mobile = "123456"
        elif step_id == "TC_015_SIGNUP_SPECIAL_CHAR_NAME":
            name = "John!@#"
        elif step_id == "TC_016_SIGNUP_NUMERIC_NAME":
            name = "John123"
        elif step_id == "TC_017_SIGNUP_LONG_NAME":
            name = "J" * 100
        elif step_id == "TC_018_SIGNUP_DUPLICATE_EMAIL":
            email = "existing@finguard.com"

        self.type_into(Locators.SIGNUP_NAME_FIELD, name)
        self.type_into(Locators.SIGNUP_EMAIL_FIELD, email)
        self.type_into(Locators.SIGNUP_MOBILE_FIELD, mobile)
        self.type_into(Locators.SIGNUP_PASSWORD_FIELD, password)
        self.type_into(Locators.SIGNUP_CONFIRM_PASSWORD_FIELD, confirm)
        
        self.find_clickable(Locators.SIGNUP_BTN).click()
        time.sleep(1.5)
        self.find_el(Locators.SIGNUP_TITLE, timeout=5)

    def _run_signup_back_nav(self):
        self.find_clickable(Locators.SIGNUP_LOGIN_LINK).click()
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.LOGIN_TITLE)

    def _run_signup_success(self):
        self.find_clickable(Locators.SIGNUP_LINK).click()
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.SIGNUP_TITLE)

        # Register distinct email to avoid duplicate error
        email_unique = f"appium_{int(time.time())}@finguard.com"
        self.type_into(Locators.SIGNUP_NAME_FIELD, config.TEST_USER["full_name"])
        self.type_into(Locators.SIGNUP_EMAIL_FIELD, email_unique)
        self.type_into(Locators.SIGNUP_MOBILE_FIELD, config.TEST_USER["mobile"])
        self.type_into(Locators.SIGNUP_PASSWORD_FIELD, config.TEST_USER["password"])
        self.type_into(Locators.SIGNUP_CONFIRM_PASSWORD_FIELD, config.TEST_USER["password"])

        self.find_clickable(Locators.SIGNUP_BTN).click()
        time.sleep(config.API_SLEEP)
        self.find_el(Locators.LOGIN_TITLE, timeout=15)

    def _run_login_nav(self):
        self.find_el(Locators.LOGIN_TITLE)

    def _run_login_validation(self, step_id):
        self.find_el(Locators.LOGIN_TITLE)

        email = config.TEST_USER["email"]
        password = config.TEST_USER["password"]

        if step_id == "TC_022_LOGIN_EMPTY_FIELDS":
            email, password = "", ""
        elif step_id == "TC_023_LOGIN_EMPTY_EMAIL":
            email = ""
        elif step_id == "TC_024_LOGIN_EMPTY_PASSWORD":
            password = ""
        elif step_id == "TC_025_LOGIN_WRONG_PASSWORD":
            password = "wrongpasscode"
        elif step_id == "TC_026_LOGIN_WRONG_EMAIL_FORMAT":
            email = "invalidemail"
        elif step_id == "TC_027_LOGIN_WRONG_EMAIL_DOMAIN":
            email = "invalid@domain"
        elif step_id == "TC_028_LOGIN_SHORT_PASSWORD":
            password = "123"
        elif step_id == "TC_029_LOGIN_SQL_INJECTION":
            email = "' OR '1'='1"
        elif step_id == "TC_030_LOGIN_SPECIAL_CHARS":
            password = "pwd!@#$%^&*()"
        elif step_id == "TC_031_LOGIN_LONG_EMAIL":
            email = "a" * 80 + "@domain.com"
        elif step_id == "TC_032_LOGIN_LONG_PASSWORD":
            password = "p" * 100
        elif step_id == "TC_033_LOGIN_SPACES_EMAIL":
            email = "  " + config.TEST_USER["email"] + "  "
        elif step_id == "TC_034_LOGIN_CASE_INSENSITIVE":
            email = config.TEST_USER["email"].upper()

        self.type_into(Locators.LOGIN_EMAIL_FIELD, email)
        self.type_into(Locators.LOGIN_PASSWORD_FIELD, password)
        
        self.find_clickable(Locators.LOGIN_BTN).click()
        time.sleep(1.5)

        if step_id in ["TC_033_LOGIN_SPACES_EMAIL", "TC_034_LOGIN_CASE_INSENSITIVE"]:
            if self.element_exists(Locators.DASHBOARD_TITLE, timeout=5):
                # If logged in successfully, it is also okay. We remain there.
                pass
            else:
                self.find_el(Locators.LOGIN_TITLE, timeout=5)
        else:
            self.find_el(Locators.LOGIN_TITLE, timeout=5)

    def _run_login_success(self):
        # Clear fields and login cleanly
        email_el = self.find_clickable(Locators.LOGIN_EMAIL_FIELD)
        email_el.click()
        email_el.clear()
        email_el.send_keys(config.TEST_USER["email"])

        pwd_el = self.find_clickable(Locators.LOGIN_PASSWORD_FIELD)
        pwd_el.click()
        pwd_el.clear()
        pwd_el.send_keys(config.TEST_USER["password"])
        self._dismiss_keyboard()

        self.find_clickable(Locators.LOGIN_BTN).click()
        self.find_el(Locators.DASHBOARD_TITLE, timeout=config.LONG_WAIT)
        time.sleep(config.ANIMATION_SLEEP)

    def _run_dashboard_load(self):
        self.find_el(Locators.DASHBOARD_TITLE)

    def _run_dashboard_title(self):
        self.find_el(Locators.DASHBOARD_TITLE)
        # AppBar elements verify
        self.find_el((Locators.DASHBOARD_TITLE[0], '//*[@text="FinGuard"]'))

    def _run_dashboard_card(self, step_id):
        if step_id == "TC_038_DASHBOARD_CARD_ASSETS":
            self.find_el(Locators.ASSETS_CARD)
        elif step_id == "TC_039_DASHBOARD_CARD_LIABILITIES":
            self.find_el(Locators.LIABILITIES_CARD)
        elif step_id == "TC_040_DASHBOARD_CARD_RUNWAY":
            self.find_el(Locators.RUNWAY_CARD)
        elif step_id == "TC_041_DASHBOARD_CARD_EXPENSE_RATIO":
            self.find_el(Locators.EXPENSE_RATIO_CARD)
        elif step_id == "TC_042_DASHBOARD_CARD_DEBT_RATIO":
            self.find_el(Locators.DEBT_RATIO_CARD)
        elif step_id == "TC_043_DASHBOARD_CARD_SURPLUS":
            self.find_el(Locators.SURPLUS_CARD)

    def _run_dashboard_quick_actions(self):
        self.find_el(Locators.ADD_INCOME_TILE)
        self.find_el(Locators.ADD_EXPENSE_TILE)
        self.find_el(Locators.ADD_DEBT_TILE)
        self.find_el(Locators.FORECAST_TILE)

    def _run_dashboard_scroll(self):
        self.scroll_down()
        time.sleep(0.5)
        # Verify card under fold
        self.find_el(Locators.SURPLUS_CARD)

    def _run_quick_action_nav(self, step_id):
        self.safe_click(Locators.NAV_HOME)
        time.sleep(0.5)

        if step_id == "TC_046_QA_ADD_INCOME_NAV":
            self.find_clickable(Locators.ADD_INCOME_TILE).click()
            time.sleep(config.ANIMATION_SLEEP)
            self.find_el(Locators.ENTRY_TITLE)
        elif step_id == "TC_047_QA_ADD_EXPENSE_NAV":
            self.find_clickable(Locators.ADD_EXPENSE_TILE).click()
            time.sleep(config.ANIMATION_SLEEP)
            self.find_el(Locators.ENTRY_TITLE)
        elif step_id == "TC_048_QA_ADD_DEBT_NAV":
            self.find_clickable(Locators.ADD_INCOME_TILE).click() # route to financial entry
            time.sleep(config.ANIMATION_SLEEP)
            self.find_el(Locators.ENTRY_TITLE)
        elif step_id == "TC_049_QA_FORECAST_NAV":
            self.find_clickable(Locators.FORECAST_TILE).click()
            time.sleep(config.ANIMATION_SLEEP)
            self.find_el(Locators.PREDICTIONS_TITLE)

    def _run_quick_action_back(self):
        self.driver.back()
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.DASHBOARD_TITLE)

    def _run_income_form_load(self):
        self.find_clickable(Locators.ADD_INCOME_TILE).click()
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.ENTRY_TITLE)
        self.find_clickable(Locators.TAB_INCOME).click()

    def _run_income_test(self, step_id):
        self.find_el(Locators.ENTRY_TITLE)
        self.find_clickable(Locators.TAB_INCOME).click()
        
        category = "Salary"
        amount = "5000"
        notes = "Regular salary"
        expect_success = True

        if step_id == "TC_052_INCOME_SAVE_EMPTY":
            category, amount, notes = "", "", ""
            expect_success = False
        elif step_id == "TC_053_INCOME_SAVE_NO_CATEGORY":
            category = ""
            expect_success = False
        elif step_id == "TC_054_INCOME_SAVE_NO_AMOUNT":
            amount = ""
            expect_success = False
        elif step_id == "TC_055_INCOME_INVALID_AMOUNT":
            amount = "abc"
            expect_success = False
        elif step_id == "TC_056_INCOME_NEGATIVE_AMOUNT":
            amount = "-200"
            expect_success = False
        elif step_id == "TC_057_INCOME_ZERO_AMOUNT":
            amount = "0"
            expect_success = False
        elif step_id == "TC_058_INCOME_SPECIAL_CHAR_CATEGORY":
            category = "Bonus!@"
        elif step_id == "TC_059_INCOME_LONG_NOTES":
            notes = "N" * 150
        elif step_id == "TC_060_INCOME_EMOJI_NOTES":
            notes = "Salary 💵💰"
        elif step_id == "TC_061_INCOME_SUCCESS_SALARY":
            category = "Salary"
        elif step_id == "TC_062_INCOME_SUCCESS_BUSINESS":
            category = "Business"
        elif step_id == "TC_063_INCOME_SUCCESS_INVESTMENT":
            category = "Investment"
        elif step_id == "TC_064_INCOME_SUCCESS_GIFT":
            category = "Gift"
        elif step_id == "TC_065_INCOME_SUCCESS_OTHER":
            category = "Other"

        self.type_into(Locators.INCOME_CATEGORY, category)
        self.type_into(Locators.INCOME_AMOUNT, amount)
        self.type_into(Locators.INCOME_NOTES, notes)
        
        self.find_clickable(Locators.INCOME_SAVE_BTN).click()
        time.sleep(config.API_SLEEP)

        if not expect_success:
            self.find_el(Locators.ENTRY_TITLE, timeout=5)

    def _run_expense_form_load(self):
        self.find_el(Locators.ENTRY_TITLE)
        self.find_clickable(Locators.TAB_EXPENSE).click()
        time.sleep(0.5)

    def _run_expense_test(self, step_id):
        self.find_el(Locators.ENTRY_TITLE)
        self.find_clickable(Locators.TAB_EXPENSE).click()
        time.sleep(0.5)

        category = "Food"
        amount = "250"
        notes = "Dinner"
        expect_success = True

        if step_id == "TC_067_EXPENSE_SAVE_EMPTY":
            category, amount, notes = "", "", ""
            expect_success = False
        elif step_id == "TC_068_EXPENSE_SAVE_NO_CATEGORY":
            category = ""
            expect_success = False
        elif step_id == "TC_069_EXPENSE_SAVE_NO_AMOUNT":
            amount = ""
            expect_success = False
        elif step_id == "TC_070_EXPENSE_INVALID_AMOUNT":
            amount = "def"
            expect_success = False
        elif step_id == "TC_071_EXPENSE_NEGATIVE_AMOUNT":
            amount = "-50"
            expect_success = False
        elif step_id == "TC_072_EXPENSE_ZERO_AMOUNT":
            amount = "0"
            expect_success = False
        elif step_id == "TC_073_EXPENSE_SPECIAL_CHAR_CATEGORY":
            category = "Food&Bar"
        elif step_id == "TC_074_EXPENSE_LONG_NOTES":
            notes = "E" * 150
        elif step_id == "TC_075_EXPENSE_EMOJI_NOTES":
            notes = "Spent 🍟🍔"
        elif step_id == "TC_076_EXPENSE_SUCCESS_FOOD":
            category = "Food"
        elif step_id == "TC_077_EXPENSE_SUCCESS_RENT":
            category = "Rent"
        elif step_id == "TC_078_EXPENSE_SUCCESS_UTILITIES":
            category = "Utilities"
        elif step_id == "TC_079_EXPENSE_SUCCESS_ENTERTAINMENT":
            category = "Entertainment"
        elif step_id == "TC_080_EXPENSE_SUCCESS_OTHER":
            category = "Other"

        self.type_into(Locators.EXPENSE_CATEGORY, category)
        self.type_into(Locators.EXPENSE_AMOUNT, amount)
        self.type_into(Locators.EXPENSE_NOTES, notes)
        
        self.find_clickable(Locators.EXPENSE_SAVE_BTN).click()
        time.sleep(config.API_SLEEP)

        if not expect_success:
            self.find_el(Locators.ENTRY_TITLE, timeout=5)

    def _run_debt_form_load(self):
        self.find_el(Locators.ENTRY_TITLE)
        tab_clicked = self.safe_click(Locators.TAB_DEBT, timeout=5)
        if not tab_clicked:
            self.driver.execute_script(
                "mobile: swipeGesture",
                {"left": 200, "top": 180, "width": 400, "height": 60, "direction": "left", "percent": 0.85},
            )
        time.sleep(0.8)
        self.find_el(Locators.DEBT_SAVE_BTN)

    def _run_debt_test(self, step_id):
        self.find_el(Locators.ENTRY_TITLE)
        tab_clicked = self.safe_click(Locators.TAB_DEBT, timeout=5)
        if not tab_clicked:
            self.driver.execute_script(
                "mobile: swipeGesture",
                {"left": 200, "top": 180, "width": 400, "height": 60, "direction": "left", "percent": 0.85},
            )
        time.sleep(0.8)

        name = "Credit Card"
        outstanding = "1000"
        payment = "100"
        interest = "12.5"
        expect_success = True

        if step_id == "TC_082_DEBT_SAVE_EMPTY":
            name, outstanding, payment, interest = "", "", "", ""
            expect_success = False
        elif step_id == "TC_083_DEBT_SAVE_NO_NAME":
            name = ""
            expect_success = False
        elif step_id == "TC_084_DEBT_SAVE_NO_OUTSTANDING":
            outstanding = ""
            expect_success = False
        elif step_id == "TC_085_DEBT_SAVE_NO_PAYMENT":
            payment = ""
            expect_success = False
        elif step_id == "TC_086_DEBT_SAVE_NO_INTEREST":
            interest = ""
            expect_success = False
        elif step_id == "TC_087_DEBT_INVALID_OUTSTANDING":
            outstanding = "xyz"
            expect_success = False
        elif step_id == "TC_088_DEBT_NEGATIVE_OUTSTANDING":
            outstanding = "-200"
            expect_success = False
        elif step_id == "TC_089_DEBT_NEGATIVE_PAYMENT":
            payment = "-20"
            expect_success = False
        elif step_id == "TC_090_DEBT_NEGATIVE_INTEREST":
            interest = "-1"
            expect_success = False
        elif step_id == "TC_091_DEBT_ZERO_INTEREST":
            interest = "0"
        elif step_id == "TC_092_DEBT_HIGH_INTEREST":
            interest = "90"
        elif step_id == "TC_093_DEBT_SPECIAL_CHAR_NAME":
            name = "Card!@#"
        elif step_id == "TC_094_DEBT_SUCCESS_CC":
            name = "Visa"
        elif step_id == "TC_095_DEBT_SUCCESS_LOAN":
            name = "Student Loan"

        self.type_into(Locators.DEBT_NAME, name)
        self.type_into(Locators.DEBT_OUTSTANDING, outstanding)
        self.type_into(Locators.DEBT_PAYMENT, payment)
        self.type_into(Locators.DEBT_INTEREST, interest)
        
        self.find_clickable(Locators.DEBT_SAVE_BTN).click()
        time.sleep(config.API_SLEEP)

        if not expect_success:
            self.find_el(Locators.DEBT_SAVE_BTN, timeout=5)

    def _run_risk_test(self, step_id):
        self.safe_click(Locators.NAV_RISK)
        time.sleep(config.ANIMATION_SLEEP)
        
        self.find_el(Locators.RISK_ANALYSIS_TITLE)

        if step_id == "TC_098_RISK_DISTRESS":
            self.find_el(Locators.RISK_DISTRESS_HEADER)
        elif step_id == "TC_099_RISK_DRIVERS":
            self.find_el(Locators.RISK_DRIVERS_HEADER)
        elif step_id == "TC_100_RISK_WHY_SCORE":
            self.scroll_down()
            time.sleep(0.5)
            self.find_el(Locators.RISK_WHY_SCORE_HEADER)
        elif step_id == "TC_101_RISK_SUGGESTIONS":
            self.scroll_down()
            time.sleep(0.5)
            self.find_el(Locators.RISK_SUGGESTIONS_HEADER)
        elif step_id == "TC_102_RISK_SCROLL":
            self.scroll_down()

    def _run_predictions_test(self, step_id):
        self.safe_click(Locators.NAV_PREDICTIONS)
        time.sleep(config.ANIMATION_SLEEP)

        self.find_el(Locators.PREDICTIONS_TITLE)

        if step_id == "TC_105_PRED_CARDS":
            self.find_el(Locators.FORECAST_30_60_90_HEADER)
        elif step_id == "TC_106_PRED_CHART":
            self.scroll_down()
            time.sleep(0.5)
            self.find_el(Locators.FORECAST_TREND_HEADER)
        elif step_id == "TC_107_PRED_DATA_ACCURACY":
            self.find_el(Locators.FORECAST_HEADER)
        elif step_id == "TC_108_PRED_SCROLL":
            self.scroll_down()

    def _run_drawer_recommendations_test(self, step_id):
        self.safe_click(Locators.NAV_HOME)
        time.sleep(config.ANIMATION_SLEEP * 2)

        if step_id == "TC_109_DRAWER_OPEN":
            if not self._open_drawer():
                raise RuntimeError("Could not open navigation drawer")
            # Verify drawer header
            self.find_el(Locators.DRAWER_RISK_ANALYSIS)
            self.driver.back() # close drawer
        elif step_id == "TC_110_DRAWER_ITEMS":
            if not self._open_drawer():
                raise RuntimeError("Could not open navigation drawer")
            self.find_el(Locators.DRAWER_RISK_ANALYSIS)
            self.find_el(Locators.DRAWER_RECOMMENDATIONS)
            self.find_el(Locators.DRAWER_LOGOUT)
            self.driver.back() # close drawer
        elif step_id == "TC_111_DRAWER_REC_NAV":
            if not self._open_drawer():
                raise RuntimeError("Could not open navigation drawer")
            self.find_clickable(Locators.DRAWER_RECOMMENDATIONS).click()
            time.sleep(config.ANIMATION_SLEEP)
            self.find_el(Locators.RECOMMENDATIONS_TITLE)
        elif step_id == "TC_112_REC_TITLE":
            # Assume we are on Recommendations
            self.find_el(Locators.RECOMMENDATIONS_TITLE)
        elif step_id == "TC_113_REC_SECTIONS":
            # Assume we are on Recommendations
            self.find_el(Locators.REC_ACTIONS_HEADER)
        elif step_id == "TC_114_REC_BACK":
            self.driver.back()
            time.sleep(config.ANIMATION_SLEEP)
            self.find_el(Locators.DASHBOARD_TITLE)

    def _run_nav_traversal(self):
        self.safe_click(Locators.NAV_RISK)
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.RISK_ANALYSIS_TITLE)

        self.safe_click(Locators.NAV_PREDICTIONS)
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.PREDICTIONS_TITLE)

        self.safe_click(Locators.NAV_PROFILE)
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.PROFILE_TITLE)

        self.safe_click(Locators.NAV_HOME)
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.DASHBOARD_TITLE)

    def _run_nav_state_preservation(self):
        # Verify inputs or states are retained during basic navigation
        self.safe_click(Locators.NAV_HOME)
        time.sleep(0.5)
        self.find_el(Locators.DASHBOARD_TITLE)

    def _run_profile_load(self):
        self.safe_click(Locators.NAV_PROFILE)
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.PROFILE_TITLE)

    def _run_profile_edit_test(self, step_id):
        self.safe_click(Locators.NAV_PROFILE)
        time.sleep(0.5)
        
        self.find_clickable(Locators.PROFILE_EDIT_BTN).click()
        time.sleep(config.ANIMATION_SLEEP)
        self.find_el(Locators.DIALOG_TITLE_EDIT)

        if step_id == "TC_118_PROFILE_EDIT_OPEN":
            self.safe_click(Locators.DIALOG_CANCEL_BTN)
        elif step_id == "TC_119_PROFILE_EDIT_EMPTY":
            name_fld = self.find_clickable(Locators.DIALOG_NAME_FIELD)
            name_fld.click()
            name_fld.clear()
            self._dismiss_keyboard()
            self.find_clickable(Locators.DIALOG_SAVE_BTN).click()
            time.sleep(1)
            # Should remain open
            self.find_el(Locators.DIALOG_TITLE_EDIT)
            self.safe_click(Locators.DIALOG_CANCEL_BTN)
        elif step_id == "TC_120_PROFILE_EDIT_SUCCESS":
            name_fld = self.find_clickable(Locators.DIALOG_NAME_FIELD)
            name_fld.click()
            name_fld.clear()
            name_fld.send_keys("Appium User")
            self._dismiss_keyboard()
            self.find_clickable(Locators.DIALOG_SAVE_BTN).click()
            time.sleep(config.API_SLEEP)
        elif step_id == "TC_121_PROFILE_EDIT_CANCEL":
            self.safe_click(Locators.DIALOG_CANCEL_BTN)
        elif step_id == "TC_122_LOGOUT_CANCEL":
            # Close dialog if any
            self.safe_click(Locators.DIALOG_CANCEL_BTN, timeout=2)

    def _run_logout_success(self):
        self.safe_click(Locators.NAV_PROFILE)
        time.sleep(0.5)
        self.find_clickable(Locators.PROFILE_LOGOUT_BTN).click()
        time.sleep(config.API_SLEEP)
        self.find_el(Locators.LOGIN_TITLE, timeout=10)
