#include <condition_variable>
#include <deque>
#include <iostream>
#include <mutex>
#include <optional>
#include <stop_token>
#include <thread>
#include <vector>

template <typename T>
class BlockingQueue {
public:
    void push(T v) {
        { std::lock_guard lock{m_}; q_.push_back(std::move(v)); }   // modify under the lock
        cv_.notify_one();
    }
    std::optional<T> pop() {                                       // nullopt once closed and drained
        std::unique_lock lock{m_};
        cv_.wait(lock, [&] { return !q_.empty() || closed_; });    // predicate handles spurious wakeups
        if (q_.empty()) return std::nullopt;
        T v = std::move(q_.front()); q_.pop_front();
        return v;
    }
    void close() {
        { std::lock_guard lock{m_}; closed_ = true; }
        cv_.notify_all();
    }
private:
    std::mutex m_;
    std::condition_variable cv_;
    std::deque<T> q_;
    bool closed_ = false;
};

int main() {
    BlockingQueue<int> q;
    long long total = 0;
    int consumed = 0;
    std::mutex result_m;
    {
        std::vector<std::jthread> consumers;
        for (int c = 0; c < 3; ++c)
            consumers.emplace_back([&] {
                while (auto block = q.pop()) {
                    std::lock_guard lock{result_m};
                    total += *block; ++consumed;
                }
            });
        std::jthread producer{[&] { for (int i = 1; i <= 1000; ++i) q.push(i); q.close(); }};
    }
    std::cout << "consumed " << consumed << " blocks, total " << total << '\n';

    std::mutex m;
    std::condition_variable_any cv;
    std::jthread waiter{[&](std::stop_token st) {
        std::unique_lock lock{m};
        bool ready = cv.wait(lock, st, [] { return false; });       // wakes on stop request
        std::cout << "waiter woke by stop, predicate=" << std::boolalpha << ready << '\n';
    }};
    waiter.request_stop();
}
