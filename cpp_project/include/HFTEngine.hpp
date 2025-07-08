#ifndef HFT_ENGINE_HPP
#define HFT_ENGINE_HPP

#include <thread>
#include <atomic>
#include <functional>

// Very lightweight high-frequency trading loop that repeatedly
// calls a user-supplied callback.
class HFTEngine {
public:
    HFTEngine();
    ~HFTEngine();

    void start(const std::function<void()>& tickCallback,
               int intervalMs = 50);
    void stop();

private:
    std::thread worker;
    std::atomic<bool> running{false};
};

#endif // HFT_ENGINE_HPP
