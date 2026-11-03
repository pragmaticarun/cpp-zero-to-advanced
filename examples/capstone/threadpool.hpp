// threadpool.hpp — Capstone A: a small concurrent task library.
// Bounded queue (back-pressure), futures for results, stats, graceful or immediate shutdown.
#pragma once
#include <atomic>
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

namespace tasklib {

struct Stats {
    std::size_t submitted = 0, completed = 0, failed = 0, rejected = 0;
};

class ThreadPool {
public:
    enum class Shutdown { drain, discard };

    explicit ThreadPool(unsigned threads, std::size_t max_queue = 1024) : max_queue_{max_queue} {
        if (threads == 0) throw std::invalid_argument{"threads must be > 0"};
        if (max_queue == 0) throw std::invalid_argument{"max_queue must be > 0"};
        workers_.reserve(threads);
        for (unsigned i = 0; i < threads; ++i) workers_.emplace_back([this] { worker_loop(); });
    }
    ThreadPool(const ThreadPool&) = delete;
    ThreadPool& operator=(const ThreadPool&) = delete;
    ~ThreadPool() { shutdown(Shutdown::drain); }

    // Blocks while the queue is full (back-pressure). Throws if the pool is shut down.
    template <typename F, typename... Args>
    [[nodiscard]] auto submit(F&& f, Args&&... args) -> std::future<std::invoke_result_t<F, Args...>> {
        auto [job, fut] = make_job(std::forward<F>(f), std::forward<Args>(args)...);
        std::unique_lock lock{m_};
        not_full_.wait(lock, [&] { return stopping_ || q_.size() < max_queue_; });
        if (stopping_) { ++stats_.rejected; throw std::runtime_error{"pool is shut down"}; }
        q_.push_back(std::move(job));
        ++stats_.submitted;
        lock.unlock();
        not_empty_.notify_one();
        return std::move(fut);
    }

    // Never blocks: returns nullopt if the queue is full or the pool is stopping.
    template <typename F, typename... Args>
    [[nodiscard]] auto try_submit(F&& f, Args&&... args) -> std::optional<std::future<std::invoke_result_t<F, Args...>>> {
        auto [job, fut] = make_job(std::forward<F>(f), std::forward<Args>(args)...);
        {
            std::lock_guard lock{m_};
            if (stopping_ || q_.size() >= max_queue_) { ++stats_.rejected; return std::nullopt; }
            q_.push_back(std::move(job));
            ++stats_.submitted;
        }
        not_empty_.notify_one();
        return std::move(fut);
    }

    // Wait until every submitted task has finished.
    void wait_idle() {
        std::unique_lock lock{m_};
        idle_.wait(lock, [&] { return q_.empty() && active_ == 0; });
    }

    void shutdown(Shutdown mode) {
        std::deque<Job> dropped;
        {
            std::lock_guard lock{m_};
            if (stopping_ && workers_.empty()) return;
            stopping_ = true;
            if (mode == Shutdown::discard) dropped.swap(q_);   // their futures get broken_promise
        }
        not_empty_.notify_all();
        not_full_.notify_all();
        for (auto& w : workers_) if (w.joinable()) w.join();
        workers_.clear();
    }

    [[nodiscard]] Stats stats() const {
        std::lock_guard lock{m_};
        Stats s = stats_;
        s.failed = task_failures_.load(std::memory_order_relaxed);
        return s;
    }
    [[nodiscard]] std::size_t thread_count() const { return workers_.size(); }

private:
    struct Job { std::function<void()> run; };

    template <typename F, typename... Args>
    auto make_job(F&& f, Args&&... args) {
        using R = std::invoke_result_t<F, Args...>;
        auto task = std::make_shared<std::packaged_task<R()>>(
            [this, fn = std::forward<F>(f), ... a = std::forward<Args>(args)]() mutable -> R {
                try { return std::invoke(fn, a...); }
                catch (...) { task_failures_.fetch_add(1, std::memory_order_relaxed); throw; }  // rethrown into the future
            });
        std::future<R> fut = task->get_future();
        Job job{[task] { (*task)(); }};                    // exceptions are stored in the future
        return std::pair{std::move(job), std::move(fut)};
    }

    void worker_loop() {
        for (;;) {
            Job job;
            {
                std::unique_lock lock{m_};
                not_empty_.wait(lock, [&] { return stopping_ || !q_.empty(); });
                if (q_.empty()) return;                     // stopping and drained
                job = std::move(q_.front());
                q_.pop_front();
                ++active_;
            }
            not_full_.notify_one();
            job.run();                                       // never throws: packaged_task captures exceptions
            {
                std::lock_guard lock{m_};
                --active_;
                ++stats_.completed;
                if (q_.empty() && active_ == 0) idle_.notify_all();
            }
        }
    }

    mutable std::mutex m_;
    std::condition_variable not_empty_, not_full_, idle_;
    std::deque<Job> q_;
    std::size_t max_queue_;
    std::size_t active_ = 0;
    bool stopping_ = false;
    Stats stats_;
    std::atomic<std::size_t> task_failures_{0};
    std::vector<std::thread> workers_;
};

}  // namespace tasklib
