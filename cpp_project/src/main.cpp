#include "Trader.hpp"
#include <cstdlib>

int main() {
    const char* key = std::getenv("ALPACA_API_KEY");
    const char* secret = std::getenv("ALPACA_API_SECRET");
    const char* url = std::getenv("ALPACA_BASE_URL");

    Trader trader(key ? key : "", secret ? secret : "", url ? url : "");
    trader.run();
    return 0;
}

