T = {"san": ["thread"]}
WEEK = dict(num=14, title="Concurrency II: atomics, lock-free code, thread pools, and coroutines", intro="""
Last week used locks. This week goes underneath them — atomics and the C++ memory model — then builds two
real components (a lock-free single-producer/single-consumer queue and a thread pool, both feeding the
capstones), and finishes with coroutines, C++20's machinery for writing asynchronous code that reads like
sequential code. This is the hardest week of the course. Go slowly, and lean on ThreadSanitizer.
""", lessons=[
dict(title="Atomics and the memory model", std="C++20", minutes=15, area="Concurrency: atomics",
features=[("`std::atomic<T>`, `load`, `store`, `exchange`, `fetch_add`", "C++11"), ("`compare_exchange_weak` / `_strong`", "C++11"), ("Memory orders: `seq_cst`, `acquire`, `release`, `acq_rel`, `relaxed`", "C++11"), ("Happens-before and synchronizes-with", "C++11"), ("`std::atomic_ref`", "C++20"), ("`atomic::wait` / `notify_one` / `notify_all`", "C++20"), ("`std::atomic_flag`, `is_lock_free`, `is_always_lock_free`", "C++11/17"), ("`std::atomic<std::shared_ptr<T>>`, `atomic<float>` arithmetic", "C++20"), ("`volatile` is not for threads", "—")],
why="""
Modern CPUs and compilers reorder memory operations aggressively for speed. On one thread you never notice.
Across threads, it means writing `data = 42; ready = true;` doesn't guarantee another thread that sees
`ready == true` also sees `data == 42`. The memory model tells you exactly what's guaranteed — and atomics
with the right memory order give you those guarantees without a mutex.
""",
body="""
## Atomics: indivisible operations

`std::atomic<int> n; ++n;` is a single indivisible read-modify-write — no lost updates, no data race.
`compare_exchange_weak(expected, desired)` is the building block of lock-free algorithms: "if the value is
still `expected`, set it to `desired`; otherwise tell me the current value".

## Memory order, intuitively

- **`seq_cst`** (default): all threads agree on one global order of all seq_cst operations. Easiest to
  reason about. Use it unless you've measured a need.
- **`release` store + `acquire` load**: the publishing pattern. Everything written before the release
  store is visible to a thread whose acquire load reads that store. This is "message passing".
- **`relaxed`**: atomic, but no ordering of *other* memory. Fine for counters and statistics.

```mermaid
sequenceDiagram
    participant P as Producer
    participant C as Consumer
    P->>P: data = 42 (plain write)
    P->>C: ready.store(true, release)
    C->>C: ready.load(acquire) == true
    C->>C: read data -> guaranteed 42
```

{{ex}}

## `volatile` is not a synchronization tool

`volatile` stops the compiler from optimizing away accesses (for memory-mapped hardware registers — Week 16)
but provides no atomicity and no inter-thread ordering. Using it for flags between threads is a data race.

## C++20 additions

`atomic::wait(old)` blocks until the value changes (efficient, futex-based), `notify_one/all` wakes waiters.
`std::atomic_ref` performs atomic operations on a plain object you don't own (e.g. inside an array).

!!! warning "Honest advice"
    Weaker orders than `seq_cst` are an expert tool. A wrong `relaxed` can pass all tests on x86 (strongly
    ordered hardware) and fail on ARM. If you use them, document *why* each one is correct.
""",
files={"": r'''
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
''', **T},
takeaways=["Atomics make single operations indivisible; `compare_exchange` is the lock-free building block.",
"Release/acquire pairs publish data from one thread to another.",
"`relaxed` is fine for independent counters; default to `seq_cst` otherwise.",
"`volatile` is not for threading; C++20 adds `wait`/`notify` and `atomic_ref`."],
quiz=[("Why might `ready.store(true, relaxed)` be insufficient for publishing `data`?", "Relaxed provides no ordering of other memory, so the consumer may see `ready == true` but a stale `data`."),
("Why does `compare_exchange_weak` sit in a loop?", "It can fail spuriously and fails when another thread changed the value; on failure it updates `expected`, so you retry."),
("Is `volatile bool flag` a correct way to signal between threads?", "No — it's still a data race (UB) with no ordering guarantees; use `std::atomic<bool>`.")]),

dict(title="A lock-free single-producer/single-consumer ring buffer", std="C++20", minutes=14, area="Concurrency: lock-free",
features=[("Lock-free vs wait-free vs obstruction-free", "—"), ("SPSC ring buffer with acquire/release indices", "C++11"), ("`std::hardware_destructive_interference_size` and false sharing", "C++17"), ("`alignas` for cache-line separation", "C++11"), ("The ABA problem (concept)", "—")],
why="""
The audio callback (real-time, can't block) receives samples from the decoder thread. A mutex could block
the callback if the decoder holds it while being descheduled — an audible glitch. The standard answer is a
**single-producer single-consumer (SPSC) lock-free ring buffer**: fixed capacity, no allocation, no locks,
and only acquire/release atomics. It's also the heart of the embedded capstone.
""",
body="""
## Design

A fixed array plus two indices: `head` (written only by the consumer) and `tail` (written only by the
producer). Because each index has a single writer, we don't need CAS — just loads and stores with the right
ordering:

- Producer: write the slot, then `tail.store(next, release)` — publishes the element.
- Consumer: `tail.load(acquire)` to see published elements, read the slot, then `head.store(next, release)`
  to hand the slot back.

We keep one slot empty to distinguish "full" from "empty", and use a power-of-two capacity so wrap-around
is a cheap mask.

{{ex}}

## False sharing

If `head` and `tail` share a cache line, every write by one core invalidates the other core's copy, even
though they touch different variables. Put them on separate cache lines with `alignas(64)` (or
`std::hardware_destructive_interference_size` where available).

## Beyond SPSC

Multi-producer/multi-consumer lock-free queues need CAS and run into the **ABA problem** (a value changes
A→B→A and CAS wrongly succeeds) and safe memory reclamation (hazard pointers, RCU — `std::hazard_pointer`
and `std::rcu` are coming in C++26). Use a well-tested library (e.g. moodycamel, Folly, Boost.Lockfree)
rather than rolling your own.
""",
files={"": r'''
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
''', **T},
takeaways=["Single-writer indices + acquire/release make an SPSC ring buffer lock-free without CAS.",
"Keep one slot empty to tell full from empty; power-of-two sizes make wrap-around a mask.",
"Separate hot atomics onto different cache lines to avoid false sharing.",
"MPMC lock-free structures face ABA and reclamation problems — use proven libraries."],
quiz=[("Why doesn't the SPSC queue need compare-exchange?", "Each index has exactly one writer thread, so plain atomic stores suffice."),
("What would happen if the producer stored `tail` before writing the slot?", "The consumer could see the new tail and read a slot that hasn't been written yet."),
("What is false sharing?", "Independent variables on the same cache line causing cache-line ping-pong between cores when written.")]),

dict(title="Building a thread pool", std="C++20", minutes=14, area="Concurrency: patterns",
features=[("Thread pool design: work queue, workers, shutdown", "—"), ("Returning results with `std::packaged_task` + `std::future`", "C++11"), ("Type-erased tasks (`std::function` / move-only wrappers)", "C++11/23"), ("Graceful shutdown and exception safety", "—"), ("Work stealing (concept)", "—")],
why="""
Creating a thread per task costs tens of microseconds and unbounded threads thrash the machine. A **thread
pool** creates N workers once and feeds them tasks through a queue. It's the most-used concurrency component
in real systems — and the core of the first capstone. Let's build a small, correct one.
""",
body="""
## Design

- A `std::deque` of tasks guarded by a mutex + condition variable (Week 13).
- N `std::jthread` workers loop: wait for a task or stop, run it.
- `submit(f, args...)` wraps the call in a `std::packaged_task`, pushes it, and returns a `std::future`.
- The destructor stops accepting work, drains the queue, and joins.

Because `packaged_task` is move-only and `std::function` requires copyable callables, we hold it via
`std::shared_ptr` (portable everywhere); with C++23 `std::move_only_function` you can store it directly.

!!! note "Why CI doesn't run this one under ThreadSanitizer"
    GCC 14's TSan reports a false "data race" in `std::exception_ptr`'s reference count when an exception
    travels through a future: the count is updated inside the prebuilt (uninstrumented) `libstdc++.so`,
    so TSan can't see its atomics. It's a tooling limitation, not a bug in the pool. The capstone's tests
    run under TSan with Clang.

{{ex}}

## Things the simple pool doesn't do

- **Work stealing**: per-worker deques where idle workers steal from busy ones (reduces contention).
- **Priorities, cancellation, back-pressure** (bounded queue).
- **Tasks waiting on other tasks** inside the pool can deadlock if all workers block — a classic trap.

The capstone extends this pool with a bounded queue, statistics, and tests.
""",
files={"": r'''
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
''', "san": []},
takeaways=["A thread pool reuses N workers fed by a mutex/condvar queue.",
"`packaged_task` + `future` returns values and exceptions from tasks.",
"Run tasks outside the lock; drain and join on shutdown (member order matters!).",
"Watch for tasks that block on other tasks in the same pool — deadlock."],
quiz=[("Why is `workers_` declared last in the class?", "Members are destroyed in reverse order, so the jthreads join first, while the mutex, condvar and queue they use still exist."),
("Why wrap `packaged_task` in a `shared_ptr`?", "`std::function` requires a copyable callable and `packaged_task` is move-only."),
("How can a pool with 4 workers deadlock?", "If 4 tasks each wait on futures of tasks still in the queue, no worker is free to run those tasks.")]),

dict(title="Parallel algorithms and a preview of std::execution", std="C++20", minutes=10, area="Concurrency: parallel algorithms",
features=[("Execution policies: `seq`, `par`, `par_unseq`, `unseq`", "C++17/20"), ("`std::reduce`, `std::transform_reduce` with policies", "C++17"), ("Requirements: no data races, no locks in `par_unseq`", "C++17"), ("Implementation notes (TBB for libstdc++)", "—"), ("`std::execution` senders/receivers (preview)", "C++26")],
why="""
Often you don't need threads at all: you need "sort this faster" or "sum this faster". C++17 lets you add a
single argument — an execution policy — to most algorithms and let the library parallelize. It's the
cheapest speedup in the language, when it works.
""",
body="""
## Execution policies

```cpp
std::sort(std::execution::par, v.begin(), v.end());
double total = std::reduce(std::execution::par_unseq, xs.begin(), xs.end(), 0.0);
```

| Policy | Meaning |
|---|---|
| `seq` | sequential |
| `par` | may run on multiple threads |
| `par_unseq` | multiple threads *and* vectorized — no locks or allocation inside your function! |
| `unseq` (C++20) | vectorized on one thread |

Your element functions must not race. `std::reduce` (unlike `accumulate`) may reorder operations, so the
operation must be associative and commutative — floating-point sums may differ slightly between runs.

{{ex}}

!!! note "Library support"
    GCC's libstdc++ implements the parallel policies on top of Intel TBB (link `-ltbb`; without TBB they may
    run sequentially). MSVC supports them natively. libc++'s support is still experimental, which is why this
    example is marked "may be unsupported" locally.

## Preview: `std::execution` (C++26)

C++26 adds **senders/receivers** (P2300): a composable model for async work — `schedule(sched) |
then(f) | let_value(g)`, `when_all`, structured cancellation. It fixes `std::future`'s lack of
composition. Compilers are only starting to ship it (NVIDIA's `stdexec` is the reference implementation),
so we don't compile it here; see the C++26 preview lesson in Week 16.
""",
files={"": r'''
#include <algorithm>
#include <execution>
#include <iostream>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> v(1'000'000);
    std::iota(v.begin(), v.end(), 0);
    std::reverse(v.begin(), v.end());

    std::sort(std::execution::par, v.begin(), v.end());
    std::cout << "sorted: " << std::boolalpha << std::is_sorted(v.begin(), v.end()) << '\n';

    long long total = std::reduce(std::execution::par, v.begin(), v.end(), 0LL);
    std::cout << "reduce: " << total << '\n';

    long long sq = std::transform_reduce(std::execution::par_unseq, v.begin(), v.begin() + 1000, 0LL,
                                         std::plus<>{}, [](int x) { return static_cast<long long>(x) * x; });
    std::cout << "sum of squares 0..999: " << sq << '\n';

    std::vector<double> out(v.size());
    std::transform(std::execution::par_unseq, v.begin(), v.end(), out.begin(), [](int x) { return x * 0.5; });
    std::cout << "out[10] = " << out[10] << '\n';
}
''', "maybe_unsupported": True},
takeaways=["Adding an execution policy is the cheapest way to parallelize standard algorithms.",
"Element functions must be race-free; `par_unseq` forbids locks and allocation.",
"`std::reduce` may reorder operations — use associative, commutative ops.",
"`std::execution` (C++26) brings composable senders/receivers."],
quiz=[("Why might `std::reduce` give a slightly different floating-point sum than `std::accumulate`?", "It may group and reorder additions, and FP addition isn't associative."),
("Can you lock a mutex inside a `par_unseq` lambda?", "No — vectorized execution may interleave iterations on one thread, so locking can deadlock; it's disallowed."),
("What does libstdc++ need for real parallel execution?", "Intel TBB (link with `-ltbb`).")]),

dict(title="Coroutines I: the machinery, and writing a generator", std="C++20", minutes=15, area="Coroutines",
features=[("`co_yield`, `co_return`, `co_await`", "C++20"), ("Coroutine frame, `promise_type`", "C++20"), ("`std::coroutine_handle`", "C++20"), ("`initial_suspend` / `final_suspend`", "C++20"), ("`std::suspend_always` / `suspend_never`", "C++20"), ("Writing a generator by hand", "C++20"), ("`std::generator` (recap)", "C++23")],
why="""
A coroutine is a function that can **pause** in the middle and **resume** later, keeping its local variables.
That lets you write a lazy sequence ("yield the next sample") or an async operation ("wait for the network,
then continue") as straight-line code instead of callbacks and state machines. C++20 gives you the raw
machinery; libraries (and C++23's `std::generator`) give you friendly types. Let's see the machinery once.
""",
body="""
## What makes a function a coroutine

Any function whose body uses `co_yield`, `co_await` or `co_return`. The compiler then:

1. allocates a **coroutine frame** (locals + state), usually on the heap;
2. creates a **promise object** of type `ReturnType::promise_type`;
3. calls `promise.get_return_object()` to make the value returned to the caller;
4. inserts suspension points at `initial_suspend`, each `co_yield`/`co_await`, and `final_suspend`.

```mermaid
sequenceDiagram
    participant Caller
    participant Coro as Coroutine
    Caller->>Coro: call fib()
    Coro-->>Caller: returns Generator (suspended at initial_suspend)
    Caller->>Coro: handle.resume()
    Coro-->>Caller: co_yield 0 (suspends)
    Caller->>Coro: handle.resume()
    Coro-->>Caller: co_yield 1 (suspends)
```

## A minimal generator

{{ex}}

The caller owns the `coroutine_handle` and must `destroy()` it — our `Generator` does that in its
destructor (RAII again). Lifetime is the main trap: a coroutine that takes a reference parameter and
outlives the referent dangles. Prefer taking parameters **by value** in coroutines.

## In practice

Use `std::generator` (C++23, Week 11) when available; write your own types only when you need special
behaviour. The point of this lesson is that you can now *read* coroutine library code.
""",
files={"": r'''
#include <coroutine>
#include <exception>
#include <iostream>
#include <string>
#include <utility>

template <typename T>
class Generator {
public:
    struct promise_type {
        T current{};
        Generator get_return_object() { return Generator{std::coroutine_handle<promise_type>::from_promise(*this)}; }
        std::suspend_always initial_suspend() noexcept { return {}; }   // lazy: don't run until asked
        std::suspend_always final_suspend() noexcept { return {}; }     // keep frame so we can see "done"
        std::suspend_always yield_value(T v) { current = std::move(v); return {}; }
        void return_void() {}
        void unhandled_exception() { throw; }
    };
    explicit Generator(std::coroutine_handle<promise_type> h) : h_{h} {}
    Generator(Generator&& o) noexcept : h_{std::exchange(o.h_, {})} {}
    Generator(const Generator&) = delete;
    ~Generator() { if (h_) h_.destroy(); }                              // RAII over the coroutine frame

    bool next() { h_.resume(); return !h_.done(); }
    const T& value() const { return h_.promise().current; }
private:
    std::coroutine_handle<promise_type> h_;
};

Generator<long long> fibonacci(int count) {
    long long a = 0, b = 1;
    for (int i = 0; i < count; ++i) {
        co_yield a;                                   // suspend, handing `a` to the caller
        a = std::exchange(b, a + b);
    }
}

Generator<std::string> tokens(std::string text) {     // by value: the frame owns its copy
    std::string word;
    for (char c : text) {
        if (c == ' ') { if (!word.empty()) co_yield std::exchange(word, {}); }
        else word += c;
    }
    if (!word.empty()) co_yield word;
}

int main() {
    auto fib = fibonacci(10);
    while (fib.next()) std::cout << fib.value() << ' ';
    std::cout << '\n';
    auto t = tokens("gain 0.5  pan -0.2");
    while (t.next()) std::cout << '[' << t.value() << ']';
    std::cout << '\n';
}
'''},
takeaways=["A coroutine is a function that can suspend and resume, keeping its state in a coroutine frame.",
"The return type's `promise_type` controls behaviour; `coroutine_handle` resumes and destroys it.",
"Wrap the handle in an RAII type that calls `destroy()`.",
"Take coroutine parameters by value to avoid dangling references."],
quiz=[("What makes a function a coroutine?", "Using `co_await`, `co_yield` or `co_return` in its body."),
("Why does our generator use `suspend_always` for `initial_suspend`?", "So the body doesn't run until the caller asks for the first value (lazy)."),
("Why is `Generator<std::string> tokens(const std::string& s)` risky?", "The coroutine may run after the caller's argument (e.g. a temporary) is destroyed, leaving a dangling reference.")]),

dict(title="Coroutines II: awaitables and async tasks", std="C++20", minutes=14, area="Coroutines",
features=[("Awaitable protocol: `await_ready`, `await_suspend`, `await_resume`", "C++20"), ("A lazy `Task<T>` type with continuations", "C++20"), ("Symmetric transfer (returning a handle from `await_suspend`)", "C++20"), ("Scheduling coroutines on an event loop", "C++20"), ("Coroutine libraries (cppcoro, libunifex, Asio, stdexec)", "—")],
why="""
Generators produce values. The bigger win of coroutines is **async I/O**: "read from the socket, then parse,
then write" without callback pyramids. The key is `co_await`, which suspends the coroutine until some
operation finishes and then resumes it with the result. Let's build a tiny single-threaded event loop and a
`Task` type to see how async frameworks work under the hood.
""",
body="""
## The awaitable protocol

`co_await x` calls three functions on the awaiter:

| Function | Question it answers |
|---|---|
| `await_ready()` | Is the result already available? If true, don't suspend. |
| `await_suspend(handle)` | We're suspending — who will resume us? (store the handle somewhere) |
| `await_resume()` | Resumed — what's the value of the `co_await` expression? |

## A lazy `Task` and an event loop

In the example, `sleep_ticks(n)` is an awaitable that schedules the current coroutine on a simple event loop
`n` ticks later. `Task<T>` is lazy: it starts when awaited, and when it finishes, its `final_suspend` resumes
the awaiting coroutine via **symmetric transfer** (returning the continuation's handle), which avoids stack
growth in long chains.

{{ex}}

Notice the output: two "requests" interleave on a single thread — that's concurrency without threads.

## Use a library

Production code should use a proven library (Asio's coroutines, Folly, cppcoro-style libraries, or
`std::execution` in C++26). Writing your own task type is educational but has many subtle lifetime corners.
""",
files={"": r'''
#include <coroutine>
#include <exception>
#include <iostream>
#include <map>
#include <string>
#include <utility>
#include <vector>

struct EventLoop {
    std::multimap<int, std::coroutine_handle<>> timers;   // tick -> who to resume
    int now = 0;
    void run() {
        while (!timers.empty()) {
            auto it = timers.begin();
            now = it->first;
            auto h = it->second;
            timers.erase(it);
            h.resume();
        }
    }
};
EventLoop loop;

struct SleepTicks {
    int ticks;
    bool await_ready() const noexcept { return ticks <= 0; }
    void await_suspend(std::coroutine_handle<> h) const { loop.timers.emplace(loop.now + ticks, h); }
    void await_resume() const noexcept {}
};
SleepTicks sleep_ticks(int n) { return {n}; }

template <typename T>
class Task {
public:
    struct promise_type {
        T value{};
        std::coroutine_handle<> continuation = std::noop_coroutine();
        Task get_return_object() { return Task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
        std::suspend_always initial_suspend() noexcept { return {}; }            // lazy
        struct Final {
            bool await_ready() noexcept { return false; }
            std::coroutine_handle<> await_suspend(std::coroutine_handle<promise_type> h) noexcept {
                return h.promise().continuation;                                  // symmetric transfer
            }
            void await_resume() noexcept {}
        };
        Final final_suspend() noexcept { return {}; }
        void return_value(T v) { value = std::move(v); }
        void unhandled_exception() { std::terminate(); }
    };
    explicit Task(std::coroutine_handle<promise_type> h) : h_{h} {}
    Task(Task&& o) noexcept : h_{std::exchange(o.h_, {})} {}
    ~Task() { if (h_) h_.destroy(); }

    bool await_ready() const noexcept { return false; }
    std::coroutine_handle<> await_suspend(std::coroutine_handle<> awaiting) {
        h_.promise().continuation = awaiting;
        return h_;                                                               // start the child
    }
    T await_resume() { return std::move(h_.promise().value); }
    void start() { h_.resume(); }                                                // for top-level tasks
    bool done() const { return h_.done(); }
private:
    std::coroutine_handle<promise_type> h_;
};

Task<std::string> fetch(std::string name, int latency) {
    std::cout << "[t=" << loop.now << "] fetch " << name << " started\n";
    co_await sleep_ticks(latency);
    std::cout << "[t=" << loop.now << "] fetch " << name << " done\n";
    co_return name + "-data";
}

Task<int> handle_request(std::string id, int latency) {
    std::string a = co_await fetch(id + "/meta", latency);
    std::string b = co_await fetch(id + "/body", latency);
    std::cout << "[t=" << loop.now << "] request " << id << " got " << a << " + " << b << '\n';
    co_return static_cast<int>(a.size() + b.size());
}

int main() {
    auto r1 = handle_request("A", 3);
    auto r2 = handle_request("B", 2);
    r1.start();
    r2.start();
    loop.run();                                   // single thread, interleaved requests
    std::cout << "both done: " << std::boolalpha << (r1.done() && r2.done()) << '\n';
}
'''},
takeaways=["`co_await` uses `await_ready` / `await_suspend` / `await_resume`.",
"A lazy `Task` starts when awaited and resumes its awaiter at `final_suspend`.",
"Symmetric transfer (returning a handle) avoids stack growth in chains of coroutines.",
"Coroutines give concurrency without threads; use a proven library in production."],
quiz=[("What does `await_suspend` typically do?", "Arranges for the suspended coroutine's handle to be resumed later (e.g. registers it with an event loop or I/O completion)."),
("Why is the `Task` lazy (suspend at start)?", "So the awaiting coroutine can register itself as the continuation before the child runs, avoiding races and wasted work."),
("In the example, why do requests A and B interleave on one thread?", "Each suspends at `co_await sleep_ticks`, returning control to the event loop, which resumes whichever timer is due next.")]),
],
assignment=dict(title="Parallel pipeline with a pool and an SPSC ring", task="""
Combine this week's pieces: a producer thread generates 10,000 "audio blocks" (integers) into an
`SpscRing`; a dispatcher thread pops them and submits a processing job (e.g. square modulo 1000) for each to a
`ThreadPool`; gather futures and print the count and checksum, verifying against a sequential computation.
Must be ThreadSanitizer-clean.
""", san=["thread"], solution=r'''
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
              if (q_.empty()) { return; }
              j = std::move(q_.front()); q_.pop_front(); }
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
'''))
