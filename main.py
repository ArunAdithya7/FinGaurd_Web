from fastapi import FastAPI, HTTPException, Header,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import mysql.connector
from datetime import date, datetime
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
import calendar

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your Flutter app origin later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- CONFIG --------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root123",
    "database": "finguard_db"
}

JWT_SECRET = "your_secret_key_here"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(user_id: int, email: str):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# -------------------- SCHEMAS --------------------
class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    mobile: str
    password: str


class LoginRequest(BaseModel):
    identifier: str   # email or mobile
    password: str


# -------------------- SIGNUP --------------------
@app.post("/auth/signup")
def signup(data: SignupRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # check email/mobile already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s OR mobile = %s",
            (data.email, data.mobile)
        )
        existing = cursor.fetchone()

        if existing:
            raise HTTPException(status_code=400, detail="Email or mobile already registered")

        hashed = hash_password(data.password)

        cursor.execute(
            """
            INSERT INTO users (full_name, email, mobile, password_hash)
            VALUES (%s, %s, %s, %s)
            """,
            (data.full_name, data.email, data.mobile, hashed)
        )
        conn.commit()

        return {
            "success": True,
            "message": "Signup successful"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# -------------------- LOGIN --------------------
@app.post("/auth/login")
def login(data: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, full_name, email, mobile, password_hash
            FROM users
            WHERE email = %s OR mobile = %s
            """,
            (data.identifier, data.identifier)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token(user["id"], user["email"])

        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "mobile": user["mobile"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


def get_current_user_id(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token")

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["user_id"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def fetch_one_value(cursor, query, params):
    cursor.execute(query, params)
    row = cursor.fetchone()
    if row and row["total"] is not None:
        return float(row["total"])
    return 0.0


def month_bounds(year: int, month: int):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


def calculate_risk_score(monthly_income, monthly_expense, monthly_debt, liquid_assets, total_liabilities):
    if monthly_income <= 0:
        return 100

    expense_ratio = (monthly_expense / monthly_income) * 100 if monthly_income else 0
    debt_ratio = (monthly_debt / monthly_income) * 100 if monthly_income else 0
    runway = (liquid_assets / monthly_expense) if monthly_expense > 0 else 12

    score = 0
    score += min(expense_ratio * 0.45, 35)
    score += min(debt_ratio * 0.55, 30)

    if runway < 1:
        score += 25
    elif runway < 3:
        score += 12

    if (monthly_income - monthly_expense - monthly_debt) < 0:
        score += 20

    if total_liabilities > liquid_assets * 2:
        score += 10

    return max(0, min(100, round(score)))


def risk_level(score: int):
    if score < 25:
        return "Low"
    elif score < 50:
        return "Moderate"
    elif score < 75:
        return "High"
    return "Critical"


def build_alerts(expense_ratio, debt_ratio, runway, monthly_surplus):
    alerts = []

    if expense_ratio > 40:
        alerts.append("Expense ratio is increasing.")
    if debt_ratio > 35:
        alerts.append("Debt burden is high.")
    if runway < 1:
        alerts.append("Savings runway is less than 1 month.")
    if monthly_surplus < 0:
        alerts.append("Monthly surplus is negative.")

    if not alerts:
        alerts.append("Your financial health looks stable.")

    return alerts


class TransactionCreate(BaseModel):
    category: str
    amount: float
    notes: Optional[str] = None
    tx_date: Optional[date] = None


class AssetCreate(BaseModel):
    asset_name: str
    asset_type: str
    amount: float


class LiabilityCreate(BaseModel):
    liability_name: str
    outstanding_amount: float
    monthly_payment: float
    interest_rate: Optional[float] = 0.0


@app.post("/financial/income")
def add_income(data: TransactionCreate, user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        tx_date = data.tx_date or date.today()
        cursor.execute(
            """
            INSERT INTO financial_transactions (user_id, tx_type, category, amount, notes, tx_date)
            VALUES (%s, 'income', %s, %s, %s, %s)
            """,
            (user_id, data.category, data.amount, data.notes, tx_date)
        )
        conn.commit()
        return {"success": True, "message": "Income added successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.post("/financial/expense")
def add_expense(data: TransactionCreate, user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        tx_date = data.tx_date or date.today()
        cursor.execute(
            """
            INSERT INTO financial_transactions (user_id, tx_type, category, amount, notes, tx_date)
            VALUES (%s, 'expense', %s, %s, %s, %s)
            """,
            (user_id, data.category, data.amount, data.notes, tx_date)
        )
        conn.commit()
        return {"success": True, "message": "Expense added successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.post("/financial/asset")
def add_asset(data: AssetCreate, user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO financial_assets (user_id, asset_name, asset_type, amount)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, data.asset_name, data.asset_type, data.amount)
        )
        conn.commit()
        return {"success": True, "message": "Asset added successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.post("/financial/liability")
def add_liability(data: LiabilityCreate, user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO financial_liabilities
            (user_id, liability_name, outstanding_amount, monthly_payment, interest_rate)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, data.liability_name, data.outstanding_amount, data.monthly_payment, data.interest_rate)
        )
        conn.commit()
        return {"success": True, "message": "Liability added successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.get("/dashboard/summary")
def dashboard_summary(user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        today = date.today()
        current_year = today.year
        current_month = today.month
        month_start, month_end = month_bounds(current_year, current_month)

        # current month income / expense
        monthly_income = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_transactions
            WHERE user_id = %s AND tx_type = 'income'
            AND tx_date >= %s AND tx_date < %s
            """,
            (user_id, month_start, month_end)
        )

        monthly_expense = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_transactions
            WHERE user_id = %s AND tx_type = 'expense'
            AND tx_date >= %s AND tx_date < %s
            """,
            (user_id, month_start, month_end)
        )

        # assets and liabilities
        total_assets = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_assets
            WHERE user_id = %s
            """,
            (user_id,)
        )

        total_liabilities = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(outstanding_amount), 0) AS total
            FROM financial_liabilities
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )

        monthly_debt = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(monthly_payment), 0) AS total
            FROM financial_liabilities
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )

        liquid_assets = total_assets
        expense_ratio = round((monthly_expense / monthly_income) * 100, 1) if monthly_income > 0 else 0
        debt_ratio = round((monthly_debt / monthly_income) * 100, 1) if monthly_income > 0 else 0
        savings_runway = round(liquid_assets / monthly_expense, 1) if monthly_expense > 0 else 0
        monthly_surplus = round(monthly_income - monthly_expense - monthly_debt, 2)

        score = calculate_risk_score(
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            monthly_debt=monthly_debt,
            liquid_assets=liquid_assets,
            total_liabilities=total_liabilities
        )

        level = risk_level(score)
        alerts = build_alerts(expense_ratio, debt_ratio, savings_runway, monthly_surplus)

        # trend for last 6 months
        trend_labels = []
        trend_scores = []

        for offset in range(5, -1, -1):
            month_index = current_month - offset
            year = current_year

            while month_index <= 0:
                month_index += 12
                year -= 1

            start_date, end_date = month_bounds(year, month_index)
            label = calendar.month_abbr[month_index]
            trend_labels.append(label)

            m_income = fetch_one_value(
                cursor,
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM financial_transactions
                WHERE user_id = %s AND tx_type = 'income'
                AND tx_date >= %s AND tx_date < %s
                """,
                (user_id, start_date, end_date)
            )

            m_expense = fetch_one_value(
                cursor,
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM financial_transactions
                WHERE user_id = %s AND tx_type = 'expense'
                AND tx_date >= %s AND tx_date < %s
                """,
                (user_id, start_date, end_date)
            )

            m_debt = monthly_debt
            m_score = calculate_risk_score(m_income, m_expense, m_debt, liquid_assets, total_liabilities)
            trend_scores.append(m_score)

        return {
            "success": True,
            "risk_score": score,
            "risk_level": level,
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "monthly_income": round(monthly_income, 2),
            "monthly_expense": round(monthly_expense, 2),
            "monthly_debt": round(monthly_debt, 2),
            "debt_ratio": debt_ratio,
            "savings_runway": savings_runway,
            "expense_ratio": expense_ratio,
            "monthly_surplus": monthly_surplus,
            "alerts": alerts,
            "trend_labels": trend_labels,
            "trend_scores": trend_scores
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/risk/analysis")
def risk_analysis(user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        today = date.today()
        current_year = today.year
        current_month = today.month
        month_start, month_end = month_bounds(current_year, current_month)

        monthly_income = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_transactions
            WHERE user_id = %s AND tx_type = 'income'
            AND tx_date >= %s AND tx_date < %s
            """,
            (user_id, month_start, month_end)
        )

        monthly_expense = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_transactions
            WHERE user_id = %s AND tx_type = 'expense'
            AND tx_date >= %s AND tx_date < %s
            """,
            (user_id, month_start, month_end)
        )

        total_assets = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_assets
            WHERE user_id = %s
            """,
            (user_id,)
        )

        total_liabilities = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(outstanding_amount), 0) AS total
            FROM financial_liabilities
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )

        monthly_debt = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(monthly_payment), 0) AS total
            FROM financial_liabilities
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )

        expense_ratio = round((monthly_expense / monthly_income) * 100, 1) if monthly_income > 0 else 0
        debt_ratio = round((monthly_debt / monthly_income) * 100, 1) if monthly_income > 0 else 0
        savings_runway = round(total_assets / monthly_expense, 1) if monthly_expense > 0 else 0
        monthly_surplus = round(monthly_income - monthly_expense - monthly_debt, 2)

        score = calculate_risk_score(
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            monthly_debt=monthly_debt,
            liquid_assets=total_assets,
            total_liabilities=total_liabilities
        )

        level = risk_level(score)

        factors = [
            {
                "title": "Expense Ratio",
                "description": "How much of your income is spent every month.",
                "impact": expense_ratio
            },
            {
                "title": "Debt Ratio",
                "description": "How much of your income goes to debt payments.",
                "impact": debt_ratio
            },
            {
                "title": "Savings Runway",
                "description": "How many months your savings can cover expenses.",
                "impact": 100 - min(savings_runway * 25, 100)
            },
            {
                "title": "Monthly Surplus",
                "description": "Income left after expenses and debt payments.",
                "impact": 100 if monthly_surplus < 0 else 25
            }
        ]

        suggestions = []

        if expense_ratio > 40:
            suggestions.append("Reduce non-essential spending to lower your expense ratio.")
        if debt_ratio > 35:
            suggestions.append("Try to reduce debt payments or refinance high-interest debt.")
        if savings_runway < 1:
            suggestions.append("Increase emergency savings immediately.")
        if monthly_surplus < 0:
            suggestions.append("Your outflow is higher than income. Review your budget now.")
        if not suggestions:
            suggestions.append("Your current financial pattern looks stable. Keep tracking monthly.")

        return {
            "success": True,
            "risk_score": score,
            "risk_level": level,
            "expense_ratio": expense_ratio,
            "debt_ratio": debt_ratio,
            "savings_runway": savings_runway,
            "monthly_surplus": monthly_surplus,
            "factors": factors,
            "suggestions": suggestions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/forecast/summary")
def forecast_summary(user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        today = date.today()
        current_year = today.year
        current_month = today.month
        month_start, month_end = month_bounds(current_year, current_month)

        monthly_income = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_transactions
            WHERE user_id = %s AND tx_type = 'income'
            AND tx_date >= %s AND tx_date < %s
            """,
            (user_id, month_start, month_end)
        )

        monthly_expense = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_transactions
            WHERE user_id = %s AND tx_type = 'expense'
            AND tx_date >= %s AND tx_date < %s
            """,
            (user_id, month_start, month_end)
        )

        total_assets = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_assets
            WHERE user_id = %s
            """,
            (user_id,)
        )

        total_liabilities = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(outstanding_amount), 0) AS total
            FROM financial_liabilities
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )

        monthly_debt = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(monthly_payment), 0) AS total
            FROM financial_liabilities
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )

        current_surplus = monthly_income - monthly_expense - monthly_debt
        current_score = calculate_risk_score(
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            monthly_debt=monthly_debt,
            liquid_assets=total_assets,
            total_liabilities=total_liabilities
        )
        current_level = risk_level(current_score)

        projections = []
        chart_scores = [float(max(0, current_score - 8)), float(max(0, current_score - 4)), float(current_score), float(min(100, current_score + 6))]

        for days in [30, 60, 90]:
            months = days / 30.0

            projected_income = monthly_income
            projected_expense = monthly_expense * (1 + 0.06 * months)
            projected_debt = monthly_debt
            projected_surplus = projected_income - projected_expense - projected_debt

            projected_assets = total_assets + (current_surplus * months)
            if projected_assets < 0:
                projected_assets = 0

            projected_score = calculate_risk_score(
                monthly_income=projected_income,
                monthly_expense=projected_expense,
                monthly_debt=projected_debt,
                liquid_assets=projected_assets,
                total_liabilities=total_liabilities
            )

            if projected_score < 25:
                proj_level = "Low"
            elif projected_score < 50:
                proj_level = "Moderate"
            elif projected_score < 75:
                proj_level = "High"
            else:
                proj_level = "Critical"

            if projected_score >= 75:
                message = "High distress risk if current spending continues."
            elif projected_score >= 50:
                message = "Risk is rising. Control spending and debt."
            else:
                message = "Current trend looks manageable."

            projections.append({
                "days": days,
                "risk_score": projected_score,
                "risk_level": proj_level,
                "projected_savings": round(projected_assets, 2),
                "projected_surplus": round(projected_surplus, 2),
                "message": message
            })

        recommendations = []
        if monthly_expense > monthly_income * 0.4:
            recommendations.append("Reduce unnecessary expenses to keep your expense ratio under control.")
        if monthly_debt > monthly_income * 0.35:
            recommendations.append("Try to lower debt payments or pay off high-interest debt first.")
        if total_assets < monthly_expense:
            recommendations.append("Build an emergency fund to cover at least one month of expenses.")
        if current_surplus < 0:
            recommendations.append("Your income is not covering total outflow. Review your budget now.")
        if not recommendations:
            recommendations.append("Your current forecast looks stable. Keep monitoring monthly.")

        return {
            "success": True,
            "current_risk_score": current_score,
            "current_risk_level": current_level,
            "projections": projections,
            "chart_scores": chart_scores,
            "recommendations": recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.get("/recommendations/summary")
def recommendations_summary(user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        today = date.today()
        current_year = today.year
        current_month = today.month
        month_start, month_end = month_bounds(current_year, current_month)

        monthly_income = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_transactions
            WHERE user_id = %s AND tx_type = 'income'
            AND tx_date >= %s AND tx_date < %s
            """,
            (user_id, month_start, month_end)
        )

        monthly_expense = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_transactions
            WHERE user_id = %s AND tx_type = 'expense'
            AND tx_date >= %s AND tx_date < %s
            """,
            (user_id, month_start, month_end)
        )

        total_assets = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM financial_assets
            WHERE user_id = %s
            """,
            (user_id,)
        )

        total_liabilities = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(outstanding_amount), 0) AS total
            FROM financial_liabilities
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )

        monthly_debt = fetch_one_value(
            cursor,
            """
            SELECT COALESCE(SUM(monthly_payment), 0) AS total
            FROM financial_liabilities
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )

        expense_ratio = round((monthly_expense / monthly_income) * 100, 1) if monthly_income > 0 else 0
        debt_ratio = round((monthly_debt / monthly_income) * 100, 1) if monthly_income > 0 else 0
        savings_runway = round(total_assets / monthly_expense, 1) if monthly_expense > 0 else 0
        monthly_surplus = round(monthly_income - monthly_expense - monthly_debt, 2)

        score = calculate_risk_score(
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            monthly_debt=monthly_debt,
            liquid_assets=total_assets,
            total_liabilities=total_liabilities
        )

        level = risk_level(score)

        recommendations = []

        if expense_ratio > 40:
            recommendations.append({
                "title": "Reduce spending",
                "description": "Your expense ratio is too high. Cut non-essential spending.",
                "impact": expense_ratio
            })

        if debt_ratio > 35:
            recommendations.append({
                "title": "Lower debt burden",
                "description": "Debt payments are heavy. Try paying high-interest debt first.",
                "impact": debt_ratio
            })

        if savings_runway < 1:
            recommendations.append({
                "title": "Build emergency fund",
                "description": "Your savings runway is low. Save for at least 1 to 3 months of expenses.",
                "impact": 100 - min(savings_runway * 30, 100)
            })

        if monthly_surplus < 0:
            recommendations.append({
                "title": "Fix negative cash flow",
                "description": "You are spending more than you earn. Review your budget immediately.",
                "impact": 100
            })

        if total_assets < monthly_expense * 2:
            recommendations.append({
                "title": "Increase savings",
                "description": "Your liquid savings are low compared to monthly spending.",
                "impact": 70
            })

        if not recommendations:
            recommendations.append({
                "title": "Keep tracking monthly",
                "description": "Your current financial position looks stable. Continue monitoring regularly.",
                "impact": 10
            })

        priority_actions = []
        if monthly_surplus < 0:
            priority_actions.append("Stop unnecessary expenses immediately.")
        if debt_ratio > 35:
            priority_actions.append("Pay high-interest debt first.")
        if savings_runway < 1:
            priority_actions.append("Increase emergency savings this month.")
        if expense_ratio > 40:
            priority_actions.append("Reduce discretionary spending.")

        if not priority_actions:
            priority_actions.append("Maintain your current spending discipline.")

        return {
            "success": True,
            "risk_score": score,
            "risk_level": level,
            "recommendations": recommendations,
            "priority_actions": priority_actions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

class ProfileUpdateRequest(BaseModel):
    full_name: str
    mobile: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@app.get("/profile/me")
def get_profile(user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, full_name, email, mobile, created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "success": True,
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "joined_at": user["created_at"].strftime("%Y-%m-%d") if user["created_at"] else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/profile/update")
def update_profile(
    data: ProfileUpdateRequest,
    user_id: int = Depends(get_current_user_id)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            UPDATE users
            SET full_name = %s, mobile = %s
            WHERE id = %s
            """,
            (data.full_name, data.mobile, user_id)
        )
        conn.commit()

        return {
            "success": True,
            "message": "Profile updated successfully"
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/profile/change-password")
def change_password(
    data: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT password_hash FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(data.current_password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        new_hash = hash_password(data.new_password)

        cursor.execute(
            """
            UPDATE users
            SET password_hash = %s
            WHERE id = %s
            """,
            (new_hash, user_id)
        )
        conn.commit()

        return {
            "success": True,
            "message": "Password changed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()