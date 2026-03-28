import streamlit as st
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------- FIREBASE CONFIG ----------------
API_KEY = st.secrets["FIREBASE_API_KEY"]

def firebase_signup(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        return requests.post(url, json=payload, timeout=10).json()
    except requests.exceptions.RequestException:
        return {"error": {"message": "Network error: Unable to connect to Firebase"}}

def firebase_login(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        return requests.post(url, json=payload, timeout=10).json()
    except requests.exceptions.RequestException:
        return {"error": {"message": "Network error: Unable to connect to Firebase"}}

# ---------------- EMAIL ALERT CONFIG ----------------
ALERT_EMAIL_ENABLED = (
    "ALERT_EMAIL_ADDRESS" in st.secrets
    and "ALERT_EMAIL_PASSWORD" in st.secrets
)

ALERT_EMAIL_ADDRESS = st.secrets["ALERT_EMAIL_ADDRESS"] if ALERT_EMAIL_ENABLED else ""
ALERT_EMAIL_PASSWORD = st.secrets["ALERT_EMAIL_PASSWORD"] if ALERT_EMAIL_ENABLED else ""

def send_email_alert(to_email, subject, body):
    if not ALERT_EMAIL_ENABLED:
        st.warning("Email alerts are not configured in secrets.toml")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = ALERT_EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
        server.starttls()
        server.login(ALERT_EMAIL_ADDRESS, ALERT_EMAIL_PASSWORD)
        server.sendmail(ALERT_EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email alert failed: {e}")
        return False

def create_alert_message(user_email, summary):
    dashboard_link = "http://localhost:8501"

    body = f"""
Hello,

This is an alert from your Crypto Investment Manager.

User: {user_email}

Portfolio Summary:
- Total Invested: ₹{summary['invested']:.2f}
- Current Portfolio Value: ₹{summary['current']:.2f}
- Total Profit/Loss: ₹{summary['pnl']:.2f}
- Profit/Loss %: {summary['pnl_pct']:.2f}%
- Risk Score: {summary.get('risk_score', 0)}
- Risk Status: {summary.get('risk_status', 'N/A')}

Alerts:
"""

    if summary["alerts"]:
        for alert in summary["alerts"]:
            body += f"- {alert}\n"
    else:
        body += "- No critical alerts\n"

    body += f"""

Open Dashboard / Alert Link:
{dashboard_link}

Regards,
Crypto Investment Manager
"""
    return body

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Crypto Investment Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- THEME ----------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] { 
    font-family: 'Chakra Petch', sans-serif !important; 
    font-size: 18px !important;          
    font-weight: 500 !important;         
    line-height: 1.6 !important;
}

.block-container { 
    padding-top: 1.4rem; 
    padding-bottom: 2rem; 
}

.stApp { 
    background: linear-gradient(180deg, #021024, #052659, #5483B3); 
    color: white; 
}

header { 
    visibility: visible !important; 
    background: transparent !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

h1, h2, h3 { 
    font-weight: 900 !important; 
    letter-spacing: 1.2px; 
    margin-bottom: 12px !important; 
}
h1 { font-size: 62px !important; }
h2 { font-size: 40px !important; }
h3 { font-size: 28px !important; }

.main-title {
    font-size: 70px !important;
    font-weight: 950 !important;
    letter-spacing: 3px !important;
    margin: 0 0 10px 0;
    text-transform: uppercase;
    text-align: center;
}

.sub-title { 
    font-size: 20px !important;  
    opacity: 0.92; 
    margin-bottom: 18px; 
    text-align: center; 
    font-weight: 700 !important;
}

p, span, div, label, li { 
    font-size: 18px !important;
    font-weight: 500 !important;
}
.stMarkdown p, 
.stMarkdown span, 
.stMarkdown li { 
    font-size: 18px !important;
    font-weight: 500 !important;
}
.stCaption, small { 
    font-size: 16px !important;  
    font-weight: 500 !important;
    opacity: 0.88;
}

.card {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(18px);
    border-radius: 22px;
    padding: 26px;
    margin-top: 16px;
    margin-bottom: 22px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 10px 28px rgba(0,0,0,0.40);
    transition: all 0.25s ease;
}
.card:hover { 
    transform: translateY(-3px); 
}

.auth-wrap {
    max-width: 520px;
    margin: 0 auto;
    padding: 28px 26px 24px 26px;
    border-radius: 26px;
    background: linear-gradient(180deg, rgba(2,16,36,0.72), rgba(5,38,89,0.62));
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 18px 50px rgba(0,0,0,0.55);
    backdrop-filter: blur(18px);
}
.auth-title {
    font-size: 40px !important;
    font-weight: 900 !important;
    letter-spacing: 1.3px;
    text-align: center;
    margin: 6px 0 18px 0;
}

.auth-tabs{
    display:flex;
    width:420px;
    max-width:100%;
    margin: 10px auto 18px auto;
    padding:8px;
    border-radius:999px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.14);
    backdrop-filter: blur(14px);
}
.auth-tab-link{
    flex:1;
    text-decoration:none !important;
    text-align:center;
    padding:12px 10px;
    border-radius:999px;
    font-weight:800 !important;
    font-size: 18px !important;
    color: rgba(255,255,255,0.85) !important;
}
.auth-tab-link:hover{ 
    color:white !important; 
}
.auth-tab-link.active{
    background: linear-gradient(90deg, #0b3b7a, #5483B3);
    color: #ffffff !important;
    box-shadow: 0 10px 22px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.14);
}

.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stSlider label{
    font-size: 18px !important;
    font-weight: 800 !important;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox div,
textarea{
    font-size: 18px !important;
    font-weight: 500 !important;
    border-radius: 12px !important;
}

.auth-wrap .stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    color: white !important;
    padding: 12px 12px !important;
    font-size: 18px !important;
}

.stButton > button{
    font-size: 18px !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
}

.auth-wrap .stButton > button {
    width: 100% !important;
    min-width: unset !important;
    border-radius: 16px !important;
    padding: 12px 18px !important;
    font-weight: 800 !important;
    font-size: 20px !important;
    background: linear-gradient(90deg, #0b3b7a, #5483B3) !important;
    color: white !important;
    border: none !important;
    transition: 0.25s ease;
}
.auth-wrap .stButton > button:hover {
    background: #C1E8FF !important;
    color: #021024 !important;
    transform: scale(1.02);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #052659 0%,
        #0b3b7a 45%,
        #6FA3D6 100%
    ) !important;
    border-right: 1px solid rgba(255,255,255,0.12);
}
section[data-testid="stSidebar"] > div {
    background: transparent !important;
}
section[data-testid="stSidebar"] * {
    color: #EAF4FF !important;
    font-size: 18px !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-width: unset;
    background: linear-gradient(90deg, #0b3b7a, #7FB5E6) !important;
    color: white !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(90deg, #5483B3, #9CC8F0) !important;
    transform: scale(1.04);
}

[data-testid="metric-container"] {
    background: rgba(0,0,0,0.30);
    border-radius: 16px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.10);
}
[data-testid="stMetricLabel"]{
    font-size: 20px !important;
    font-weight: 800 !important;
}
[data-testid="stMetricValue"]{
    font-size: 34px !important;
    font-weight: 950 !important;
}

[data-testid="stDataFrame"] *{
    font-size: 16px !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "last_auto_alert_sent" not in st.session_state:
    st.session_state.last_auto_alert_sent = None

def set_page(page):
    st.session_state.menu = page

# ---------------- AUTH MODE NAV ----------------
mode = st.query_params.get("mode", None)
if mode in ["login", "signup"]:
    st.session_state.auth_mode = mode

# ---------------- AUTHENTICATION ----------------
if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>CRYPTO MANAGER</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Secure Login • Live Market Data • Risk & Reports</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.3, 1])

    with col2:
        st.markdown("<div class='auth-wrap'>", unsafe_allow_html=True)
        st.markdown("<div class='auth-title'>USER AUTHENTICATION</div>", unsafe_allow_html=True)

        active_login = "active" if st.session_state.auth_mode == "login" else ""
        active_signup = "active" if st.session_state.auth_mode == "signup" else ""

        st.markdown(f"""
        <div class="auth-tabs">
            <a class="auth-tab-link {active_login}" href="?mode=login">Login</a>
            <a class="auth-tab-link {active_signup}" href="?mode=signup">Signup</a>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email Address", key="auth_email")
        password = st.text_input("Password", type="password", key="auth_pass")

        if st.session_state.auth_mode == "signup":
            confirm_password = st.text_input("Confirm Password", type="password", key="auth_confirm")

            if st.button("Signup", key="do_signup"):
                if password != confirm_password:
                    st.error("Passwords do not match ❌")
                else:
                    result = firebase_signup(email, password)
                    if "idToken" in result:
                        st.success("Account created ✅ Now login!")
                        st.query_params["mode"] = "login"
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        error_msg = result.get("error", {}).get("message", "Signup failed")
                        st.error(error_msg)
        else:
            if st.button("Login", key="do_login"):
                result = firebase_login(email, password)
                if "idToken" in result:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.query_params.clear()
                    st.rerun()
                else:
                    error_msg = result.get("error", {}).get("message", "Invalid email or password")
                    st.error(error_msg)

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_email}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.query_params.clear()
        st.rerun()

    st.markdown("## Navigation")
    if st.button("Home"):
        set_page("Home")
    if st.button("Risk Checker"):
        set_page("Risk Checker")
    if st.button("Investment Mix"):
        set_page("Investment Mix")
    if st.button("Report Generator"):
        set_page("Report Generator")
    if st.button("Spreading Rule Setter"):
        set_page("Spreading Rule Setter")

menu = st.session_state.menu

# ---------------- LOGIC ----------------
def volatility_check(v):
    if v < 30:
        return "Low Volatility"
    elif v < 60:
        return "Medium Volatility"
    else:
        return "High Volatility"

def investment_check(a):
    if a < 10000:
        return "Low Investment"
    elif a < 50000:
        return "Normal Investment"
    else:
        return "High Investment"

def run_parallel_risk_checks(volatility, investment_amount):
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(volatility_check, volatility)
        f2 = executor.submit(investment_check, investment_amount)
        return f1.result(), f2.result()

@st.cache_data(ttl=60)
def get_crypto_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        data = requests.get(url, timeout=10).json()
        return {
            "price": data["market_data"]["current_price"]["inr"],
            "market_cap": data["market_data"]["market_cap"]["inr"],
            "change_24h": data["market_data"]["price_change_percentage_24h"]
        }
    except Exception:
        return {"price": 0.0, "market_cap": 0.0, "change_24h": 0.0}

@st.cache_data(ttl=60)
def get_price_chart(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "inr", "days": 7}
        data = requests.get(url, params=params, timeout=10).json()
        df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception:
        return pd.DataFrame(columns=["timestamp", "price"])

def compute_returns(series: pd.Series) -> pd.Series:
    return series.pct_change().dropna()

def predict_next_price_from_trend(price_df: pd.DataFrame):
    if price_df.empty or len(price_df) < 2:
        return {
            "trend": "Not enough data",
            "predicted_price": 0.0,
            "avg_return_pct": 0.0,
            "confidence": "Low",
            "return_vol_pct": 0.0
        }

    s = price_df["price"].astype(float)
    returns = compute_returns(s)

    if returns.empty:
        last_price = float(s.iloc[-1])
        return {
            "trend": "Not enough data",
            "predicted_price": last_price,
            "avg_return_pct": 0.0,
            "confidence": "Low",
            "return_vol_pct": 0.0
        }

    avg_ret = returns.mean()
    vol_ret = returns.std()
    last_price = float(s.iloc[-1])
    predicted_price = last_price * (1 + avg_ret)

    trend = "Uptrend 📈" if avg_ret > 0 else ("Downtrend 📉" if avg_ret < 0 else "Sideways ➖")
    vol_pct = float(vol_ret * 100)
    confidence = "High" if vol_pct < 1.0 else ("Medium" if vol_pct < 2.5 else "Low")

    return {
        "trend": trend,
        "predicted_price": predicted_price,
        "avg_return_pct": float(avg_ret * 100),
        "confidence": confidence,
        "return_vol_pct": vol_pct
    }

# ---------------- INVESTMENT MIX ----------------
def get_allocation_plan(risk_level: str):
    r = risk_level.lower()
    if "low" in r:
        return {"Bitcoin": 60, "Ethereum": 30, "Solana": 10}
    elif "medium" in r:
        return {"Bitcoin": 45, "Ethereum": 35, "Solana": 20}
    else:
        return {"Bitcoin": 30, "Ethereum": 30, "Solana": 40}

def build_allocation_table(total_investment: float, allocation_pct: dict):
    rows = []
    for coin, pct in allocation_pct.items():
        amount = (pct / 100) * total_investment
        rows.append({"Coin": coin, "Allocation %": pct, "Amount (₹)": round(amount, 2)})
    return pd.DataFrame(rows)

# ---------------- SPREADING RULE FUNCTIONS ----------------

def spreading_table(total_investment, allocation_pct):
    rows = []
    for coin, pct in allocation_pct.items():
        amount = (pct / 100) * total_investment
        rows.append({
            "Coin": coin,
            "Allocation %": pct,
            "Amount (₹)": round(amount, 2)
        })
    return pd.DataFrame(rows)


def apply_spreading_rules(base_alloc, scenario, risk_score, pnl_pct, predictions, max_cap):
    adjusted = base_alloc.copy()
    rules_applied = []

    # Market scenario
    if scenario == "Bull Market":
        adjusted["Bitcoin"] += 5
        rules_applied.append("Bull Market → Increased Bitcoin")

    elif scenario == "Bear Market":
        adjusted["Solana"] -= 5
        rules_applied.append("Bear Market → Reduced Solana")

    # Risk rule
    if risk_score > 70:
        adjusted["Bitcoin"] += 5
        adjusted["Solana"] -= 5
        rules_applied.append("High Risk → Safer allocation")

    # Profit/Loss rule
    if pnl_pct < 0:
        adjusted["Ethereum"] += 5
        rules_applied.append("Loss → Increased Ethereum")

    # Prediction rule
    for coin, trend in predictions.items():
        if trend == "Uptrend":
            adjusted[coin] += 3
        elif trend == "Downtrend":
            adjusted[coin] -= 3

    # Cap rule
    for coin in adjusted:
        if adjusted[coin] > max_cap:
            adjusted[coin] = max_cap

    # Normalize to 100%
    total = sum(adjusted.values())
    adjusted = {k: round(v * 100 / total, 2) for k, v in adjusted.items()}

    return adjusted, rules_applied


# ---------------- HOME DASHBOARD HELPERS ----------------
COIN_MAP = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Solana": "solana",
}
def get_prices_inr(coin_ids):
    if not coin_ids:
        return {}
    try:
        ids = ",".join(sorted(set(coin_ids)))
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ids, "vs_currencies": "inr"}
        data = requests.get(url, params=params, timeout=10).json()
        out = {}
        for cid in coin_ids:
            out[cid] = float(data.get(cid, {}).get("inr", 0.0))
        return out
    except Exception:
        return {cid: 0.0 for cid in coin_ids}

@st.cache_data(ttl=300)
def get_coin_series_inr(coin_id, days=7):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "inr", "days": days}
        data = requests.get(url, params=params, timeout=10).json()
        prices = data.get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        if df.empty:
            return pd.DataFrame({"timestamp": pd.to_datetime([]), "price": []})
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["price"] = df["price"].astype(float)
        return df
    except Exception:
        return pd.DataFrame({"timestamp": pd.to_datetime([]), "price": []})

def risk_score_from_holdings(holdings):
    if not holdings:
        return 0, "No holdings"

    coin_ids = [h["coin_id"] for h in holdings]
    prices = get_prices_inr(coin_ids)

    vals = []
    for h in holdings:
        cur = prices.get(h["coin_id"], 0.0)
        vals.append(max(cur * float(h["qty"]), 0.0))
    total = sum(vals) if sum(vals) > 0 else 1.0
    weights = [v / total for v in vals]

    hhi = sum(w * w for w in weights)
    concentration_score = min(100, int(hhi * 100))

    vol_parts = []
    for i, h in enumerate(holdings):
        df = get_coin_series_inr(h["coin_id"], days=7)
        if df.empty or len(df) < 5:
            vol_parts.append(0.0)
            continue
        r = compute_returns(df["price"])
        vol_parts.append(float(r.std()) * weights[i])
    vol = sum(vol_parts)
    vol_score = min(100, int(vol * 4000))

    score = min(100, int(0.55 * concentration_score + 0.45 * vol_score))

    if score < 35:
        status = "Low Risk ✅"
    elif score < 70:
        status = "Medium Risk ⚠️"
    else:
        status = "High Risk 🚨"

    return score, status

def suggestion_for_coin(coin_id: str) -> str:
    df = get_coin_series_inr(coin_id, days=7)
    if df.empty or len(df) < 5:
        return "Hold"
    pred = predict_next_price_from_trend(df)
    cur = float(df["price"].iloc[-1])
    nxt = float(pred["predicted_price"])

    up_band = cur * 1.005
    down_band = cur * 0.995

    if pred["confidence"] in ["High", "Medium"]:
        if nxt > up_band:
            return "Buy"
        if nxt < down_band:
            return "Sell"
    return "Hold"

def build_portfolio_summary(holdings):
    if not holdings:
        return {
            "invested": 0.0,
            "current": 0.0,
            "pnl": 0.0,
            "pnl_pct": 0.0,
            "table": pd.DataFrame(columns=["Coin", "Quantity", "Avg Buy (₹)", "Current Price (₹)", "Value (₹)", "P/L (₹)", "Suggestion"]),
            "alerts": [],
            "trend": pd.DataFrame(columns=["timestamp", "portfolio_value"]),
        }

    coin_ids = [h["coin_id"] for h in holdings]
    prices = get_prices_inr(coin_ids)

    rows = []
    invested_total = 0.0
    current_total = 0.0

    for h in holdings:
        coin = h["coin"]
        cid = h["coin_id"]
        qty = float(h["qty"])
        avg_buy = float(h["avg_buy"])

        invested = qty * avg_buy
        current_price = float(prices.get(cid, 0.0))
        value = qty * current_price
        pnl = value - invested

        invested_total += invested
        current_total += value

        sug = suggestion_for_coin(cid)

        rows.append({
            "Coin": coin,
            "Quantity": round(qty, 6),
            "Avg Buy (₹)": round(avg_buy, 2),
            "Current Price (₹)": round(current_price, 2),
            "Value (₹)": round(value, 2),
            "P/L (₹)": round(pnl, 2),
            "Suggestion": sug
        })

    pnl_total = current_total - invested_total
    pnl_pct = (pnl_total / invested_total * 100) if invested_total > 0 else 0.0

    table = pd.DataFrame(rows).sort_values(by="Value (₹)", ascending=False)

    alerts = []
    if pnl_pct <= -10:
        alerts.append("🚨 Portfolio down more than 10% — consider reducing risk / rebalancing.")
    elif pnl_pct <= -5:
        alerts.append("⚠️ Portfolio down more than 5% — monitor closely.")

    risk_score, risk_status = risk_score_from_holdings(holdings)
    if risk_score >= 70:
        alerts.append("🚨 High Risk portfolio — reduce concentration or shift to safer allocation.")
    elif 35 <= risk_score < 70:
        alerts.append("⚠️ Medium Risk portfolio — keep diversification and monitor volatility.")

    trend = None
    for h in holdings:
        df = get_coin_series_inr(h["coin_id"], days=7)
        if df.empty:
            continue
        df = df[["timestamp", "price"]].copy()
        df["value"] = df["price"] * float(h["qty"])
        df = df[["timestamp", "value"]]
        if trend is None:
            trend = df.rename(columns={"value": "portfolio_value"})
        else:
            t1 = trend.copy()
            t1["timestamp"] = t1["timestamp"].dt.floor("H")
            df["timestamp"] = df["timestamp"].dt.floor("H")
            merged = pd.merge(t1, df, on="timestamp", how="outer").sort_values("timestamp").ffill()
            merged["portfolio_value"] = merged["portfolio_value"].fillna(0) + merged["value"].fillna(0)
            trend = merged[["timestamp", "portfolio_value"]]

    if trend is None:
        trend = pd.DataFrame(columns=["timestamp", "portfolio_value"])
    else:
        trend = trend.dropna().sort_values("timestamp")

    return {
        "invested": invested_total,
        "current": current_total,
        "pnl": pnl_total,
        "pnl_pct": pnl_pct,
        "table": table,
        "alerts": alerts,
        "risk_score": risk_score,
        "risk_status": risk_status,
        "trend": trend,
    }

def ensure_home_state():
    if "holdings" not in st.session_state:
        st.session_state.holdings = [
            {"coin": "Bitcoin", "coin_id": "bitcoin", "qty": 0.001, "avg_buy": 4500000},
            {"coin": "Ethereum", "coin_id": "ethereum", "qty": 0.02, "avg_buy": 250000},
            {"coin": "Solana", "coin_id": "solana", "qty": 0.2, "avg_buy": 9000},
        ]

    if "reports" not in st.session_state:
        st.session_state.reports = []

def add_report(name: str, df: pd.DataFrame, status: str = "Ready ✅"):
    st.session_state.reports.insert(0, {
        "name": name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "csv": df.to_csv(index=False),
    })

# ---------------- HOME ----------------
if menu == "Home":
    ensure_home_state()

    st.markdown("<div class='main-title'>CRYPTO MANAGER</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>User Profile • Portfolio • Risk • Insights • Reports</div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 0.8])
    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 👤 User Profile")
        st.write(f"**Email:** {st.session_state.user_email}")
        st.write("**Status:** Logged in ✅")
        st.write("**Mode:** Live CoinGecko prices (INR) ✅")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### ➕ Add / Update Holding")

        coin = st.selectbox("Coin", list(COIN_MAP.keys()), key="home_add_coin")
        qty = st.number_input("Quantity", min_value=0.0, value=0.0, step=0.01, format="%.6f", key="home_add_qty")
        avg_buy = st.number_input("Avg Buy Price (₹)", min_value=0.0, value=0.0, step=1000.0, key="home_add_avg")

        if st.button("Save Holding", key="home_save_holding"):
            cid = COIN_MAP[coin]
            found = False
            for h in st.session_state.holdings:
                if h["coin_id"] == cid:
                    h["qty"] = qty
                    h["avg_buy"] = avg_buy
                    h["coin"] = coin
                    found = True
                    break
            if not found:
                st.session_state.holdings.append({"coin": coin, "coin_id": cid, "qty": qty, "avg_buy": avg_buy})
            st.success("Holding saved ✅")
            st.rerun()

        if st.button("Clear All Holdings", key="home_clear_holdings"):
            st.session_state.holdings = []
            st.success("Holdings cleared ✅")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    summary = build_portfolio_summary(st.session_state.holdings)

    today_str = datetime.now().strftime("%Y-%m-%d")
    should_send_auto_alert = (
        ALERT_EMAIL_ENABLED
        and (summary.get("risk_score", 0) >= 70 or summary.get("pnl_pct", 0) <= -5)
        and st.session_state.last_auto_alert_sent != today_str
    )

    if should_send_auto_alert:
        subject = "🚨 Crypto Portfolio Alert Notification"
        body = create_alert_message(st.session_state.user_email, summary)
        sent = send_email_alert(
            to_email=st.session_state.user_email,
            subject=subject,
            body=body
        )
        if sent:
            st.session_state.last_auto_alert_sent = today_str

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Invested (₹)", f"{summary['invested']:,.2f}")
    k2.metric("Current Portfolio Value (₹)", f"{summary['current']:,.2f}")
    k3.metric("Total Profit/Loss (₹)", f"{summary['pnl']:,.2f}")
    k4.metric("P/L %", f"{summary['pnl_pct']:.2f}%")

    r1, r2 = st.columns([1, 1])
    with r1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🧠 Risk Score / Status")
        st.metric("Risk Score (0–100)", f"{summary.get('risk_score', 0)}")
        st.write(f"**Status:** {summary.get('risk_status', 'N/A')}")
        st.caption("Risk score is based on portfolio concentration + 7-day return volatility.")
        st.markdown("</div>", unsafe_allow_html=True)

    with r2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 💡 Suggestions (Buy / Hold / Sell)")
        if summary["table"].empty:
            st.info("Add holdings to see suggestions.")
        else:
            sug_counts = summary["table"]["Suggestion"].value_counts().to_dict()
            st.write(f"**Buy:** {sug_counts.get('Buy', 0)} | **Hold:** {sug_counts.get('Hold', 0)} | **Sell:** {sug_counts.get('Sell', 0)}")
            st.dataframe(summary["table"][["Coin", "Suggestion", "Value (₹)", "P/L (₹)"]], width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📌 Active Holdings Summary")
    st.dataframe(summary["table"], width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📈 Portfolio Growth Trend (Last 7 Days)")
    if summary["trend"].empty:
        st.info("Trend will appear once holdings have enough market chart data.")
    else:
        st.line_chart(summary["trend"].set_index("timestamp"))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🚨 Alert Notifications")

    if not summary["alerts"]:
        st.success("No critical alerts ✅")
    else:
        for a in summary["alerts"]:
            st.warning(a)

        col_alert1, col_alert2 = st.columns(2)

        with col_alert1:
            if st.button("Send Alert Email", key="send_alert_email"):
                subject = "🚨 Crypto Portfolio Alert Notification"
                body = create_alert_message(st.session_state.user_email, summary)
                sent = send_email_alert(
                    to_email=st.session_state.user_email,
                    subject=subject,
                    body=body
                )
                if sent:
                    st.success("Alert email sent successfully ✅")

        with col_alert2:
            st.markdown(
                """
                <a href="http://localhost:8501" target="_blank" style="text-decoration:none;">
                    <div style="
                        background: linear-gradient(90deg, #0b3b7a, #5483B3);
                        color: white;
                        padding: 12px 18px;
                        border-radius: 12px;
                        text-align: center;
                        font-weight: 700;
                        margin-top: 2px;
                    ">
                        Open Dashboard Alert Link
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📄 Downloadable Reports")

    cA, cB, cC = st.columns(3)

    with cA:
        if st.button("Generate Portfolio Report", key="gen_portfolio_report"):
            df = summary["table"].copy()
            df.insert(0, "User", st.session_state.user_email)
            add_report("Portfolio Report", df)
            st.success("Portfolio report added ✅")

    with cB:
        if st.button("Generate Risk Report", key="gen_risk_report"):
            df = pd.DataFrame([{
                "User": st.session_state.user_email,
                "Risk Score": summary.get("risk_score", 0),
                "Risk Status": summary.get("risk_status", "N/A"),
                "Total Invested (₹)": round(summary["invested"], 2),
                "Current Value (₹)": round(summary["current"], 2),
                "P/L %": round(summary["pnl_pct"], 2),
                "Generated On": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            add_report("Risk Report", df)
            st.success("Risk report added ✅")

    with cC:
        if st.button("Generate Prediction Report", key="gen_pred_report"):
            rows = []
            for h in st.session_state.holdings:
                dfp = get_coin_series_inr(h["coin_id"], days=7)
                if dfp.empty:
                    continue
                pred = predict_next_price_from_trend(dfp)
                rows.append({
                    "Coin": h["coin"],
                    "Trend": pred["trend"],
                    "Predicted Next Price (₹)": round(float(pred["predicted_price"]), 2),
                    "Confidence": pred["confidence"],
                    "Avg Daily Return %": round(float(pred["avg_return_pct"]), 2),
                    "Return Volatility %": round(float(pred["return_vol_pct"]), 2),
                })
            df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Coin", "Trend", "Predicted Next Price (₹)", "Confidence"])
            add_report("Prediction Report", df, status="Ready ✅" if not df.empty else "No data ⚠️")
            st.success("Prediction report added ✅")

    st.markdown("#### 📌 Reports List")
    if not st.session_state.reports:
        st.info("No reports generated yet. Use the buttons above.")
    else:
        for i, rep in enumerate(st.session_state.reports[:10]):
            rr1, rr2, rr3, rr4 = st.columns([2.2, 1.5, 1.2, 1.6])
            rr1.write(f"**{rep['name']}**")
            rr2.write(rep["date"])
            rr3.write(rep["status"])
            rr4.download_button(
                "Download",
                data=rep["csv"],
                file_name=f"{rep['name'].lower().replace(' ', '_')}.csv",
                mime="text/csv",
                key=f"dl_rep_{i}"
            )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RISK CHECKER ----------------
elif menu == "Risk Checker":
    st.markdown("<div class='main-title' style='font-size:40px;'>RISK ANALYSIS</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    coin_map = {"Bitcoin": "bitcoin", "Ethereum": "ethereum", "Solana": "solana"}
    coin_name = st.selectbox("Select Coin", list(coin_map.keys()))
    coin_id = coin_map[coin_name]

    live_data = get_crypto_data(coin_id)
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Price (INR)", f"₹ {live_data['price']:,}")
    m2.metric("Market Cap (INR)", f"₹ {live_data['market_cap']:,}")
    m3.metric("24h Change (%)", f"{live_data['change_24h']:.2f}%")

    chart_df = get_price_chart(coin_id)
    if chart_df.empty:
        st.info("Price chart data unavailable.")
    else:
        st.line_chart(chart_df.set_index("timestamp"))

    pred = predict_next_price_from_trend(chart_df)
    st.markdown("### 🔮 Prediction (Simple Trend Forecast)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Trend", pred["trend"])
    c2.metric("Predicted Next Price (INR)", f"₹ {pred['predicted_price']:,.2f}")
    c3.metric("Confidence", pred["confidence"])
    st.caption(
        f"Avg daily return: {pred['avg_return_pct']:.2f}% | "
        f"Return volatility: {pred['return_vol_pct']:.2f}%"
    )

    volatility = st.slider("Market Volatility (%)", 0, 100, 30)
    investment = st.number_input("Investment Amount (₹)", min_value=1000, step=1000)

    if st.button("Run Analysis"):
        vol_result, inv_result = run_parallel_risk_checks(volatility, investment)
        st.success("Analysis Completed")
        st.caption("⚡ Risk checks executed in parallel using ThreadPoolExecutor")
        r1, r2 = st.columns(2)
        r1.metric("Volatility Risk", vol_result)
        r2.metric("Investment Risk", inv_result)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- INVESTMENT MIX ----------------
elif menu == "Investment Mix":
    st.markdown("<div class='main-title' style='font-size:40px;'>INVESTMENT MIX</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.write("Generate a **portfolio mix** based on your risk level and total investment.")

    total_investment = st.number_input("Total Investment Amount (₹)", min_value=1000, step=1000, value=10000)
    risk_level = st.selectbox(
        "Select Risk Level",
        ["Low Risk (Conservative)", "Medium Risk (Balanced)", "High Risk (Aggressive)"]
    )

    if st.button("Generate Investment Mix"):
        allocation_pct = get_allocation_plan(risk_level)
        mix_df = build_allocation_table(total_investment, allocation_pct)

        st.success("Investment Mix Generated ✅")
        st.subheader("📊 Allocation Table")
        st.dataframe(mix_df, width="stretch")

        st.subheader("📈 Portfolio Distribution")
        chart_vals = mix_df.set_index("Coin")["Amount (₹)"]
        st.bar_chart(chart_vals)

        st.download_button(
            "Download Mix as CSV",
            mix_df.to_csv(index=False),
            file_name="investment_mix.csv",
            mime="text/csv"
        )

        st.info(
            "Low risk = more allocation to Bitcoin (stable). "
            "High risk = more allocation to Solana (volatile)."
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- REPORT GENERATOR ----------------
elif menu == "Report Generator":
    st.markdown("<div class='main-title' style='font-size:40px;'>REPORT GENERATOR</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    coin = st.selectbox("Select Coin", ["Bitcoin", "Ethereum", "Solana"])
    volatility = st.slider("Market Volatility (%)", 0, 100, 50)
    investment = st.number_input("Investment Amount (₹)", min_value=1000, step=1000)

    if st.button("Generate Report"):
        vol_result, inv_result = run_parallel_risk_checks(volatility, investment)

        df = pd.DataFrame({
            "Coin": [coin],
            "Volatility": [volatility],
            "Investment": [investment],
            "Volatility Risk": [vol_result],
            "Investment Risk": [inv_result],
            "Generated On": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })

        st.success("Report Generated Successfully ✅")
        st.caption("⚡ Risk checks executed in parallel using ThreadPoolExecutor")
        st.dataframe(df, width="stretch")

        st.download_button(
            "Download Report",
            df.to_csv(index=False),
            "investment_report.csv"
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SPREADING RULE SETTER ----------------

elif menu == "Spreading Rule Setter":
    st.markdown("<div class='main-title' style='font-size:40px;'>SPREADING RULE SETTER</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.write("This module applies rule-based portfolio spreading based on risk, market scenario, portfolio loss, and prediction trends.")

    total_investment = st.number_input(
        "Total Investment Amount (₹)",
        min_value=1000,
        step=1000,
        value=50000,
        key="spread_total_investment"
    )

    base_risk_level = st.selectbox(
        "Select Base Risk Level",
        ["Low Risk (Conservative)", "Medium Risk (Balanced)", "High Risk (Aggressive)"],
        key="spread_risk_level"
    )

    scenario = st.selectbox(
        "Select Market Scenario",
        ["Bull Market", "Bear Market", "Volatile Market"],
        key="spread_scenario"
    )

    risk_score = st.slider(
        "Portfolio Risk Score",
        0, 100, 60,
        key="spread_risk_score"
    )

    pnl_pct = st.slider(
        "Portfolio Profit/Loss %",
        -20, 20, -3,
        key="spread_pnl_pct"
    )

    max_cap = st.slider(
        "Maximum Allocation Cap Per Coin (%)",
        30, 80, 60,
        key="spread_max_cap"
    )

    st.markdown("### Prediction Trend Input")
    btc_trend = st.selectbox("Bitcoin Trend", ["Uptrend", "Downtrend", "Sideways"], key="btc_trend")
    eth_trend = st.selectbox("Ethereum Trend", ["Uptrend", "Downtrend", "Sideways"], key="eth_trend")
    sol_trend = st.selectbox("Solana Trend", ["Uptrend", "Downtrend", "Sideways"], key="sol_trend")

    if st.button("Apply Spreading Rules", key="apply_spread_rules"):
        # Base mix from existing investment mix rules
        base_alloc = get_allocation_plan(base_risk_level)

        predictions = {
            "Bitcoin": btc_trend,
            "Ethereum": eth_trend,
            "Solana": sol_trend
        }

        adjusted_alloc, applied_rules = apply_spreading_rules(
            base_alloc=base_alloc,
            scenario=scenario,
            risk_score=risk_score,
            pnl_pct=pnl_pct,
            predictions=predictions,
            max_cap=max_cap
        )

        base_df = spreading_table(total_investment, base_alloc)
        final_df = spreading_table(total_investment, adjusted_alloc)

        st.success("Spreading rules applied successfully ✅")

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("📊 Base Allocation")
            st.dataframe(base_df, width="stretch")

        with c2:
            st.subheader("✅ Adjusted Allocation")
            st.dataframe(final_df, width="stretch")

        st.subheader("📈 Adjusted Portfolio Distribution")
        chart_df = final_df.set_index("Coin")["Amount (₹)"]
        st.bar_chart(chart_df)

        st.subheader("🧠 Applied Rules")
        if applied_rules:
            for rule in applied_rules:
                st.info(rule)
        else:
            st.info("No rules were triggered. Base allocation remains unchanged.")

        st.download_button(
            "Download Adjusted Spread Report",
            final_df.to_csv(index=False),
            file_name="spreading_rule_report.csv",
            mime="text/csv"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    