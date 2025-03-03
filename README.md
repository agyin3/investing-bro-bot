# Stock Market Investment Program

This is an automated stock market investment program designed for short-term and algorithmic trading. The system integrates with **Alpaca** for executing trades and leverages multiple data sources for real-time market analysis.

## Features

-   📈 **Algorithmic Trading** – Executes trades based on predefined strategies.
-   🔍 **Data Aggregation** – Uses multiple sources to enhance decision-making.
-   📊 **Backtesting** – Analyzes historical data before live execution.
-   🚀 **Automated Execution** – Trades are placed automatically via Alpaca.
-   📡 **Risk Management** – Implements stop-loss and portfolio diversification.
-   📜 **Graphical and Text Outputs** – Provides visual charts and text alerts.

## Technologies Used

-   **Python** – Core backend processing and algorithm execution.
-   **Alpaca API** – Brokerage integration for live trading.
-   **Pandas / NumPy** – Data handling and numerical computations.
-   **Matplotlib / Plotly** – Data visualization.
-   **React (optional)** – If a frontend is required.

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/yourusername/stock-investment-bot.git
    cd stock-investment-bot
    ```

2. **Create a virtual environment**:

    ```sh
    python -m venv venv
    source venv/bin/activate   # On macOS/Linux
    venv\Scripts\activate      # On Windows
    ```

3. **Install dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables** (Create a `.env` file):

    ```sh
    ALPACA_API_KEY=your_api_key
    ALPACA_SECRET_KEY=your_secret_key
    ```

5. **Run the program**:
    ```sh
    python main.py
    ```

## Usage

1. **Configure Trading Strategies**  
   Modify `strategy.py` to adjust the logic for buying and selling stocks.

2. **Backtest Before Live Trading**

    ```sh
    python backtest.py
    ```

3. **Start Live Trading**  
   Ensure your Alpaca account is funded and configured before running:
    ```sh
    python trade.py
    ```

## Roadmap

-   [ ] Add AI-based predictive modeling.
-   [ ] Expand support for multiple broker APIs.
-   [ ] Develop a web-based dashboard (React/Next.js).

## Contributing

Pull requests are welcome! Please open an issue first to discuss proposed changes.

## License

This project is licensed under the MIT License.

---

### ⚠ Disclaimer

This software is for educational purposes only. Use at your own risk. Past performance does not guarantee future results.
