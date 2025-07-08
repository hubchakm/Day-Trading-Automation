#include "HFTEngine.hpp"
#include <chrono>

HFTEngine::HFTEngine() = default;
HFTEngine::~HFTEngine() { stop(); }

void HFTEngine::start(const std::function<void()>& tickCallback, int intervalMs) {
    stop();
    running = true;
    worker = std::thread([=]() {
        while (running) {
            auto start = std::chrono::high_resolution_clock::now();
            tickCallback();
            auto end = std::chrono::high_resolution_clock::now();
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
            if (elapsed.count() < intervalMs) {
                std::this_thread::sleep_for(std::chrono::milliseconds(intervalMs - elapsed.count()));
            }
        }
    });
}

void HFTEngine::stop() {
    if (running) {
        running = false;
        if (worker.joinable()) {
            worker.join();
        }
    }
}
