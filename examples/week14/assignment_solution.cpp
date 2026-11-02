#include <array>
#include <atomic>
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <functional>
#include <future>
#include <iostream>
#include <memory>
#include <mutex>
#include <optional>
#include <thread>
#include <vector>

template <typename T, std::size_t N>
class SpscRing {
public:
    bool try_push(const T& v) {
        auto t = tail_.load(std::memory_order_relaxed), next = (t + 1) & (N - 1);
        if (next == head_.load(std::memory_order_acquire)) return false;
        buf_[t] = v; tail_.store(next, std::memory_order_release); return true;
    }
    std::optional<T> try_pop() {
        auto h = head_.load(std::memory_order_relaxed);
        if (h == tail_.load(std::memory_order_acquire)) return std::nullopt;
        T v = buf_[h]; head_.store((h + 1) & (N - 1), std::memory_order_release); return v;
    }
private:
    std::array<T, N> buf_{};
    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
};

class ThreadPool {
public:
    explicit ThreadPool(unsigned n) { for (unsigned i = 0; i < n; ++i) w_.emplace_back([this] { run(); }); }
    ~ThreadPool() { { std::lock_guard l{m_}; stop_ = true; } cv_.notify_all(); }
    std::future<int> submit(std::function<int()> f) {
        auto t = std::make_shared<std::packaged_task<int()>>(std::move(f));
        auto fut = t->get_future();
        { std::lock_guard l{m_}; q_.emplace_back([t] { (*t)(); }); }
        cv_.notify_one();
        return fut;
    }
private:
    void run() {
        for (;;) {
            std::function<void()> j;
            { std::unique_lock l{m_}; cv_.wait(l, [&] { return stop_ || !q_.empty(); });
              if (q_.empty()) return; j = std::move(q_.front()); q_.pop_front(); }
            j();
        }
    }
    std::mutex m_; std::condition_variable cv_; std::deque<std::function<void()>> q_; bool stop_ = false;
    std::vector<std::jthread> w_;
};

int process(int block) { return (block * block) % 1000; }

int main() {
    constexpr int blocks = 10000;
    SpscRing<int, 256> ring;
    std::vector<std::future<int>> futures;
    futures.reserve(blocks);
    {
        ThreadPool pool{4};
        std::jthread producer{[&] { for (int i = 0; i < blocks; ++i) while (!ring.try_push(i)) std::this_thread::yield(); }};
        std::jthread dispatcher{[&] {
            for (int got = 0; got < blocks;) {
                if (auto b = ring.try_pop()) { int v = *b; futures.push_back(pool.submit([v] { return process(v); })); ++got; }
                else std::this_thread::yield();
            }
        }};
        dispatcher.join();
        long long sum = 0;
        for (auto& f : futures) sum += f.get();
        long long expected = 0;
        for (int i = 0; i < blocks; ++i) expected += process(i);
        std::cout << "processed " << futures.size() << " blocks, checksum " << sum
                  << (sum == expected ? " (matches sequential)" : " (MISMATCH)") << '\n';
    }
}
