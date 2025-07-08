import asyncio
from .trader import Trader

async def main():
    trader = Trader()
    await trader.run()

if __name__ == '__main__':
    asyncio.run(main())
