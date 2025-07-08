#include "Trader.hpp"
#include <iostream>

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
    // Placeholder for trading logic
}

