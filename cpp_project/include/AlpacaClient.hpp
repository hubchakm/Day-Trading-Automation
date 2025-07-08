#ifndef ALPACA_CLIENT_HPP
#define ALPACA_CLIENT_HPP

#include <string>
#include <map>

struct Position {
    std::string symbol;
    double qty{0};
    double entry_price{0};
};

class AlpacaClient {
public:
    AlpacaClient(const std::string& apiKey,
                 const std::string& apiSecret,
                 const std::string& baseUrl);

    double getAccountEquity();
    bool isMarketOpen();
    double getCurrentPrice(const std::string& symbol);
    std::map<std::string, Position> listPositions();
    void buy(const std::string& symbol, double dollars);
    void sell(const std::string& symbol, double qty);

private:
    std::string key;
    std::string secret;
    std::string url;
};

#endif // ALPACA_CLIENT_HPP
