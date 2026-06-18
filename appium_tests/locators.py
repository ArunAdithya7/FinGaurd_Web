"""
locators.py
-----------
Central element locator definitions for the FinGuard Android app.
Uses AppiumBy strategies that are robust against Flutter rendered elements.

Screen Coverage:
  - Splash / Get Started
  - Login
  - Signup
  - Dashboard (summary cards, quick action tiles, drawer)
  - Financial Entry  (Income / Expense / Debt tabs)
  - Risk Analysis
  - Predictions / Forecast
  - Recommendations
  - Profile  (view, edit dialog, change-password dialog, logout)
"""

from appium.webdriver.common.appiumby import AppiumBy


class Locators:
    # ============================================================
    # SPLASH & GET STARTED
    # ============================================================
    SPLASH_TEXT       = (AppiumBy.XPATH, '//*[@text="FinGuard"]')
    SPLASH_LOGO       = (AppiumBy.XPATH, "//android.widget.ImageView")
    GET_STARTED_BTN   = (AppiumBy.XPATH, '//*[@text="Get Started"]')

    # ============================================================
    # LOGIN SCREEN
    # ============================================================
    LOGIN_TITLE          = (AppiumBy.XPATH, '//*[@text="Welcome Back!"]')
    LOGIN_EMAIL_FIELD    = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"email") '
        'or contains(@text,"Email") '
        'or contains(@hint,"email") '
        'or contains(@hint,"Email")]',
    )
    LOGIN_PASSWORD_FIELD = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"password") '
        'or contains(@text,"Password") '
        'or contains(@hint,"password") '
        'or contains(@hint,"Password")]',
    )
    LOGIN_BTN            = (AppiumBy.XPATH, '//*[@text="Login"]')
    SIGNUP_LINK          = (AppiumBy.XPATH, '//*[@text="Sign Up"]')
    # Error snackbar or any error text appearing after bad login
    LOGIN_ERROR_MSG      = (
        AppiumBy.XPATH,
        '//*[contains(@text,"Invalid") '
        'or contains(@text,"incorrect") '
        'or contains(@text,"wrong") '
        'or contains(@text,"error")]',
    )

    # ============================================================
    # SIGNUP SCREEN
    # ============================================================
    SIGNUP_TITLE                  = (AppiumBy.XPATH, '//*[@text="Create Account"]')
    SIGNUP_NAME_FIELD             = (
        AppiumBy.XPATH,
        '//android.widget.EditText[@text="Full Name" '
        'or contains(@text,"Name") '
        'or contains(@hint,"Name")]',
    )
    SIGNUP_EMAIL_FIELD            = (
        AppiumBy.XPATH,
        '//android.widget.EditText[@text="Email" '
        'or contains(@hint,"Email")]',
    )
    SIGNUP_MOBILE_FIELD           = (
        AppiumBy.XPATH,
        '//android.widget.EditText[@text="Mobile Number" '
        'or contains(@text,"Mobile") '
        'or contains(@hint,"Mobile")]',
    )
    SIGNUP_PASSWORD_FIELD         = (
        AppiumBy.XPATH,
        '//android.widget.EditText[@text="Password" '
        'or contains(@hint,"Password")]',
    )
    SIGNUP_CONFIRM_PASSWORD_FIELD = (
        AppiumBy.XPATH,
        '//android.widget.EditText[@text="Confirm Password" '
        'or contains(@hint,"Confirm")]',
    )
    SIGNUP_BTN                    = (AppiumBy.XPATH, '//*[@text="Sign Up"]')
    # Back to Login link
    SIGNUP_LOGIN_LINK             = (
        AppiumBy.XPATH,
        '//*[contains(@text,"Login") or contains(@text,"Already have")]',
    )

    # ============================================================
    # DASHBOARD SCREEN
    # ============================================================
    DASHBOARD_TITLE    = (AppiumBy.XPATH, '//*[@text="Dashboard"]')
    DRAWER_OPEN_BTN    = (
        AppiumBy.XPATH,
        '//android.widget.ImageButton[@content-desc="Open navigation drawer"]',
    )

    # Summary / Metric Cards
    ASSETS_CARD     = (AppiumBy.XPATH, '//*[contains(@text,"Assets")]')
    LIABILITIES_CARD = (AppiumBy.XPATH, '//*[contains(@text,"Liabilities")]')
    RUNWAY_CARD     = (AppiumBy.XPATH, '//*[contains(@text,"Savings Runway")]')
    EXPENSE_RATIO_CARD = (AppiumBy.XPATH, '//*[contains(@text,"Expense Ratio")]')
    DEBT_RATIO_CARD = (AppiumBy.XPATH, '//*[contains(@text,"Debt Ratio")]')
    SURPLUS_CARD    = (AppiumBy.XPATH, '//*[contains(@text,"Monthly Surplus")]')

    # Quick Action Tiles
    ADD_INCOME_TILE  = (AppiumBy.XPATH, '//*[@text="Add Income"]')
    ADD_EXPENSE_TILE = (AppiumBy.XPATH, '//*[@text="Add Expense"]')
    ADD_DEBT_TILE    = (AppiumBy.XPATH, '//*[@text="Add Debt"]')
    FORECAST_TILE    = (AppiumBy.XPATH, '//*[@text="Forecast"]')

    # Bottom Navigation Bar
    NAV_HOME        = (
        AppiumBy.XPATH,
        '//android.widget.TextView[@text="Home"] | //*[@content-desc="Home"]',
    )
    NAV_RISK        = (
        AppiumBy.XPATH,
        '//android.widget.TextView[@text="Risk"] | //*[@content-desc="Risk"]',
    )
    NAV_PREDICTIONS = (
        AppiumBy.XPATH,
        '//android.widget.TextView[@text="Predictions"] | //*[@content-desc="Predictions"]',
    )
    NAV_PROFILE     = (
        AppiumBy.XPATH,
        '//android.widget.TextView[@text="Profile"] | //*[@content-desc="Profile"]',
    )

    # ============================================================
    # NAVIGATION DRAWER
    # ============================================================
    DRAWER_RISK_ANALYSIS    = (AppiumBy.XPATH, '//*[@text="Risk Analysis"]')
    DRAWER_RECOMMENDATIONS  = (AppiumBy.XPATH, '//*[@text="Recommendations"]')
    DRAWER_LOGOUT           = (AppiumBy.XPATH, '//*[@text="Logout"]')

    # ============================================================
    # FINANCIAL ENTRY SCREEN
    # ============================================================
    ENTRY_TITLE     = (AppiumBy.XPATH, '//*[@text="Add Financial Data"]')
    TAB_INCOME      = (AppiumBy.XPATH, '//*[@text="Income" or @text="INCOME"]')
    TAB_EXPENSE     = (AppiumBy.XPATH, '//*[@text="Expense" or @text="EXPENSE"]')
    TAB_DEBT        = (AppiumBy.XPATH, '//*[@text="Debt" or @text="DEBT"]')

    # Income Form
    INCOME_CATEGORY = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"category") '
        'or contains(@text,"Category") '
        'or contains(@hint,"category")]',
    )
    INCOME_AMOUNT   = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"Amount") '
        'or contains(@hint,"Amount")]',
    )
    INCOME_NOTES    = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"Notes") '
        'or contains(@hint,"Notes")]',
    )
    INCOME_SAVE_BTN = (AppiumBy.XPATH, '//*[@text="Save Income"]')

    # Expense Form
    EXPENSE_CATEGORY = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"category") '
        'or contains(@text,"Category") '
        'or contains(@hint,"category")]',
    )
    EXPENSE_AMOUNT   = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"Amount") '
        'or contains(@hint,"Amount")]',
    )
    EXPENSE_NOTES    = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"Notes") '
        'or contains(@hint,"Notes")]',
    )
    EXPENSE_SAVE_BTN = (AppiumBy.XPATH, '//*[@text="Save Expense"]')

    # Debt Form
    DEBT_NAME        = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"name") '
        'or contains(@text,"Name") '
        'or contains(@hint,"Name")]',
    )
    DEBT_OUTSTANDING = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"Outstanding") '
        'or contains(@hint,"Outstanding")]',
    )
    DEBT_PAYMENT     = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"payment") '
        'or contains(@text,"Payment") '
        'or contains(@hint,"Payment")]',
    )
    DEBT_INTEREST    = (
        AppiumBy.XPATH,
        '//android.widget.EditText[contains(@text,"interest") '
        'or contains(@text,"Interest") '
        'or contains(@hint,"Interest")]',
    )
    DEBT_SAVE_BTN    = (AppiumBy.XPATH, '//*[@text="Save Debt"]')

    # ============================================================
    # RISK ANALYSIS SCREEN
    # ============================================================
    RISK_ANALYSIS_TITLE        = (AppiumBy.XPATH, '//*[@text="Risk Analysis"]')
    RISK_DISTRESS_HEADER       = (AppiumBy.XPATH, '//*[contains(@text,"Financial Distress Risk")]')
    RISK_DRIVERS_HEADER        = (AppiumBy.XPATH, '//*[contains(@text,"Risk Drivers")]')
    RISK_WHY_SCORE_HEADER      = (AppiumBy.XPATH, '//*[contains(@text,"Why this score")]')
    RISK_SUGGESTIONS_HEADER    = (AppiumBy.XPATH, '//*[contains(@text,"Suggested Actions")]')
    RISK_EXPENSE_RATIO_CARD    = (AppiumBy.XPATH, '//*[contains(@text,"Expense Ratio")]')
    RISK_DEBT_RATIO_CARD       = (AppiumBy.XPATH, '//*[contains(@text,"Debt Ratio")]')
    RISK_SAVINGS_RUNWAY_CARD   = (AppiumBy.XPATH, '//*[contains(@text,"Savings Runway")]')
    RISK_MONTHLY_SURPLUS_CARD  = (AppiumBy.XPATH, '//*[contains(@text,"Monthly Surplus")]')

    # ============================================================
    # PREDICTIONS / FORECAST SCREEN
    # ============================================================
    PREDICTIONS_TITLE        = (AppiumBy.XPATH, '//*[@text="Predictions"]')
    FORECAST_HEADER          = (AppiumBy.XPATH, '//*[contains(@text,"Forecasted Financial Risk")]')
    FORECAST_30_60_90_HEADER = (AppiumBy.XPATH, '//*[contains(@text,"30 / 60 / 90")]')
    FORECAST_TREND_HEADER    = (AppiumBy.XPATH, '//*[contains(@text,"Risk Trend Preview")]')
    FORECAST_REC_HEADER      = (AppiumBy.XPATH, '//*[contains(@text,"Recommended Actions")]')

    # ============================================================
    # RECOMMENDATIONS SCREEN
    # ============================================================
    RECOMMENDATIONS_TITLE    = (AppiumBy.XPATH, '//*[@text="Recommendations"]')
    REC_ACTIONS_HEADER       = (AppiumBy.XPATH, '//*[contains(@text,"Recommended Actions")]')
    REC_PRIORITY_HEADER      = (AppiumBy.XPATH, '//*[contains(@text,"Priority Actions")]')
    REC_DETAILED_HEADER      = (AppiumBy.XPATH, '//*[contains(@text,"Detailed Recommendations")]')

    # ============================================================
    # PROFILE SCREEN
    # ============================================================
    PROFILE_TITLE           = (AppiumBy.XPATH, '//*[@text="Profile"]')
    PROFILE_EDIT_BTN        = (AppiumBy.XPATH, '//*[@text="Edit Profile"]')
    PROFILE_CHANGE_PWD_BTN  = (AppiumBy.XPATH, '//*[@text="Change Password"]')
    PROFILE_LOGOUT_BTN      = (AppiumBy.XPATH, '//*[@text="Logout"]')

    # Edit Profile Dialog
    DIALOG_TITLE_EDIT   = (AppiumBy.XPATH, '//*[@text="Edit Profile"]')
    DIALOG_NAME_FIELD   = (AppiumBy.XPATH, '//android.widget.EditText[1]')
    DIALOG_MOBILE_FIELD = (AppiumBy.XPATH, '//android.widget.EditText[2]')
    DIALOG_CANCEL_BTN   = (AppiumBy.XPATH, '//*[@text="Cancel"]')
    DIALOG_SAVE_BTN     = (AppiumBy.XPATH, '//*[@text="Save"]')

    # Change Password Dialog
    DIALOG_TITLE_PWD    = (AppiumBy.XPATH, '//*[@text="Change Password"]')
    DIALOG_CURRENT_PWD  = (AppiumBy.XPATH, '//android.widget.EditText[1]')
    DIALOG_NEW_PWD      = (AppiumBy.XPATH, '//android.widget.EditText[2]')
    DIALOG_UPDATE_BTN   = (AppiumBy.XPATH, '//*[@text="Update"]')
