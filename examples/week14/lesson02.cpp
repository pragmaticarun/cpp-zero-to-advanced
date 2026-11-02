#include <array>
#include <atomic>
#include <cstddef>
#include <iostream>
#include <optional>
#include <thread>

template <typename T, std::size_t N>
class SpscRing {
    static_assert(N >= 2 && (N & (N - 1)) == 0, "capacity must be a power of two");
public:
    bool try_push(const T& v) {                               // producer thread only
        auto t = tail_.load(std::memory_order_relaxed);
        auto next = (t + 1) & (N - 1);
        if (next == head_.load(std::memory_order_acquire)) return false;   // full
        buf_[t] = v;
        tail_.store(next, std::memory_order_release);          // publish
        return true;
    }
    std::optional<T> try_pop() {                              // consumer thread only
        auto h = head_.load(std::memory_order_relaxed);
        if (h == tail_.load(std::memory_order_acquire)) return std::nullopt;   // empty
        T v = buf_[h];
        head_.store((h + 1) & (N - 1), std::memory_order_release);  // hand slot back
        return v;
    }
    static constexpr std::size_t capacity() { return N - 1; }
private:
    std::array<T, N> buf_{};
    alignas(64) std::atomic<std::size_t> head_{0};            // separate cache lines: no false sharing
    alignas(64) std::atomic<std::size_t> tail_{0};
};

int main() {
    SpscRing<int, 1024> ring;
    constexpr int count = 200000;
    long long sum = 0;
    bool in_order = true;
    {
        std::jthread producer{[&] {
            for (int i = 1; i <= count; ++i) while (!ring.try_push(i)) std::this_thread::yield();
        }};
        std::jthread consumer{[&] {
            int expected = 1;
            while (expected <= count) {
                if (auto v = ring.try_pop()) { in_order = in_order && *v == expected; sum += *v; ++expected; }
                else std::this_thread::yield();
            }
        }};
    }
    std::cout << "received " << count << " items in order: " << std::boolalpha << in_order << ", sum " << sum << '\n';
    std::cout << "usable capacity " << SpscRing<int, 1024>::capacity() << '\n';
}
