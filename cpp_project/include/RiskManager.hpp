#ifndef RISK_MANAGER_HPP
#define RISK_MANAGER_HPP

#include <string>
#include <unordered_map>

class RiskManager {
public:
    explicit RiskManager(double maxPositionRisk = 0.02,
                         double dailyLossLimit = 0.05);

    bool canEnter(const std::string& symbol, double equity);
    bool shouldExit(double entryPrice, double currentPrice);

private:
    double maxRisk;
    double dailyLimit;
    std::unordered_map<std::string, double> entryPrices;
    double dailyPnL{0};
};

#endif // RISK_MANAGER_HPP
