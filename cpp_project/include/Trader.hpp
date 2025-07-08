#ifndef TRADER_HPP
#define TRADER_HPP

#include "AlpacaClient.hpp"
#include "MarketScanner.hpp"
#include <string>
#include <vector>

class Trader {
public:
    Trader(const std::string& apiKey,
           const std::string& apiSecret,
           const std::string& baseUrl);

    void run();

private:
    AlpacaClient api;
    MarketScanner scanner;
};

#endif // TRADER_HPP
