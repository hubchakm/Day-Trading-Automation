#include "RiskManager.hpp"

RiskManager::RiskManager(double maxPositionRisk, double dailyLossLimit)
    : maxRisk(maxPositionRisk), dailyLimit(dailyLossLimit) {}

bool RiskManager::canEnter(const std::string& symbol, double equity) {
    if (dailyPnL < -dailyLimit * equity) {
        return false;
    }
    return entryPrices.find(symbol) == entryPrices.end();
}

bool RiskManager::shouldExit(double entryPrice, double currentPrice) {
    double change = (currentPrice - entryPrice) / entryPrice;
    return change <= -maxRisk || change >= maxRisk;
}
