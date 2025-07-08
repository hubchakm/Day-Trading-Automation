#include "Trader.hpp"
#include <iostream>
#include <chrono>
#include <thread>

Trader::Trader(const std::string& apiKey,
               const std::string& apiSecret,
               const std::string& baseUrl)
    : api(apiKey, apiSecret, baseUrl) {}

void Trader::run() {
    std::cout << "Fetching top gainers..." << std::endl;
    auto gainers = scanner.fetchTopGainers();
    std::cout << "Found " << gainers.size() << " gainers" << std::endl;
    for (const auto& g : gainers) {
        std::cout << " - " << g << std::endl;
    }

    // Example backtest
    auto data = backtester.loadData("historical.csv");
    if (!data.empty()) {
        double equity = backtester.run(data, 10000.0, 0.01);
        std::cout << "Backtest final equity: $" << equity << std::endl;
    }

    // Simple high frequency loop printing prices
    hft.start([&]() {
        if (!api.isMarketOpen()) return;
        for (const auto& sym : gainers) {
            double price = api.getCurrentPrice(sym);
            if (risk.canEnter(sym, api.getAccountEquity())) {
                std::cout << "[HFT] " << sym << " $" << price << std::endl;
            }
        }
    }, 100);

    std::this_thread::sleep_for(std::chrono::seconds(1));
    hft.stop();
}

