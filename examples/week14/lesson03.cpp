#include <condition_variable>
#include <deque>
#include <functional>
#include <future>
#include <iostream>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <type_traits>
#include <vector>

class ThreadPool {
public:
    explicit ThreadPool(unsigned n) {
        for (unsigned i = 0; i < n; ++i) workers_.emplace_back([this] { run(); });
    }
    ~ThreadPool() {
        { std::lock_guard lock{m_}; stopping_ = true; }
        cv_.notify_all();
    }                                                       // jthreads join after draining
    template <typename F, typename... Args>
    auto submit(F&& f, Args&&... args) -> std::future<std::invoke_result_t<F, Args...>> {
        using R = std::invoke_result_t<F, Args...>;
        auto task = std::make_shared<std::packaged_task<R()>>(
            [f = std::forward<F>(f), ... a = std::forward<Args>(args)]() mutable { return std::invoke(f, a...); });
        auto fut = task->get_future();
        {
            std::lock_guard lock{m_};
            if (stopping_) throw std::runtime_error{"pool is stopping"};
            q_.emplace_back([task] { (*task)(); });
        }
        cv_.notify_one();
        return fut;
    }
private:
    void run() {
        for (;;) {
            std::function<void()> job;
            {
                std::unique_lock lock{m_};
                cv_.wait(lock, [&] { return stopping_ || !q_.empty(); });
                if (q_.empty()) return;                     // stopping and drained
                job = std::move(q_.front()); q_.pop_front();
            }
            job();                                          // run outside the lock
        }
    }
    std::mutex m_;
    std::condition_variable cv_;
    std::deque<std::function<void()>> q_;
    bool stopping_ = false;
    std::vector<std::jthread> workers_;                     // declared last: destroyed (joined) first
};

int main() {
    std::vector<std::future<long long>> results;
    {
        ThreadPool pool{4};
        for (int i = 1; i <= 8; ++i)
            results.push_back(pool.submit([](int n) { long long s = 0; for (int k = 1; k <= n * 1000; ++k) s += k; return s; }, i));
        auto failing = pool.submit([] { throw std::runtime_error{"bad input"}; return 0; });
        try { (void)failing.get(); } catch (const std::exception& e) { std::cout << "task failed: " << e.what() << '\n'; }
        auto hello = pool.submit([](const std::string& who) { return "hello " + who; }, std::string{"pool"});
        std::cout << hello.get() << '\n';
    }
    for (std::size_t i = 0; i < results.size(); ++i) std::cout << "sum(1.." << (i + 1) * 1000 << ") = " << results[i].get() << '\n';
}
