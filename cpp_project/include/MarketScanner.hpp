#ifndef MARKET_SCANNER_HPP
#define MARKET_SCANNER_HPP

#include <string>
#include <vector>

class MarketScanner {
public:
    // Fetch top gainers from Yahoo finance.
    std::vector<std::string> fetchTopGainers(int limit = 30);
};

#endif // MARKET_SCANNER_HPP
