import aiohttp
from typing import List
from .logger import logger
from .config import NEWS_API_KEY

YAHOO_GAINERS_URL = "https://query1.finance.yahoo.com/v7/finance/screener/predefined/saved"
NEWS_URL = "https://newsapi.org/v2/everything"

class MarketAPI:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    async def get_top_movers(self, limit: int = 10) -> List[str]:
        params = {"scrIds": "day_gainers", "count": limit}
        try:
            async with self.session.get(YAHOO_GAINERS_URL, params=params, timeout=10) as resp:
                data = await resp.json()
                quotes = data['finance']['result'][0]['quotes']
                movers = [q['symbol'] for q in quotes if q.get('regularMarketPrice', 0) > 5]
                logger.info(f"Fetched top movers: {movers}")
                return movers
        except Exception as e:
            logger.error(f"Error fetching top movers: {e}")
            return []

    async def fetch_news(self, symbol: str, limit: int = 5) -> List[str]:
        if not NEWS_API_KEY:
            logger.warning("NEWS_API_KEY not set, skipping news fetch")
            return []
        params = {
            "q": symbol,
            "apiKey": NEWS_API_KEY,
            "pageSize": limit,
            "sortBy": "publishedAt",
            "language": "en"
        }
        try:
            async with self.session.get(NEWS_URL, params=params, timeout=10) as resp:
                data = await resp.json()
                titles = [article['title'] for article in data.get('articles', [])]
                logger.info(f"News for {symbol}: {titles}")
                return titles
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    async def fetch_price_history(self, symbol: str, range: str = '1d', interval: str = '5m') -> List[float]:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
        params = {"range": range, "interval": interval}
        try:
            async with self.session.get(url, params=params, timeout=10) as resp:
                data = await resp.json()
                closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
                return [c for c in closes if c is not None]
        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            return []
