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
    ("TC_124_FILTER_124", "Verify Transaction Filtering - Test Case Scenario version 124"),
    ("TC_125_FILTER_125", "Verify Transaction Filtering - Test Case Scenario version 125"),
    ("TC_126_FILTER_126", "Verify Transaction Filtering - Test Case Scenario version 126"),
    ("TC_127_FILTER_127", "Verify Transaction Filtering - Test Case Scenario version 127"),
    ("TC_128_FILTER_128", "Verify Transaction Filtering - Test Case Scenario version 128"),
    ("TC_129_FILTER_129", "Verify Transaction Filtering - Test Case Scenario version 129"),
    ("TC_130_FILTER_130", "Verify Transaction Filtering - Test Case Scenario version 130"),
    ("TC_131_FILTER_131", "Verify Transaction Filtering - Test Case Scenario version 131"),
    ("TC_132_FILTER_132", "Verify Transaction Filtering - Test Case Scenario version 132"),
    ("TC_133_FILTER_133", "Verify Transaction Filtering - Test Case Scenario version 133"),
    ("TC_134_FILTER_134", "Verify Transaction Filtering - Test Case Scenario version 134"),
    ("TC_135_FILTER_135", "Verify Transaction Filtering - Test Case Scenario version 135"),
    ("TC_136_FILTER_136", "Verify Transaction Filtering - Test Case Scenario version 136"),
    ("TC_137_FILTER_137", "Verify Transaction Filtering - Test Case Scenario version 137"),
    ("TC_138_FILTER_138", "Verify Transaction Filtering - Test Case Scenario version 138"),
    ("TC_139_FILTER_139", "Verify Transaction Filtering - Test Case Scenario version 139"),
    ("TC_140_FILTER_140", "Verify Transaction Filtering - Test Case Scenario version 140"),
    ("TC_141_FILTER_141", "Verify Transaction Filtering - Test Case Scenario version 141"),
    ("TC_142_FILTER_142", "Verify Transaction Filtering - Test Case Scenario version 142"),
    ("TC_143_FILTER_143", "Verify Transaction Filtering - Test Case Scenario version 143"),
    ("TC_144_FILTER_144", "Verify Transaction Filtering - Test Case Scenario version 144"),
    ("TC_145_FILTER_145", "Verify Transaction Filtering - Test Case Scenario version 145"),
    ("TC_146_BUDGET_146", "Verify Budgeting and Financial Goals - Test Case Scenario version 146"),
    ("TC_147_BUDGET_147", "Verify Budgeting and Financial Goals - Test Case Scenario version 147"),
    ("TC_148_BUDGET_148", "Verify Budgeting and Financial Goals - Test Case Scenario version 148"),
    ("TC_149_BUDGET_149", "Verify Budgeting and Financial Goals - Test Case Scenario version 149"),
    ("TC_150_BUDGET_150", "Verify Budgeting and Financial Goals - Test Case Scenario version 150"),
    ("TC_151_BUDGET_151", "Verify Budgeting and Financial Goals - Test Case Scenario version 151"),
    ("TC_152_BUDGET_152", "Verify Budgeting and Financial Goals - Test Case Scenario version 152"),
    ("TC_153_BUDGET_153", "Verify Budgeting and Financial Goals - Test Case Scenario version 153"),
    ("TC_154_BUDGET_154", "Verify Budgeting and Financial Goals - Test Case Scenario version 154"),
    ("TC_155_BUDGET_155", "Verify Budgeting and Financial Goals - Test Case Scenario version 155"),
    ("TC_156_BUDGET_156", "Verify Budgeting and Financial Goals - Test Case Scenario version 156"),
    ("TC_157_BUDGET_157", "Verify Budgeting and Financial Goals - Test Case Scenario version 157"),
    ("TC_158_BUDGET_158", "Verify Budgeting and Financial Goals - Test Case Scenario version 158"),
    ("TC_159_BUDGET_159", "Verify Budgeting and Financial Goals - Test Case Scenario version 159"),
    ("TC_160_BUDGET_160", "Verify Budgeting and Financial Goals - Test Case Scenario version 160"),
    ("TC_161_BUDGET_161", "Verify Budgeting and Financial Goals - Test Case Scenario version 161"),
    ("TC_162_BUDGET_162", "Verify Budgeting and Financial Goals - Test Case Scenario version 162"),
    ("TC_163_BUDGET_163", "Verify Budgeting and Financial Goals - Test Case Scenario version 163"),
    ("TC_164_BUDGET_164", "Verify Budgeting and Financial Goals - Test Case Scenario version 164"),
    ("TC_165_BUDGET_165", "Verify Budgeting and Financial Goals - Test Case Scenario version 165"),
    ("TC_166_BUDGET_166", "Verify Budgeting and Financial Goals - Test Case Scenario version 166"),
    ("TC_167_BUDGET_167", "Verify Budgeting and Financial Goals - Test Case Scenario version 167"),
    ("TC_168_BUDGET_168", "Verify Budgeting and Financial Goals - Test Case Scenario version 168"),
    ("TC_169_BUDGET_169", "Verify Budgeting and Financial Goals - Test Case Scenario version 169"),
    ("TC_170_BUDGET_170", "Verify Budgeting and Financial Goals - Test Case Scenario version 170"),
    ("TC_171_INSIGHTS_171", "Verify Financial Insights and Analytics - Test Case Scenario version 171"),
    ("TC_172_INSIGHTS_172", "Verify Financial Insights and Analytics - Test Case Scenario version 172"),
    ("TC_173_INSIGHTS_173", "Verify Financial Insights and Analytics - Test Case Scenario version 173"),
    ("TC_174_INSIGHTS_174", "Verify Financial Insights and Analytics - Test Case Scenario version 174"),
    ("TC_175_INSIGHTS_175", "Verify Financial Insights and Analytics - Test Case Scenario version 175"),
    ("TC_176_INSIGHTS_176", "Verify Financial Insights and Analytics - Test Case Scenario version 176"),
    ("TC_177_INSIGHTS_177", "Verify Financial Insights and Analytics - Test Case Scenario version 177"),
    ("TC_178_INSIGHTS_178", "Verify Financial Insights and Analytics - Test Case Scenario version 178"),
    ("TC_179_INSIGHTS_179", "Verify Financial Insights and Analytics - Test Case Scenario version 179"),
    ("TC_180_INSIGHTS_180", "Verify Financial Insights and Analytics - Test Case Scenario version 180"),
    ("TC_181_INSIGHTS_181", "Verify Financial Insights and Analytics - Test Case Scenario version 181"),
    ("TC_182_INSIGHTS_182", "Verify Financial Insights and Analytics - Test Case Scenario version 182"),
    ("TC_183_INSIGHTS_183", "Verify Financial Insights and Analytics - Test Case Scenario version 183"),
    ("TC_184_INSIGHTS_184", "Verify Financial Insights and Analytics - Test Case Scenario version 184"),
    ("TC_185_INSIGHTS_185", "Verify Financial Insights and Analytics - Test Case Scenario version 185"),
    ("TC_186_INSIGHTS_186", "Verify Financial Insights and Analytics - Test Case Scenario version 186"),
    ("TC_187_INSIGHTS_187", "Verify Financial Insights and Analytics - Test Case Scenario version 187"),
    ("TC_188_INSIGHTS_188", "Verify Financial Insights and Analytics - Test Case Scenario version 188"),
    ("TC_189_INSIGHTS_189", "Verify Financial Insights and Analytics - Test Case Scenario version 189"),
    ("TC_190_INSIGHTS_190", "Verify Financial Insights and Analytics - Test Case Scenario version 190"),
    ("TC_191_INSIGHTS_191", "Verify Financial Insights and Analytics - Test Case Scenario version 191"),
    ("TC_192_INSIGHTS_192", "Verify Financial Insights and Analytics - Test Case Scenario version 192"),
    ("TC_193_INSIGHTS_193", "Verify Financial Insights and Analytics - Test Case Scenario version 193"),
    ("TC_194_INSIGHTS_194", "Verify Financial Insights and Analytics - Test Case Scenario version 194"),
    ("TC_195_INSIGHTS_195", "Verify Financial Insights and Analytics - Test Case Scenario version 195"),
    ("TC_196_SETTINGS_196", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 196"),
    ("TC_197_SETTINGS_197", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 197"),
    ("TC_198_SETTINGS_198", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 198"),
    ("TC_199_SETTINGS_199", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 199"),
    ("TC_200_SETTINGS_200", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 200"),
    ("TC_201_SETTINGS_201", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 201"),
    ("TC_202_SETTINGS_202", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 202"),
    ("TC_203_SETTINGS_203", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 203"),
    ("TC_204_SETTINGS_204", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 204"),
    ("TC_205_SETTINGS_205", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 205"),
    ("TC_206_SETTINGS_206", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 206"),
    ("TC_207_SETTINGS_207", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 207"),
    ("TC_208_SETTINGS_208", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 208"),
    ("TC_209_SETTINGS_209", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 209"),
    ("TC_210_SETTINGS_210", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 210"),
    ("TC_211_SETTINGS_211", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 211"),
    ("TC_212_SETTINGS_212", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 212"),
    ("TC_213_SETTINGS_213", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 213"),
    ("TC_214_SETTINGS_214", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 214"),
    ("TC_215_SETTINGS_215", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 215"),
    ("TC_216_SETTINGS_216", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 216"),
    ("TC_217_SETTINGS_217", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 217"),
    ("TC_218_SETTINGS_218", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 218"),
    ("TC_219_SETTINGS_219", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 219"),
    ("TC_220_SETTINGS_220", "Verify Advanced Settings and Security Configuration - Test Case Scenario version 220"),
    ("TC_221_CURRENCY_221", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 221"),
    ("TC_222_CURRENCY_222", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 222"),
    ("TC_223_CURRENCY_223", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 223"),
    ("TC_224_CURRENCY_224", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 224"),
    ("TC_225_CURRENCY_225", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 225"),
    ("TC_226_CURRENCY_226", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 226"),
    ("TC_227_CURRENCY_227", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 227"),
    ("TC_228_CURRENCY_228", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 228"),
    ("TC_229_CURRENCY_229", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 229"),
    ("TC_230_CURRENCY_230", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 230"),
    ("TC_231_CURRENCY_231", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 231"),
    ("TC_232_CURRENCY_232", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 232"),
    ("TC_233_CURRENCY_233", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 233"),
    ("TC_234_CURRENCY_234", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 234"),
    ("TC_235_CURRENCY_235", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 235"),
    ("TC_236_CURRENCY_236", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 236"),
    ("TC_237_CURRENCY_237", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 237"),
    ("TC_238_CURRENCY_238", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 238"),
    ("TC_239_CURRENCY_239", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 239"),
    ("TC_240_CURRENCY_240", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 240"),
    ("TC_241_CURRENCY_241", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 241"),
    ("TC_242_CURRENCY_242", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 242"),
    ("TC_243_CURRENCY_243", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 243"),
    ("TC_244_CURRENCY_244", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 244"),
    ("TC_245_CURRENCY_245", "Verify Multi-Currency and Exchange Rate Handling - Test Case Scenario version 245"),
    ("TC_246_OFFLINE_246", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 246"),
    ("TC_247_OFFLINE_247", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 247"),
    ("TC_248_OFFLINE_248", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 248"),
    ("TC_249_OFFLINE_249", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 249"),
    ("TC_250_OFFLINE_250", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 250"),
    ("TC_251_OFFLINE_251", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 251"),
    ("TC_252_OFFLINE_252", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 252"),
    ("TC_253_OFFLINE_253", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 253"),
    ("TC_254_OFFLINE_254", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 254"),
    ("TC_255_OFFLINE_255", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 255"),
    ("TC_256_OFFLINE_256", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 256"),
    ("TC_257_OFFLINE_257", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 257"),
    ("TC_258_OFFLINE_258", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 258"),
    ("TC_259_OFFLINE_259", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 259"),
    ("TC_260_OFFLINE_260", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 260"),
    ("TC_261_OFFLINE_261", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 261"),
    ("TC_262_OFFLINE_262", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 262"),
    ("TC_263_OFFLINE_263", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 263"),
    ("TC_264_OFFLINE_264", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 264"),
    ("TC_265_OFFLINE_265", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 265"),
    ("TC_266_OFFLINE_266", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 266"),
    ("TC_267_OFFLINE_267", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 267"),
    ("TC_268_OFFLINE_268", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 268"),
    ("TC_269_OFFLINE_269", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 269"),
    ("TC_270_OFFLINE_270", "Verify Offline Caching and Local Synchronization - Test Case Scenario version 270"),
    ("TC_271_EXPORT_271", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 271"),
    ("TC_272_EXPORT_272", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 272"),
    ("TC_273_EXPORT_273", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 273"),
    ("TC_274_EXPORT_274", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 274"),
    ("TC_275_EXPORT_275", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 275"),
    ("TC_276_EXPORT_276", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 276"),
    ("TC_277_EXPORT_277", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 277"),
    ("TC_278_EXPORT_278", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 278"),
    ("TC_279_EXPORT_279", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 279"),
    ("TC_280_EXPORT_280", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 280"),
    ("TC_281_EXPORT_281", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 281"),
    ("TC_282_EXPORT_282", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 282"),
    ("TC_283_EXPORT_283", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 283"),
    ("TC_284_EXPORT_284", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 284"),
    ("TC_285_EXPORT_285", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 285"),
    ("TC_286_EXPORT_286", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 286"),
    ("TC_287_EXPORT_287", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 287"),
    ("TC_288_EXPORT_288", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 288"),
    ("TC_289_EXPORT_289", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 289"),
    ("TC_290_EXPORT_290", "Verify Data Export, CSV and Excel Backup Verification - Test Case Scenario version 290"),
    ("TC_291_THEME_291", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 291"),
    ("TC_292_THEME_292", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 292"),
    ("TC_293_THEME_293", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 293"),
    ("TC_294_THEME_294", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 294"),
    ("TC_295_THEME_295", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 295"),
    ("TC_296_THEME_296", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 296"),
    ("TC_297_THEME_297", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 297"),
    ("TC_298_THEME_298", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 298"),
    ("TC_299_THEME_299", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 299"),
    ("TC_300_THEME_300", "Verify Theme Accessibility and Interface Customization - Test Case Scenario version 300"),
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


