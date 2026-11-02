#include <chrono>
#include <iostream>
#include <string>
#include <utility>

class Timer {
public:
    explicit Timer(std::string label) : label_{std::move(label)}, start_{std::chrono::steady_clock::now()} {}
    ~Timer() {
        const auto ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start_);
        std::cout << label_ << ": " << ms.count() << " ms\n";
    }
    Timer(const Timer&) = delete;
    Timer& operator=(const Timer&) = delete;
private:
    std::string label_;
    std::chrono::steady_clock::time_point start_;
};

int main() {
    volatile double sink = 0;   // volatile so the loop isn't optimized away
    {
        Timer t{"sum loop"};
        for (int i = 0; i < 1'000'000; ++i) sink = sink + i * 0.5;
    }
}
