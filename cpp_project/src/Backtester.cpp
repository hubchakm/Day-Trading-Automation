#include "Backtester.hpp"
#include <fstream>
#include <sstream>

std::vector<HistoricalBar> Backtester::loadData(const std::string& csvFile) {
    std::vector<HistoricalBar> data;
    std::ifstream file(csvFile);
    std::string line;
    if (!file.is_open()) {
        return data;
    }
    // Expect header: date,open,high,low,close
    std::getline(file, line); // discard header
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string token;
        HistoricalBar bar;
        std::getline(ss, bar.date, ',');
        if (std::getline(ss, token, ',')) bar.open = std::stod(token);
        if (std::getline(ss, token, ',')) bar.high = std::stod(token);
        if (std::getline(ss, token, ',')) bar.low = std::stod(token);
        if (std::getline(ss, token, ',')) bar.close = std::stod(token);
        data.push_back(bar);
    }
    return data;
}

// Extremely naive backtest: buy if close > open, sell next bar at close.
double Backtester::run(const std::vector<HistoricalBar>& data,
                       double initialCash,
                       double riskPerTrade) {
    double cash = initialCash;
    double position = 0.0;
    for (size_t i = 1; i < data.size(); ++i) {
        const auto& prev = data[i - 1];
        const auto& bar = data[i];
        if (prev.close > prev.open && cash > 0) {
            // risk a fraction of cash
            double dollars = cash * riskPerTrade;
            position += dollars / bar.open;
            cash -= dollars;
        }
        if (position > 0) {
            cash += position * bar.close;
            position = 0;
        }
    }
    return cash + position * data.back().close;
}

