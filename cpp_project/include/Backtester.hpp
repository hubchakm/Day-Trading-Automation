#ifndef BACKTESTER_HPP
#define BACKTESTER_HPP

#include <string>
#include <vector>
#include <map>

struct HistoricalBar {
    std::string date;
    double open{0};
    double high{0};
    double low{0};
    double close{0};
};

// Simple backtesting framework that loads CSV files and simulates trades.
class Backtester {
public:
    // Load historical data from CSV for given symbol.
    std::vector<HistoricalBar> loadData(const std::string& csvFile);

    // Run backtest using simple closing price strategy.
    // Returns final portfolio value starting from initialCash.
    double run(const std::vector<HistoricalBar>& data,
               double initialCash,
               double riskPerTrade);
};

#endif // BACKTESTER_HPP
