# Alpaca Momentum Day Trader Bot

A Python trading bot that buys and sells US stocks using real-time momentum and volume signals via the Alpaca API.

**Features:**

* Dynamic universe (fetches live top gainers)
* Risk management (stop-loss, take-profit, trailing stop)
* Automatic position monitoring and rotation
* Manual user controls for quick exits or resets
* Trade logs for performance analysis

---

## Getting Started

### 1. **Sign up for Alpaca**

* Register for a free account (paper or live trading) here:
  [https://alpaca.markets/](https://alpaca.markets/)

* **Paper trading is free** and recommended for testing.

### 2. **Create API Keys**

* After registering and verifying your account, go to:

  * **Dashboard > API Keys**
  * Click “Generate New Key”
  * Copy your **API Key ID** and **Secret Key**.

  [Alpaca: Creating an API Key – Docs](https://docs.alpaca.markets/docs/creating-an-api-key)

### 3. **Clone This Repo**

```bash
git clone https://github.com/YOUR_USERNAME/your-alpaca-bot-repo.git
cd your-alpaca-bot-repo
```

### 4. **Set Up Your `.env` File**

Create a file named `.env` in your project root directory:

```
ALPACA_API_KEY=your_api_key_id_here
ALPACA_API_SECRET=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
STARTING_CASH=100
```

* Use `https://api.alpaca.markets` for live trading (with real money; **not recommended for beginners**).

### 5. **Install Requirements**

Make sure you have Python 3.8+ and pip. Then run:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should contain:

```
alpaca-trade-api
pandas
python-dotenv
pytz
requests
```

### 6. **Run the Bot**

```bash
python stock-script.py
```

* The bot will wait for market open, pick top momentum stocks, and begin trading.
* Use the keyboard:

  * Press **`s`** and Enter: Sell all positions and exit.
  * Press **`r`** and Enter: Recheck all positions against the latest top movers and rebalance.

---

## Features

* **Live momentum scanning:** Pulls real-time top gainers from Yahoo Finance.
* **Volume and trend filter:** Trades only if a stock is showing real strength and volume.
* **Risk management:** Stop-loss, take-profit, and trailing stop logic.
* **Day trade and loss limits:** Controls risk on small accounts.
* **No overnight holding:** Sells everything before market close.
* **Trade summary/report:** Prints end-of-day P\&L and exports trade log to `trades.csv`.
* **Emergency manual controls:** Keyboard shortcuts for safety and strategy adjustments.

---

##  Disclaimers & Notes

* This script is **for educational purposes only**. Trading stocks carries risk. Past results do not guarantee future returns.
* Test thoroughly with **paper trading** before going live.
* You are solely responsible for your trading and API keys security.

---

##  Resources

* [Alpaca Documentation](https://docs.alpaca.markets/)
* [Alpaca Paper Trading](https://alpaca.markets/docs/trading-on-alpaca/paper-trading/)
* [Yahoo Finance Screener](https://finance.yahoo.com/screener/predefined/day_gainers)
* [Python-dotenv](https://pypi.org/project/python-dotenv/)

---

**Questions or suggestions?**
Open an issue or [contact me here](mailto:your@email.com)!

---

**Happy trading!**
