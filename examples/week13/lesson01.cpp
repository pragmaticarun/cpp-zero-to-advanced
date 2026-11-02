#include <atomic>
#include <chrono>
#include <functional>
#include <iostream>
#include <stop_token>
#include <thread>
#include <vector>

void decode(int file_id, int& result) { result = file_id * file_id; }   // pretend work

int main() {
    std::vector<int> results(4);
    {
        std::vector<std::jthread> workers;
        for (int i = 0; i < 4; ++i) workers.emplace_back(decode, i + 1, std::ref(results[i]));
    }                                                  // all jthreads join here
    for (int r : results) std::cout << r << ' ';
    std::cout << "<- decoded\n";

    std::atomic<int> ticks{0};
    {
        std::jthread meter{[&ticks](std::stop_token st) {
            std::stop_callback on_stop{st, [] { std::cout << "stop requested\n"; }};
            while (!st.stop_requested()) {
                ++ticks;
                std::this_thread::sleep_for(std::chrono::milliseconds{1});
            }
        }};
        while (ticks < 5) std::this_thread::yield();
        meter.request_stop();                          // cooperative: the thread notices and exits
    }                                                  // and is joined
    std::cout << "meter ran at least 5 ticks: " << std::boolalpha << (ticks >= 5) << '\n';

    std::thread classic{[] {}};
    classic.join();                                    // forget this and std::terminate() is called
    std::cout << "hardware threads known: " << (std::thread::hardware_concurrency() > 0) << '\n';
}
