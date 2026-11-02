#include <atomic>
#include <barrier>
#include <iostream>
#include <latch>
#include <mutex>
#include <semaphore>
#include <thread>
#include <vector>

thread_local int per_thread_calls = 0;

int main() {
    constexpr int N = 4;
    std::latch ready{N};
    std::atomic<int> started{0};
    {
        std::vector<std::jthread> ts;
        for (int i = 0; i < N; ++i) ts.emplace_back([&] { ++started; ready.count_down(); });
        ready.wait();                                   // all workers have checked in
        std::cout << "latch released after " << started.load() << " workers\n";
    }

    int phase = 0;
    std::barrier sync{N, [&]() noexcept { ++phase; }};  // completion runs once per phase
    std::atomic<int> work_done{0};
    {
        std::vector<std::jthread> ts;
        for (int i = 0; i < N; ++i)
            ts.emplace_back([&] {
                for (int p = 0; p < 3; ++p) { ++work_done; sync.arrive_and_wait(); }
            });
    }
    std::cout << "barrier phases: " << phase << ", work items: " << work_done.load() << '\n';

    std::counting_semaphore<2> slots{2};                // at most 2 "downloads" at once
    std::atomic<int> active{0}, max_active{0};
    {
        std::vector<std::jthread> ts;
        for (int i = 0; i < 6; ++i)
            ts.emplace_back([&] {
                slots.acquire();
                int now = ++active;
                int prev = max_active.load();
                while (now > prev && !max_active.compare_exchange_weak(prev, now)) {}
                std::this_thread::yield();
                --active;
                slots.release();
            });
    }
    std::cout << "max concurrent downloads: " << (max_active.load() <= 2 ? "<= 2" : "too many!") << '\n';

    {
        std::jthread a{[] { for (int i = 0; i < 5; ++i) ++per_thread_calls; }};
        std::jthread b{[] { ++per_thread_calls; }};
    }
    std::cout << "main's thread_local still " << per_thread_calls << '\n';
}
