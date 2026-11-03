HEADERS = {
"threadpool.hpp": r'''
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
''',
"ring_buffer.hpp": r'''
// ring_buffer.hpp — Capstone B: fixed-capacity ring buffers for embedded / real-time code.
// No heap, no exceptions required, constexpr-friendly single-threaded variant,
// and a lock-free SPSC variant safe between an ISR (producer) and the main loop (consumer).
#pragma once
#include <array>
#include <atomic>
#include <cstddef>
#include <new>
#include <optional>
#include <type_traits>
#include <utility>

namespace embedded {

// Single-threaded ring buffer. Usable in constant expressions.
template <typename T, std::size_t N>
class RingBuffer {
    static_assert(N > 0, "capacity must be positive");
    static_assert(std::is_trivially_copyable_v<T> || std::is_nothrow_move_assignable_v<T>,
                  "T must be cheap and safe to move in real-time code");
public:
    using value_type = T;
    enum class Overflow { reject, overwrite_oldest };

    constexpr explicit RingBuffer(Overflow policy = Overflow::reject) noexcept : policy_{policy} {}

    [[nodiscard]] constexpr bool push(const T& v) noexcept(std::is_nothrow_copy_assignable_v<T>) {
        if (full()) {
            if (policy_ == Overflow::reject) return false;
            head_ = next(head_); --size_; ++overwritten_;
        }
        data_[(head_ + size_) % N] = v;
        ++size_;
        return true;
    }
    [[nodiscard]] constexpr std::optional<T> pop() noexcept(std::is_nothrow_move_constructible_v<T>) {
        if (empty()) return std::nullopt;
        T v = std::move(data_[head_]);
        head_ = next(head_); --size_;
        return v;
    }
    [[nodiscard]] constexpr const T* peek() const noexcept { return empty() ? nullptr : &data_[head_]; }
    [[nodiscard]] constexpr const T& operator[](std::size_t i) const noexcept { return data_[(head_ + i) % N]; }  // 0 = oldest
    constexpr void clear() noexcept { head_ = size_ = 0; }

    [[nodiscard]] constexpr std::size_t size() const noexcept { return size_; }
    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return N; }
    [[nodiscard]] constexpr bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] constexpr bool full() const noexcept { return size_ == N; }
    [[nodiscard]] constexpr std::size_t overwritten() const noexcept { return overwritten_; }

    // Minimal forward iteration, oldest to newest
    class const_iterator {
    public:
        using value_type = T; using difference_type = std::ptrdiff_t;
        constexpr const_iterator() = default;
        constexpr const_iterator(const RingBuffer* rb, std::size_t i) : rb_{rb}, i_{i} {}
        constexpr const T& operator*() const { return (*rb_)[i_]; }
        constexpr const_iterator& operator++() { ++i_; return *this; }
        constexpr const_iterator operator++(int) { auto t = *this; ++i_; return t; }
        constexpr bool operator==(const const_iterator&) const = default;
    private:
        const RingBuffer* rb_ = nullptr;
        std::size_t i_ = 0;
    };
    [[nodiscard]] constexpr const_iterator begin() const noexcept { return {this, 0}; }
    [[nodiscard]] constexpr const_iterator end() const noexcept { return {this, size_}; }

private:
    static constexpr std::size_t next(std::size_t i) noexcept { return (i + 1) % N; }
    std::array<T, N> data_{};
    std::size_t head_ = 0, size_ = 0, overwritten_ = 0;
    Overflow policy_;
};

// Lock-free single-producer / single-consumer ring (e.g. ISR -> main loop).
// Capacity N must be a power of two; usable capacity is N - 1.
template <typename T, std::size_t N>
class SpscRing {
    static_assert(N >= 2 && (N & (N - 1)) == 0, "N must be a power of two");
    static_assert(std::is_trivially_copyable_v<T>, "keep ISR payloads trivially copyable");
    static_assert(std::atomic<std::size_t>::is_always_lock_free, "needs lock-free atomics on this target");
public:
    [[nodiscard]] bool push(const T& v) noexcept {            // producer only
        const auto t = tail_.load(std::memory_order_relaxed);
        const auto n = (t + 1) & (N - 1);
        if (n == head_.load(std::memory_order_acquire)) { dropped_.fetch_add(1, std::memory_order_relaxed); return false; }
        buf_[t] = v;
        tail_.store(n, std::memory_order_release);
        return true;
    }
    [[nodiscard]] std::optional<T> pop() noexcept {           // consumer only
        const auto h = head_.load(std::memory_order_relaxed);
        if (h == tail_.load(std::memory_order_acquire)) return std::nullopt;
        T v = buf_[h];
        head_.store((h + 1) & (N - 1), std::memory_order_release);
        return v;
    }
    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return N - 1; }
    [[nodiscard]] std::size_t dropped() const noexcept { return dropped_.load(std::memory_order_relaxed); }
private:
    std::array<T, N> buf_{};
    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
    alignas(64) std::atomic<std::size_t> dropped_{0};
};

}  // namespace embedded
''',
}

CAPSTONES = {
"index": dict(md="""
# Capstones

Two projects pull the course together. Each comes with a complete reference implementation (a header-only
library), a test program, and a demo — all compiled and run by the same checker as every lesson example, on
GCC 14 and Clang, with sanitizers in CI.

| Capstone | Builds on | You'll practise |
|---|---|---|
| [A: Concurrent task library + CLI](threadpool.md) | Weeks 4–5, 9, 13–14 | RAII, futures, condition variables, back-pressure, shutdown, testing under TSan |
| [B: Embedded ring buffer](ringbuffer.md) | Weeks 3, 7–8, 10, 14, 16 | templates, `constexpr`, no-heap design, iterators, lock-free SPSC |

## How to approach them (Andrew Ng-style)

1. **Read the spec and write the tests first** — or at least list the cases.
2. Build the simplest version that passes one test. Then the next.
3. Run under sanitizers early (`-fsanitize=address,undefined`, and separately `-fsanitize=thread`).
4. Only then compare with the reference implementation. It's fine — expected, even — if yours differs.

Honest note: Capstone A's concurrency is the hardest thing in this course. If a test hangs or TSan
complains, that's not failure; it's the learning.
"""),
"threadpool": dict(md="""
# Capstone A: A concurrent task library with a CLI

## The problem

You have a batch of jobs — say, checksumming files or rendering audio stems. You want a reusable library
that runs them on N threads, returns results through futures, propagates exceptions, applies
**back-pressure** (a bounded queue, so a fast producer can't exhaust memory), reports statistics, and shuts
down cleanly. Then a small command-line tool on top.

## Requirements

1. `ThreadPool(threads, max_queue)` — validates arguments.
2. `submit(f, args...)` → `std::future<R>`; blocks while the queue is full; throws after shutdown.
3. `try_submit(...)` → `std::optional<std::future<R>>`; never blocks.
4. Exceptions inside tasks reach the caller via `future::get()`; the pool keeps running.
5. `wait_idle()` waits until all submitted work is done.
6. `shutdown(drain)` finishes queued work; `shutdown(discard)` drops it (futures report `broken_promise`).
7. `stats()` returns submitted / completed / failed / rejected counts.
8. Tests pass under ThreadSanitizer.

## The library

{{header:threadpool.hpp}}

Design notes:

- **Three condition variables**: `not_empty_` (workers wait for jobs), `not_full_` (producers wait for
  space), `idle_` (`wait_idle`). Separate CVs avoid waking the wrong kind of waiter.
- Jobs run **outside the lock**.
- A task's exception is counted (for `stats().failed`) and rethrown into its `packaged_task`, which stores
  it in the future — so worker threads never see it.
- `shutdown` is idempotent and called from the destructor (RAII).

## Tests

{{file:tests}}

## The CLI

`taskrun [--threads N] [--jobs M] [--queue Q]` computes a CPU-bound job set and prints a summary. With no
arguments it uses defaults (which is how the checker runs it).

{{file:cli}}

## Extensions

- Work stealing with per-worker deques.
- Task priorities, or cancellation with `std::stop_token`.
- Replace `std::function` with `std::move_only_function` (C++23) to avoid the `shared_ptr`.
- Expose the pool as a `std::execution` scheduler (C++26, via stdexec).
""", files={
"tests": {"san": ["thread"], "code": r'''
#include "threadpool.hpp"

#include <atomic>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

int failures = 0;
#define CHECK(c) do { if (!(c)) { ++failures; std::cout << "  FAILED line " << __LINE__ << ": " #c "\n"; } } while (0)

void test_results() {
    tasklib::ThreadPool pool{4};
    std::vector<std::future<int>> fs;
    for (int i = 0; i < 100; ++i) fs.push_back(pool.submit([](int x) { return x * 2; }, i));
    int sum = 0;
    for (auto& f : fs) sum += f.get();
    CHECK(sum == 9900);
}

void test_exceptions_propagate() {
    tasklib::ThreadPool pool{2};
    auto bad = pool.submit([]() -> int { throw std::runtime_error{"boom"}; });
    bool caught = false;
    try { (void)bad.get(); } catch (const std::runtime_error& e) { caught = std::string{e.what()} == "boom"; }
    CHECK(caught);
    CHECK(pool.submit([] { return 7; }).get() == 7);       // pool still works
    CHECK(pool.stats().failed == 1);
}

void test_backpressure_and_try_submit() {
    tasklib::ThreadPool pool{1, 2};
    std::atomic<bool> release{false};
    auto blocker = pool.submit([&] { while (!release) std::this_thread::yield(); });
    while (pool.stats().submitted == 0) {}
    // worker is busy; queue capacity is 2
    std::vector<std::future<void>> queued;
    for (int i = 0; i < 10; ++i)
        if (auto f = pool.try_submit([] {})) queued.push_back(std::move(*f));
    CHECK(queued.size() <= 2);
    CHECK(pool.stats().rejected >= 8);
    release = true;
    blocker.get();
    for (auto& f : queued) f.get();
}

void test_wait_idle_and_stats() {
    tasklib::ThreadPool pool{3};
    std::atomic<int> done{0};
    for (int i = 0; i < 50; ++i) (void)pool.submit([&] { ++done; });
    pool.wait_idle();
    CHECK(done == 50);
    auto s = pool.stats();
    CHECK(s.submitted == 50 && s.completed == 50 && s.failed == 0);
}

void test_shutdown() {
    tasklib::ThreadPool pool{2};
    std::atomic<int> ran{0};
    for (int i = 0; i < 20; ++i) (void)pool.submit([&] { ++ran; });
    pool.shutdown(tasklib::ThreadPool::Shutdown::drain);
    CHECK(ran == 20);
    bool threw = false;
    try { (void)pool.submit([] {}); } catch (const std::runtime_error&) { threw = true; }
    CHECK(threw);

    tasklib::ThreadPool p2{1};
    std::atomic<bool> go{false};
    auto first = p2.submit([&] { while (!go) std::this_thread::yield(); });
    auto dropped = p2.submit([] { return 1; });
    std::thread releaser{[&] { std::this_thread::sleep_for(std::chrono::milliseconds{20}); go = true; }};
    p2.shutdown(tasklib::ThreadPool::Shutdown::discard);
    releaser.join();
    first.get();
    bool broken = false;
    try { (void)dropped.get(); } catch (const std::future_error& e) { broken = e.code() == std::future_errc::broken_promise; }
    CHECK(broken || dropped.valid() == false);
}

void test_bad_arguments() {
    bool threw = false;
    try { tasklib::ThreadPool p{0}; } catch (const std::invalid_argument&) { threw = true; }
    CHECK(threw);
}

int main() {
    struct T { const char* name; void (*fn)(); };
    for (auto [name, fn] : {T{"results", test_results}, T{"exceptions propagate", test_exceptions_propagate},
                            T{"back-pressure / try_submit", test_backpressure_and_try_submit},
                            T{"wait_idle and stats", test_wait_idle_and_stats}, T{"shutdown modes", test_shutdown},
                            T{"bad arguments", test_bad_arguments}}) {
        std::cout << "[ RUN ] " << name << '\n';
        fn();
    }
    std::cout << (failures == 0 ? "ALL TESTS PASSED\n" : "SOME TESTS FAILED\n");
    return failures == 0 ? 0 : 1;
}
'''},
"cli": {"san": ["thread"], "code": r'''
#include "threadpool.hpp"

#include <charconv>
#include <cstdint>
#include <iostream>
#include <string_view>
#include <vector>

struct Options { unsigned threads = 4; int jobs = 32; std::size_t queue = 8; };

bool parse_uint(std::string_view s, auto& out) {
    auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), out);
    return ec == std::errc{} && p == s.data() + s.size() && out > 0;
}

bool parse_args(int argc, char** argv, Options& o) {
    for (int i = 1; i < argc; ++i) {
        std::string_view a = argv[i];
        if (i + 1 >= argc) { std::cerr << "missing value for " << a << '\n'; return false; }
        std::string_view v = argv[++i];
        bool ok = a == "--threads" ? parse_uint(v, o.threads)
                : a == "--jobs"    ? parse_uint(v, o.jobs)
                : a == "--queue"   ? parse_uint(v, o.queue) : false;
        if (!ok) { std::cerr << "bad option " << a << ' ' << v << '\n'; return false; }
    }
    return true;
}

std::uint64_t collatz_steps(std::uint64_t n) {
    std::uint64_t steps = 0;
    while (n != 1) { n = (n % 2) ? 3 * n + 1 : n / 2; ++steps; }
    return steps;
}

int main(int argc, char** argv) {
    Options opt;
    if (!parse_args(argc, argv, opt)) {
        std::cerr << "usage: taskrun [--threads N] [--jobs M] [--queue Q]\n";
        return 2;
    }
    tasklib::ThreadPool pool{opt.threads, opt.queue};
    std::vector<std::future<std::uint64_t>> results;
    for (int j = 0; j < opt.jobs; ++j)
        results.push_back(pool.submit([j] {                  // blocks when the queue is full
            std::uint64_t best = 0;
            for (std::uint64_t n = 1 + static_cast<std::uint64_t>(j) * 1000; n <= static_cast<std::uint64_t>(j + 1) * 1000; ++n)
                best = std::max(best, collatz_steps(n));
            return best;
        }));
    std::uint64_t overall = 0;
    for (auto& f : results) overall = std::max(overall, f.get());
    pool.wait_idle();
    auto s = pool.stats();
    std::cout << "threads=" << pool.thread_count() << " jobs=" << opt.jobs << " queue=" << opt.queue << '\n';
    std::cout << "longest Collatz chain below " << opt.jobs * 1000 << ": " << overall << " steps\n";
    std::cout << "stats: submitted=" << s.submitted << " completed=" << s.completed
              << " failed=" << s.failed << " rejected=" << s.rejected << '\n';
}
'''},
}),
"ringbuffer": dict(md="""
# Capstone B: An embedded fixed-capacity ring buffer

## The problem

A microcontroller samples a sensor in an interrupt at 8 kHz; the main loop filters and transmits the data.
You need a buffer that: never allocates, has bounded and predictable timing, can be used in `constexpr`
code and tests, supports an overwrite-oldest policy for "latest N readings" use cases, and has a lock-free
variant for the ISR→main-loop hand-off.

## Requirements

1. `RingBuffer<T, N>`: `push` / `pop` / `peek` / indexing (0 = oldest) / iteration, `full`, `empty`,
   `clear`; overflow policy **reject** or **overwrite oldest** (with a counter).
2. All operations `noexcept` for trivially copyable `T`, and usable in constant expressions.
3. `SpscRing<T, N>`: lock-free single-producer/single-consumer, power-of-two capacity, drop counter.
4. No heap allocation anywhere; `static_assert`s for misuse (zero capacity, non-power-of-two, non-trivial
   ISR payloads, non-lock-free atomics).
5. Tests run under ASan/UBSan; the SPSC test runs under TSan.

## The library

{{header:ring_buffer.hpp}}

Design notes:

- The single-threaded buffer stores `head` and `size` (not head/tail), so it uses all N slots. The SPSC
  version must keep one slot empty, because head and tail are written by different threads.
- `constexpr` everything: the tests below include `static_assert`-based tests that run inside the compiler.
- On a real MCU you'd check `is_always_lock_free` for `std::size_t` atomics (some 8-bit targets fail), or
  use a critical section instead.

## Tests

{{file:tests}}

## Demo: a simulated sensor ISR

A thread stands in for the interrupt; the main loop drains the SPSC ring and keeps a moving average of the
last 8 readings in an overwrite-oldest `RingBuffer`.

{{file:demo}}

## Extensions

- Bulk `push_n`/`pop_n` with `std::span` for DMA transfers.
- A `std::ranges`-compatible random-access iterator.
- Port to a real board (e.g. an STM32 with `arm-none-eabi-g++ -fno-exceptions -fno-rtti`) and measure
  cycles per push.
- Replace your own buffer with C++26 `std::inplace_vector` where a FIFO isn't needed.
"""
, files={
"tests": {"san": ["address", "undefined"], "code": r'''
#include "ring_buffer.hpp"

#include <iostream>
#include <string>

using embedded::RingBuffer;

// ---- compile-time tests: run by the compiler itself ----
constexpr bool fifo_order() {
    RingBuffer<int, 3> rb;
    (void)rb.push(1); (void)rb.push(2); (void)rb.push(3);
    return !rb.push(4) && rb.pop() == 1 && rb.pop() == 2 && rb.pop() == 3 && !rb.pop();
}
static_assert(fifo_order());

constexpr bool overwrite_policy() {
    RingBuffer<int, 3> rb{RingBuffer<int, 3>::Overflow::overwrite_oldest};
    for (int i = 1; i <= 5; ++i) (void)rb.push(i);
    return rb.size() == 3 && rb[0] == 3 && rb[2] == 5 && rb.overwritten() == 2;
}
static_assert(overwrite_policy());

constexpr int sum_by_iteration() {
    RingBuffer<int, 4> rb;
    for (int i = 1; i <= 4; ++i) (void)rb.push(i);
    (void)rb.pop(); (void)rb.push(10);                    // wrapped
    int s = 0; for (int v : rb) s += v;
    return s;
}
static_assert(sum_by_iteration() == 2 + 3 + 4 + 10);
static_assert(sizeof(RingBuffer<std::uint8_t, 16>) < 64, "no hidden heap pointers or bloat");

int failures = 0;
#define CHECK(c) do { if (!(c)) { ++failures; std::cout << "  FAILED line " << __LINE__ << ": " #c "\n"; } } while (0)

int main() {
    std::cout << "[ RUN ] run-time wrap-around stress\n";
    RingBuffer<int, 7> rb;
    int next_in = 0, next_out = 0;
    for (int round = 0; round < 1000; ++round) {
        for (int k = 0; k < round % 5; ++k) if (rb.push(next_in)) ++next_in;
        for (int k = 0; k < round % 3; ++k) if (auto v = rb.pop()) { CHECK(*v == next_out); ++next_out; }
        CHECK(rb.size() == static_cast<std::size_t>(next_in - next_out));
    }

    std::cout << "[ RUN ] peek / clear\n";
    RingBuffer<int, 2> small;
    CHECK(small.peek() == nullptr);
    (void)small.push(42);
    CHECK(small.peek() && *small.peek() == 42);
    small.clear();
    CHECK(small.empty());

    std::cout << "[ RUN ] non-trivial element type\n";
    RingBuffer<std::string, 2> names;
    CHECK(names.push("kick"));
    CHECK(names.push("snare"));
    CHECK(!names.push("hat"));
    CHECK(names.pop() == std::string{"kick"});

    std::cout << "[ RUN ] SPSC single-threaded semantics\n";
    embedded::SpscRing<int, 4> spsc;
    CHECK(spsc.push(1) && spsc.push(2) && spsc.push(3));
    CHECK(!spsc.push(4));                                // capacity N-1 = 3
    CHECK(spsc.dropped() == 1);
    CHECK(spsc.pop() == 1);

    std::cout << "compile-time tests: 4 passed (static_assert)\n";
    std::cout << (failures == 0 ? "ALL TESTS PASSED\n" : "SOME TESTS FAILED\n");
    return failures == 0 ? 0 : 1;
}
'''},
"demo": {"san": ["thread"], "code": r'''
#include "ring_buffer.hpp"

#include <atomic>
#include <cstdint>
#include <iostream>
#include <thread>

struct Sample { std::uint32_t seq; std::int16_t value; };

int main() {
    embedded::SpscRing<Sample, 64> isr_to_main;
    std::atomic<bool> sensor_done{false};
    constexpr std::uint32_t total = 5000;

    std::thread isr{[&] {                                    // stands in for the 8 kHz sampling interrupt
        for (std::uint32_t i = 0; i < total; ++i) {
            Sample s{i, static_cast<std::int16_t>((i % 100) - 50)};
            while (!isr_to_main.push(s)) std::this_thread::yield();   // a real ISR would drop instead
        }
        sensor_done.store(true, std::memory_order_release);
    }};

    embedded::RingBuffer<std::int16_t, 8> window{embedded::RingBuffer<std::int16_t, 8>::Overflow::overwrite_oldest};
    std::uint32_t received = 0, expected_seq = 0;
    bool in_order = true;
    for (;;) {
        if (auto s = isr_to_main.pop()) {
            in_order = in_order && s->seq == expected_seq++;
            (void)window.push(s->value);
            ++received;
        } else if (sensor_done.load(std::memory_order_acquire)) {
            if (auto last = isr_to_main.pop()) { in_order = in_order && last->seq == expected_seq++; (void)window.push(last->value); ++received; continue; }
            break;
        } else {
            std::this_thread::yield();
        }
    }
    isr.join();
    int sum = 0;
    for (auto v : window) sum += v;
    std::cout << "received " << received << " samples, in order: " << std::boolalpha << in_order << '\n';
    std::cout << "last 8 readings average: " << static_cast<double>(sum) / static_cast<double>(window.size()) << '\n';
    std::cout << "window overwrote " << window.overwritten() << " older readings; no heap used\n";
}
'''},
}),
}
