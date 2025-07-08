import asyncio
from typing import List, Dict

from .api import MarketAPI
from .model import PricePredictor
from .logger import logger
from .config import POSITIONS

class Trader:
    def __init__(self):
        self.api = MarketAPI()
        self.predictor = PricePredictor()

    async def analyze_symbol(self, symbol: str) -> Dict:
        prices, news = await asyncio.gather(
            self.api.fetch_price_history(symbol),
            self.api.fetch_news(symbol)
        )
        if not prices:
            return {"symbol": symbol, "score": -float('inf')}
        prediction = self.predictor.predict_next(prices)
        current = prices[-1]
        score = prediction - current
        logger.info(f"{symbol} prediction: {prediction:.2f}, current: {current:.2f}, score: {score:.2f}")
        return {"symbol": symbol, "score": score, "news": news, "prediction": prediction}

    async def pick_winners(self, candidates: List[str]) -> List[Dict]:
        tasks = [self.analyze_symbol(sym) for sym in candidates]
        results = await asyncio.gather(*tasks)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:POSITIONS]

    async def run(self):
        movers = await self.api.get_top_movers(limit=POSITIONS * 5)
        if not movers:
            logger.error("No movers found.")
            return
        winners = await self.pick_winners(movers)
        for win in winners:
            logger.info(f"Top pick {win['symbol']} predicted {win['prediction']:.2f}")
            for headline in win.get('news', []):
                logger.info(f" - {headline}")
        await self.api.close()

