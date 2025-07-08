#ifndef TRADER_HPP
#define TRADER_HPP

#include "AlpacaClient.hpp"
#include "MarketScanner.hpp"
#include "RiskManager.hpp"
#include "Backtester.hpp"
#include "HFTEngine.hpp"
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
    RiskManager risk;
    Backtester backtester;
    HFTEngine hft;
};

#endif // TRADER_HPP
