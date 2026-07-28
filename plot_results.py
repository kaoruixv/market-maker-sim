import matplotlib.pyplot as plt
import pandas as pd


def plot_simulation_data():
    print("Loading simulation_ticks.csv...")
    try:
        df = pd.read_csv("simulation_ticks.csv")
    except FileNotFoundError:
        print("Error: simulation_ticks.csv not found in this directory.")
        return

    # Create a figure with 2 stacked subplots
    _fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Top subplot: Prices and Quotes
    ax1.plot(
        df["Step"], df["MidPrice"], label="Mid Price", color="black", linewidth=1.5
    )
    ax1.plot(
        df["Step"],
        df["Quote_Ask"],
        label="Agent Ask",
        color="red",
        linestyle="--",
        alpha=0.7,
    )
    ax1.plot(
        df["Step"],
        df["Quote_Bid"],
        label="Agent Bid",
        color="green",
        linestyle="--",
        alpha=0.7,
    )
    ax1.set_ylabel("Price")
    ax1.set_title("Avellaneda-Stoikov Pricing vs Mid Price")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Bottom subplot: Inventory
    ax2.plot(df["Step"], df["Inventory"], label="Inventory", color="blue", linewidth=2)
    ax2.axhline(0, color="black", linestyle="-", alpha=0.3)
    ax2.set_xlabel("Simulation Step")
    ax2.set_ylabel("Net Position (Qty)")
    ax2.set_title("Agent Inventory Over Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save the file locally
    plt.savefig("local_as_analysis.png")
    print("Success! Plot saved as local_as_analysis.png in your current directory.")

    # Attempt to open the interactive viewing window
    try:
        plt.show()
    except Exception:  # noqa: BLE001
        print(
            "Interactive window not supported in this terminal, but the PNG is saved!"
        )


if __name__ == "__main__":
    plot_simulation_data()
