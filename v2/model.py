import numpy as np
from typing import List

class PricePredictor:
    """Simple linear regression predictor."""

    def predict_next(self, prices: List[float]) -> float:
        if len(prices) < 2:
            return prices[-1] if prices else 0
        x = np.arange(len(prices))
        y = np.array(prices)
        A = np.vstack([x, np.ones(len(x))]).T
        m, b = np.linalg.lstsq(A, y, rcond=None)[0]
        next_x = len(prices)
        prediction = m * next_x + b
        return float(prediction)
