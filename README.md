# 🚀 Crypto Investment Manager

A full-stack Python-based system for **cryptocurrency analysis, prediction, and portfolio optimization** using real-time data, rule-based logic, and risk analysis.

---

## 📌 Project Overview

Crypto Investment Manager helps users manage crypto investments efficiently by:

* 📊 Analyzing historical and live market data
* ⚙️ Generating optimal investment mix
* 🔍 Performing risk analysis using parallel processing
* 📈 Predicting future trends
* 📄 Generating reports with alerts

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit (Python-based UI)
* **Backend:** Python
* **API:** CoinGecko API
* **Authentication:** Firebase
* **Data Processing:** Pandas
* **Email Alerts:** SMTP (Gmail)

---

## ✨ Key Features

* 🔐 User Authentication (Login / Signup using Firebase)
* 📊 Live Crypto Dashboard (Real-time INR prices)
* 📈 Portfolio Tracking & Growth Visualization
* ⚙️ Investment Mix Calculator (Risk-based allocation)
* 🔍 Risk Checker (Parallel processing)
* 🔮 Price Prediction (Trend-based forecasting)
* 📄 Report Generator (Downloadable CSV reports)
* 🔔 Email Alerts for risk and loss conditions
* 🧠 Spreading Rule Setter (Dynamic portfolio balancing)

---

## 📂 Project Structure

```
Crypto-Investment-Manager/
│
├── app.py                          # Full-stack application (frontend + backend)
├── data_collector.py               # Data collection from CoinGecko API
├── eda.py                          # Data analysis
├── eda_visuals.py                  # Visualization
├── risk_based_mix_calculator.py    # Investment logic
│
├── docs/                           # Documentation & screenshots
│   ├── agile.md                    # Agile development documentation
│   ├── screenshots                 # Output images
│
├── README.md
├── LICENSE
```

---

## 📄 Documentation

* 📘 [Agile Documentation](docs/agile.md)

---

## ⚙️ How to Run

### 1. Install dependencies

```
pip install streamlit pandas requests
```

### 2. Run application

```
streamlit run app.py
```

### 3. Open browser

```
http://localhost:8501
```

---

## ⚠️ Challenges Faced

* Handling parallel processing efficiently
* Managing multiple module integration
* Ensuring prediction accuracy
* Designing flexible rule-based system

---

## 🔮 Future Improvements

* Integrate Machine Learning models (LSTM, ARIMA)
* Real-time trading signals
* Improved UI/UX design
* Deploy as a web application

---

## 📊 Project Status

✔ Completed as part of **Infosys Springboard Internship**
✔ All milestones implemented successfully

---

## 👨‍💻 Author

**Pradeeptha G**

---

## 📜 License

This project is licensed under the MIT License.
