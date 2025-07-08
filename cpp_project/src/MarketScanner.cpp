#include "MarketScanner.hpp"
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <iostream>

using json = nlohmann::json;

namespace {
size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}
}

std::vector<std::string> MarketScanner::fetchTopGainers(int limit) {
    std::vector<std::string> movers;
    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "Failed to init curl" << std::endl;
        return movers;
    }

    std::string readBuffer;
    std::string url = "https://query1.finance.yahoo.com/v7/finance/screener/predefined/saved?";
    url += "scrIds=day_gainers&count=" + std::to_string(limit);

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
    CURLcode res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
        curl_easy_cleanup(curl);
        return movers;
    }
    curl_easy_cleanup(curl);

    try {
        auto j = json::parse(readBuffer);
        auto quotes = j["finance"]["result"][0]["quotes"];
        for (auto& q : quotes) {
            if (q.contains("symbol") && q.contains("regularMarketPrice") && q["regularMarketPrice"].get<double>() > 5) {
                movers.push_back(q["symbol"].get<std::string>());
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "JSON parse error: " << e.what() << std::endl;
    }
    return movers;
}

