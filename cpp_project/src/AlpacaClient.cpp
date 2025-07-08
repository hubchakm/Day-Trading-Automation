#include "AlpacaClient.hpp"
#include <iostream>

AlpacaClient::AlpacaClient(const std::string& apiKey,
                           const std::string& apiSecret,
                           const std::string& baseUrl)
    : key(apiKey), secret(apiSecret), url(baseUrl) {}

// Placeholder implementations

double AlpacaClient::getAccountEquity() {
    std::cout << "[Stub] getAccountEquity called" << std::endl;
    return 0.0;
}

bool AlpacaClient::isMarketOpen() {
    std::cout << "[Stub] isMarketOpen called" << std::endl;
    return true;
}

double AlpacaClient::getCurrentPrice(const std::string& symbol) {
    std::cout << "[Stub] getCurrentPrice(" << symbol << ")" << std::endl;
    return 0.0;
}

std::map<std::string, Position> AlpacaClient::listPositions() {
    std::cout << "[Stub] listPositions" << std::endl;
    return {};
}

void AlpacaClient::buy(const std::string& symbol, double dollars) {
    std::cout << "[Stub] buy " << symbol << " $" << dollars << std::endl;
}

void AlpacaClient::sell(const std::string& symbol, double qty) {
    std::cout << "[Stub] sell " << symbol << " qty " << qty << std::endl;
}

