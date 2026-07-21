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
    if monthly_income <= 0 and monthly_expense <= 0 and monthly_debt <= 0 and liquid_assets <= 0 and total_liabilities <= 0:
        return 0

    score = 0

    if monthly_income > 0:
        expense_ratio = (monthly_expense / monthly_income) * 100
        debt_ratio = (monthly_debt / monthly_income) * 100
        score += min(expense_ratio * 0.5, 35)
        score += min(debt_ratio * 0.6, 30)

        surplus = monthly_income - monthly_expense - monthly_debt
        if surplus < 0:
            score += 25
    else:
        if monthly_expense > 0 or monthly_debt > 0 or total_liabilities > 0:
            score += 70

    if monthly_expense > 0:
        runway = liquid_assets / monthly_expense
        if runway < 1:
            score += 20
        elif runway < 3:
            score += 10
        elif runway >= 6:
            score -= 15

    if liquid_assets > 0:
        asset_bonus = min((liquid_assets / 100000) * 10, 20)
        score -= asset_bonus

    if total_liabilities > 0:
        debt_penalty = min((total_liabilities / 100000) * 8, 20)
        score += debt_penalty

    return max(0, min(100, round(score)))


def risk_level(score: int):
    if score == 0:
        return "Neutral"
    elif score < 30:
        return "Low"
    elif score < 60:
        return "Moderate"
    elif score < 85:
        return "High"
    return "Critical"


def build_alerts(expense_ratio, debt_ratio, runway, monthly_surplus):
    alerts = []

    if monthly_surplus < 0:
        alerts.append("🔥 Deficit Warning: Monthly expenses exceed total income.")
    if expense_ratio > 40:
        alerts.append("⚠️ High Expense Ratio: Spending over 40% of income.")
    if debt_ratio > 35:
        alerts.append("🚨 Heavy Debt Burden: Over 35% of income goes to debt EMI.")
    if runway < 3 and runway > 0:
        alerts.append("🛡️ Low Savings Buffer: Less than 3 months of emergency runway.")

    if not alerts:
        alerts.append("✅ Healthy Financial Status: Cash flow and risk levels are well balanced.")

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
            if m_score == 0 and score > 0:
                deltas = [-10, -6, -4, -2, 2, 0]
                m_score = max(0, min(100, score + deltas[5 - offset]))
            trend_scores.append(m_score)

        recent_activity = []
        try:
            cursor.execute(
                """
                (SELECT id, 'income' AS type, category AS title, notes, amount, tx_date AS date FROM financial_transactions WHERE user_id = %s AND tx_type = 'income')
                UNION ALL
                (SELECT id, 'expense' AS type, category AS title, notes, -amount AS amount, tx_date AS date FROM financial_transactions WHERE user_id = %s AND tx_type = 'expense')
                UNION ALL
                (SELECT id, 'debt' AS type, liability_name AS title, CONCAT('EMI: ₹', CAST(monthly_payment AS CHAR)) AS notes, -outstanding_amount AS amount, created_at AS date FROM financial_liabilities WHERE user_id = %s)
                UNION ALL
                (SELECT id, 'asset' AS type, asset_name AS title, asset_type AS notes, amount, created_at AS date FROM financial_assets WHERE user_id = %s)
                ORDER BY date DESC LIMIT 20
                """,
                (user_id, user_id, user_id, user_id)
            )
            recent_rows = cursor.fetchall()
            for r in recent_rows:
                tx_type = r['type']
                amt = float(r['amount'])
                if tx_type == 'income':
                    icon, color, badge = 'fa-arrow-down', '#16a34a', 'Income'
                elif tx_type == 'expense':
                    icon, color, badge = 'fa-arrow-up', '#ef4444', 'Expense'
                elif tx_type == 'debt':
                    icon, color, badge = 'fa-credit-card', '#8250df', 'Liability'
                else:
                    icon, color, badge = 'fa-vault', '#0969da', 'Asset'

                recent_activity.append({
                    "id": str(r['id']),
                    "type": tx_type,
                    "title": r['title'] or 'Transaction',
                    "notes": r['notes'] or '',
                    "amount": amt,
                    "txDate": str(r['date'])[:10] if r['date'] else '',
                    "icon": icon,
                    "color": color,
                    "badge": badge,
                    "rawType": tx_type,
                    "index": r['id']
                })
        except Exception as err:
            print(f"[Warning] Failed to fetch recent_activity: {err}")

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
            "recent_activity": recent_activity,
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
        has_data = monthly_income > 0 or monthly_expense > 0 or total_assets > 0 or total_liabilities > 0
        base_score = current_score if has_data else 0
        current_level = risk_level(base_score)

        projections = []
        proj_scores = []

        for days in [30, 60, 90]:
            months = days / 30.0

            projected_income = monthly_income
            projected_expense = monthly_expense * (1 + 0.04 * months)
            projected_debt = monthly_debt
            projected_surplus = projected_income - projected_expense - projected_debt

            projected_assets = max(0, total_assets + (current_surplus * months))

            if has_data:
                calc_s = calculate_risk_score(
                    monthly_income=projected_income,
                    monthly_expense=projected_expense,
                    monthly_debt=projected_debt,
                    liquid_assets=projected_assets,
                    total_liabilities=total_liabilities
                )
                projected_score = max(10, min(100, calc_s if calc_s > 0 else round(base_score + (months * 2))))
            else:
                projected_score = 0

            proj_level = risk_level(projected_score)
            proj_scores.append(float(projected_score))

            if projected_score >= 75:
                message = "High distress risk if current spending continues."
            elif projected_score >= 50:
                message = "Risk is rising. Control spending and debt."
            elif has_data:
                message = "Current financial trend looks manageable."
            else:
                message = "Add transactions to calculate 30/60/90-day forecast."

            projections.append({
                "days": days,
                "risk_score": projected_score,
                "risk_level": proj_level,
                "projected_savings": round(projected_assets, 2),
                "projected_surplus": round(projected_surplus, 2),
                "message": message
            })

        chart_scores = [float(base_score)] + proj_scores

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
        target_emergency_fund = max(10000.0, monthly_expense * 6.0)
        emergency_progress = min(100, round((total_assets / target_emergency_fund) * 100)) if target_emergency_fund > 0 else 0

        recommendations.append({
            "title": "Emergency Fund Reserve",
            "description": f"Your current savings cover {savings_runway} months of expenses. Target emergency fund: ₹{int(target_emergency_fund):,}.",
            "impact": emergency_progress
        })

        if expense_ratio > 40:
            recommendations.append({
                "title": "Reduce Discretionary Spending",
                "description": f"Expense ratio is {expense_ratio}%. Cut non-essential spending to lower it below 40%.",
                "impact": min(100, round(expense_ratio))
            })

        if debt_ratio > 25:
            recommendations.append({
                "title": "Accelerated Debt Payoff",
                "description": f"Debt ratio is {debt_ratio}%. Allocate surplus toward principal debt reduction.",
                "impact": min(100, round(debt_ratio * 1.5))
            })

        if monthly_surplus > 0:
            rec_invest = round(monthly_surplus * 0.6)
            recommendations.append({
                "title": "Wealth Building & SIP Investment",
                "description": f"Invest ₹{int(rec_invest):,} monthly in low-cost index funds or mutual funds.",
                "impact": min(100, round((monthly_surplus / (monthly_income if monthly_income > 0 else 1)) * 100))
            })

        priority_actions = []
        if monthly_surplus < 0:
            priority_actions.append("🔥 Stop non-essential spending to eliminate monthly deficit.")
        if debt_ratio > 35:
            priority_actions.append("🚨 Pay off high-interest debt using Debt Avalanche method.")
        if savings_runway < 3:
            priority_actions.append("🛡️ Allocate surplus to build 3 to 6 months of emergency reserves.")
        if expense_ratio > 40:
            priority_actions.append("⚠️ Reduce monthly subscriptions and eating out.")
        if monthly_surplus > 0:
            priority_actions.append(f"💡 Automate monthly SIP investment of ₹{int(round(monthly_surplus * 0.5)):,}.")

        if not priority_actions:
            priority_actions.append("✅ Continue tracking monthly cash flow to maintain financial health.")
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