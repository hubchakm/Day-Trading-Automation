import os

ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_API_SECRET = os.getenv('ALPACA_API_SECRET')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

STARTING_CASH = float(os.getenv('STARTING_CASH', 100))
POSITIONS = int(os.getenv('POSITIONS', 5))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
