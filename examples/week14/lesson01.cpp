#include <atomic>
#include <iostream>
#include <thread>
#include <vector>

int main() {
    std::atomic<long> hits{0};
    {
        std::vector<std::jthread> ts;
        for (int t = 0; t < 4; ++t)
            ts.emplace_back([&] { for (int i = 0; i < 100000; ++i) hits.fetch_add(1, std::memory_order_relaxed); });
    }
    std::cout << "relaxed counter: " << hits.load() << '\n';

    int data = 0;                                     // plain, non-atomic payload
    std::atomic<bool> ready{false};
    {
        std::jthread producer{[&] { data = 42; ready.store(true, std::memory_order_release); }};
        std::jthread consumer{[&] {
            while (!ready.load(std::memory_order_acquire)) {}       // spin (fine for a demo)
            std::cout << "consumer sees data = " << data << '\n';   // guaranteed 42
        }};
    }

    std::atomic<int> maximum{0};
    auto update_max = [&](int v) {
        int cur = maximum.load();
        while (v > cur && !maximum.compare_exchange_weak(cur, v)) {}   // cur refreshed on failure
    };
    {
        std::vector<std::jthread> ts;
        for (int t = 0; t < 4; ++t) ts.emplace_back([&, t] { for (int i = 0; i < 1000; ++i) update_max(t * 1000 + i); });
    }
    std::cout << "CAS max: " << maximum.load() << '\n';

    std::atomic<int> state{0};
    std::jthread waiter{[&] { state.wait(0); std::cout << "woken with state " << state.load() << '\n'; }};
    state.store(1);
    state.notify_one();
    waiter.join();

    int plain[3] = {0, 0, 0};
    {
        std::jthread a{[&] { for (int i = 0; i < 1000; ++i) std::atomic_ref{plain[1]}.fetch_add(1); }};
        std::jthread b{[&] { for (int i = 0; i < 1000; ++i) std::atomic_ref{plain[1]}.fetch_add(1); }};
    }
    std::cout << "atomic_ref on array element: " << plain[1] << '\n';
    std::cout << std::boolalpha << "atomic<long> always lock-free: " << std::atomic<long>::is_always_lock_free << '\n';
}
