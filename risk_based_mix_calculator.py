# ==========================================
# MILESTONE 2 – INVESTMENT MIX CALCULATOR
# ==========================================
import matplotlib.pyplot as plt
print("\nMILESTONE 2: INVESTMENT MIX CALCULATOR")


# ---------------------------------
# FUNCTION: MIXING LOGIC
# ---------------------------------
def calculate_mix(risk_level, total_amount):

    # Rule-based allocation
    if risk_level == "low":
        mix = {
            "Bitcoin": 0.50,
            "Ethereum": 0.30,
            "Solana": 0.10,
            "BinanceCoin": 0.10
        }

    elif risk_level == "medium":
        mix = {
            "Bitcoin": 0.40,
            "Ethereum": 0.30,
            "Solana": 0.20,
            "BinanceCoin": 0.10
        }

    elif risk_level == "high":
        mix = {
            "Bitcoin": 0.30,
            "Ethereum": 0.20,
            "Solana": 0.30,
            "BinanceCoin": 0.20
        }

    else:
        print("Invalid risk level selected.")
        return None

    # Predefined suggestions
    suggestions = {
        "Bitcoin": "Stable asset suitable for long-term holding.",
        "Ethereum": "Balanced growth with moderate risk exposure.",
        "Solana": "High growth potential but more volatile.",
        "BinanceCoin": "Good for diversification and exchange utility."
    }

    # Calculate allocation
    allocation = {}
    for coin, weight in mix.items():
        allocation[coin] = total_amount * weight

    return allocation, suggestions


# ---------------------------------
# TEST WITH SAMPLE INPUT
# ---------------------------------
if __name__ == "__main__":

    sample_risk = "medium"
    sample_amount = 100000

    result, suggestions = calculate_mix(sample_risk, sample_amount)

    print(f"\nRisk Level: {sample_risk.capitalize()}")
    print(f"Total Investment: ₹{sample_amount:,.2f}")
    print("\nRecommended Investment Mix:\n")

    total_check = 0

    for coin, amount in result.items():
        print(f"{coin}")
        print(f"  Allocation: ₹{amount:,.2f}")
        print(f"  Suggestion: {suggestions[coin]}")
        print("")
        total_check += amount

    print("Verification:")
    print(f"Total Allocated: ₹{total_check:,.2f}")

        # -------------------------------
    # VISUAL REPRESENTATION (BAR CHART)
    # -------------------------------

    coins = list(result.keys())
    amounts = list(result.values())

    plt.figure(figsize=(8, 5))
    plt.bar(coins, amounts)

    plt.title("Investment Allocation Breakdown")
    plt.xlabel("Cryptocurrency")
    plt.ylabel("Investment Amount (₹)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.show()