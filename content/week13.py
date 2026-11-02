T = {"san": ["thread"]}
WEEK = dict(num=13, title="Concurrency I: threads, locks, and synchronization", intro="""
Your phone has 8 cores; a single-threaded program uses one. This week we learn to use the rest *safely*:
starting threads, protecting shared data, waiting for events, and getting results back. Honest warning:
concurrency bugs are the hardest bugs in software — they hide in testing and appear in production. Every
example here runs under ThreadSanitizer in CI, and you should run yours under it too.
""", lessons=[
dict(title="Threads, jthread, and cooperative cancellation", std="C++20", minutes=12, area="Concurrency",
features=[("`std::thread`, `join`, `detach`", "C++11"), ("`std::jthread` (auto-joining)", "C++20"), ("`std::stop_token`, `std::stop_source`, `std::stop_callback`", "C++20"), ("`std::this_thread::sleep_for`, `yield`, `get_id`", "C++11"), ("`std::thread::hardware_concurrency`", "C++11"), ("Passing arguments to threads (copies, `std::ref`)", "C++11")],
why="""
Suppose you're decoding 200 audio files. One at a time takes 40 seconds; spread across 8 cores, about 5. A
thread is an independent flow of execution sharing your process's memory. That sharing is the power — and
the danger. Let's start with the mechanics: starting, joining, and stopping threads cleanly.
""",
body="""
## `std::thread` and its trap

```cpp
std::thread t{work};
// if we forget t.join() and t goes out of scope -> std::terminate()!
```

A joinable `std::thread` destroyed without `join()` or `detach()` calls `std::terminate`. And `detach()`
is almost always wrong: the thread may outlive the data it uses.

## `std::jthread` (C++20): use this by default

`jthread` joins automatically in its destructor, *and* carries a `std::stop_token` so you can ask it to stop.
Cancellation is **cooperative**: the thread checks `stop_requested()` and exits on its own. There's no safe
way to kill a thread from outside.

{{ex}}

## Arguments are copied

`std::thread{f, x}` copies `x` into the thread's storage. To pass a reference use `std::ref(x)` — and make
sure `x` outlives the thread. Passing a pointer or reference to a local that goes out of scope is the
classic dangling bug.

## How many threads?

`std::thread::hardware_concurrency()` hints at the number of hardware threads (may return 0 if unknown).
More threads than cores for CPU-bound work just adds context switches.
""",
files={"": r'''
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
''', **T},
takeaways=["A joinable `std::thread` that's destroyed calls `std::terminate`; prefer `std::jthread`.",
"`jthread` auto-joins and supports cooperative cancellation via `stop_token`.",
"Thread arguments are copied; use `std::ref` deliberately and mind lifetimes.",
"Avoid `detach()`; don't run more CPU-bound threads than cores."],
quiz=[("What happens if a joinable `std::thread` is destroyed?", "`std::terminate()` is called."),
("Can `request_stop()` forcibly stop a thread?", "No — it only sets a flag; the thread must check its `stop_token` and return."),
("Why is `std::thread t{f, std::ref(local)}; t.detach();` dangerous?", "The thread may still use `local` after the enclosing function returns — a dangling reference.")]),

dict(title="Data races, mutexes, and deadlock", std="C++20", minutes=13, area="Concurrency",
features=[("Data races are undefined behaviour", "C++11"), ("`std::mutex`, `std::recursive_mutex`, `std::timed_mutex`", "C++11"), ("`std::lock_guard`, `std::unique_lock`", "C++11"), ("`std::scoped_lock` (deadlock-free multi-lock)", "C++17"), ("`std::shared_mutex`, `std::shared_lock`", "C++14/17"), ("`std::call_once`, `std::once_flag`", "C++11"), ("Thread-safe static local initialization", "C++11")],
why="""
Two threads each add 1 to a counter a million times. Expected: 2,000,000. Actual: maybe 1,213,407 — and
different every run. That's a **data race**: two threads access the same memory, at least one writes, and
nothing orders them. In C++ a data race isn't just a wrong number — it's undefined behaviour.
""",
body="""
## The wrong way

{{ex:_race}}

`++counter` is read-modify-write; two threads interleave and lose updates. ThreadSanitizer flags this
immediately (CI runs this example under TSan and checks it's reported).

## Mutexes and RAII locks

```cpp
std::mutex m;
{ std::lock_guard lock{m}; ++counter; }   // unlocked automatically, even on exceptions
```

Never call `m.lock()`/`m.unlock()` by hand. Use `lock_guard` (simple), `unique_lock` (movable, can unlock
early, needed for condition variables), `scoped_lock` (locks several mutexes at once without deadlock).

{{ex}}

## Deadlock

Thread A locks `m1` then waits for `m2`; thread B locks `m2` then waits for `m1`. Forever. Fixes: always
lock in a consistent global order, or lock both at once with `std::scoped_lock{m1, m2}`, and never call
unknown code (callbacks) while holding a lock.

## Readers–writer locks and one-time init

`std::shared_mutex` lets many readers hold `shared_lock` at once while writers take `unique_lock`. Useful
for read-mostly data (but measure — it's heavier than a plain mutex). `std::call_once` and function-local
`static` variables give thread-safe lazy initialization.

!!! warning "Pitfall"
    Keep critical sections short. Holding a lock while doing I/O or calling a callback serializes your
    program and invites deadlock.
""",
files={"": r'''
#include <iostream>
#include <map>
#include <mutex>
#include <shared_mutex>
#include <string>
#include <thread>
#include <vector>

struct Account { std::mutex m; int balance; };

void transfer(Account& from, Account& to, int amount) {
    std::scoped_lock lock{from.m, to.m};       // locks both, deadlock-free regardless of order
    from.balance -= amount;
    to.balance += amount;
}

class Settings {
public:
    std::string get(const std::string& k) const {
        std::shared_lock lock{m_};             // many readers at once
        auto it = values_.find(k);
        return it == values_.end() ? "" : it->second;
    }
    void set(const std::string& k, std::string v) {
        std::unique_lock lock{m_};             // exclusive writer
        values_[k] = std::move(v);
    }
private:
    mutable std::shared_mutex m_;
    std::map<std::string, std::string> values_;
};

int main() {
    int counter = 0;
    std::mutex m;
    {
        std::vector<std::jthread> ts;
        for (int t = 0; t < 4; ++t)
            ts.emplace_back([&] { for (int i = 0; i < 100000; ++i) { std::lock_guard lock{m}; ++counter; } });
    }
    std::cout << "counter = " << counter << '\n';

    Account a{{}, 1000}, b{{}, 1000};
    {
        std::jthread t1{[&] { for (int i = 0; i < 1000; ++i) transfer(a, b, 1); }};
        std::jthread t2{[&] { for (int i = 0; i < 1000; ++i) transfer(b, a, 1); }};   // opposite order: no deadlock
    }
    std::cout << "balances " << a.balance << ' ' << b.balance << '\n';

    Settings s;
    s.set("rate", "48000");
    {
        std::vector<std::jthread> readers;
        for (int i = 0; i < 3; ++i) readers.emplace_back([&] { for (int j = 0; j < 1000; ++j) (void)s.get("rate"); });
        s.set("bits", "24");
    }
    std::cout << "rate=" << s.get("rate") << " bits=" << s.get("bits") << '\n';

    std::once_flag once;
    int inits = 0;
    {
        std::vector<std::jthread> ts;
        for (int i = 0; i < 4; ++i) ts.emplace_back([&] { std::call_once(once, [&] { ++inits; }); });
    }
    std::cout << "initialized " << inits << " time(s)\n";
}
''', **T, "_race": {"expect": "san-detect", "san": ["thread"], "code": r'''
#include <iostream>
#include <thread>

int main() {
    int counter = 0;                                   // shared, unprotected
    {
        std::jthread a{[&] { for (int i = 0; i < 100000; ++i) ++counter; }};
        std::jthread b{[&] { for (int i = 0; i < 100000; ++i) ++counter; }};
    }
    std::cout << "counter = " << counter << " (expected 200000)\n";   // data race: UB
}
'''}},
takeaways=["A data race (unsynchronized access with at least one write) is undefined behaviour.",
"Protect shared data with a mutex and RAII locks; never lock/unlock by hand.",
"Use `std::scoped_lock` for multiple mutexes, or a consistent lock order, to avoid deadlock.",
"`shared_mutex` for read-mostly data; `call_once`/static locals for one-time init."],
quiz=[("Is `++counter` on a shared `int` from two threads safe?", "No — it's a data race (UB); use a mutex or `std::atomic<int>`."),
("How does `std::scoped_lock{m1, m2}` avoid deadlock?", "It uses a deadlock-avoidance algorithm (like `std::lock`) to acquire both without holding one while blocking forever on the other."),
("Why avoid calling user callbacks while holding a lock?", "The callback might take another lock (deadlock risk) or be slow, serializing other threads.")]),

dict(title="Condition variables and a thread-safe queue", std="C++20", minutes=12, area="Concurrency",
features=[("`std::condition_variable`, `wait` with predicate", "C++11"), ("Spurious wakeups and lost wakeups", "C++11"), ("`std::condition_variable_any` with `stop_token`", "C++20"), ("`notify_one` vs `notify_all`", "C++11"), ("Producer–consumer pattern", "—")],
why="""
A decoder thread produces audio blocks; a player thread consumes them. When the queue is empty the player
should *sleep*, not spin burning a core, and wake the moment a block arrives. That's what condition
variables do — and they have two famous traps.
""",
body="""
## The pattern

```cpp
std::unique_lock lock{m};
cv.wait(lock, [&] { return !queue.empty(); });   // ALWAYS wait with a predicate
```

`wait` atomically unlocks the mutex and sleeps; on wake-up it re-locks and re-checks the predicate.

## The two traps

1. **Spurious wakeups**: `wait` may return without a notify. The predicate form loops for you.
2. **Lost wakeups**: if you change the condition *without holding the mutex*, a notify can slip between
   the waiter's check and its sleep. Always modify the shared state under the lock.

{{ex}}

## Shutdown

A blocking queue needs a way to say "no more items". The example uses a `closed` flag; C++20's
`condition_variable_any::wait(lock, stop_token, pred)` also wakes on stop requests.

`notify_one` wakes one waiter (one item added); `notify_all` wakes everyone (state change like shutdown).
""",
files={"": r'''
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
''', **T},
takeaways=["Always `wait` with a predicate — it handles spurious wakeups.",
"Change the shared condition while holding the mutex to avoid lost wakeups.",
"Blocking queues need an explicit close/shutdown path.",
"`condition_variable_any` can wait on a `stop_token` (C++20)."],
quiz=[("Why must `wait` take a `unique_lock` and not a `lock_guard`?", "`wait` needs to unlock and re-lock the mutex, which `lock_guard` can't do."),
("What's a lost wakeup?", "A notify that happens after the waiter checked the condition but before it went to sleep, so it sleeps forever; prevented by changing state under the mutex."),
("When is `notify_all` the right choice?", "When a change matters to all waiters, e.g. shutdown/close.")]),

dict(title="Futures, promises, async, and packaged_task", std="C++20", minutes=10, area="Concurrency",
features=[("`std::async` and launch policies", "C++11"), ("`std::future`, `std::shared_future`", "C++11"), ("`std::promise`", "C++11"), ("`std::packaged_task`", "C++11"), ("Exception propagation through futures", "C++11"), ("`wait_for` and `future_status`", "C++11")],
why="""
Threads and mutexes are low-level. Often you just want "compute this in the background and give me the
answer later". A `std::future` is a one-shot channel for a result — or an exception — from another thread.
""",
body="""
## `std::async`

```cpp
auto f = std::async(std::launch::async, analyze, file);   // runs on another thread
Report r = f.get();                                        // waits; rethrows if analyze threw
```

Always pass `std::launch::async`: the default policy may run the task lazily on `get()` in the *calling*
thread. And beware: the destructor of a future returned by `std::async` **blocks** until the task finishes —
`std::async(...)` whose result you ignore runs synchronously.

## `promise` and `packaged_task`

A `promise` is the writing end of a future: someone calls `set_value` or `set_exception`. A
`packaged_task` wraps a callable so that calling it fulfils a future — the building block of thread pools
(Week 14).

{{ex}}

## Limits

`std::future` has no continuations (`.then`), no composition (`when_all`), and `get()` can only be called
once (use `shared_future` for many readers). For larger async systems look at `std::execution` (C++26,
Week 14) or libraries.
""",
files={"": r'''
#include <chrono>
#include <future>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <thread>
#include <vector>

double analyze(const std::vector<double>& samples) {
    if (samples.empty()) throw std::invalid_argument{"no samples"};
    return std::accumulate(samples.begin(), samples.end(), 0.0) / static_cast<double>(samples.size());
}

int main() {
    std::vector<double> a{1, 2, 3, 4}, b{10, 20};
    auto fa = std::async(std::launch::async, analyze, std::cref(a));
    auto fb = std::async(std::launch::async, analyze, std::cref(b));
    std::cout << "means: " << fa.get() << ' ' << fb.get() << '\n';

    auto bad = std::async(std::launch::async, analyze, std::vector<double>{});
    try { (void)bad.get(); } catch (const std::exception& e) { std::cout << "exception crossed threads: " << e.what() << '\n'; }

    std::promise<int> p;
    std::future<int> f = p.get_future();
    std::jthread producer{[pr = std::move(p)]() mutable {
        std::this_thread::sleep_for(std::chrono::milliseconds{10});
        pr.set_value(42);
    }};
    if (f.wait_for(std::chrono::seconds{0}) == std::future_status::timeout) std::cout << "not ready yet\n";
    std::cout << "promise delivered " << f.get() << '\n';

    std::packaged_task<int(int, int)> task{[](int x, int y) { return x * y; }};
    std::future<int> tf = task.get_future();
    std::jthread runner{std::move(task), 6, 7};
    std::shared_future<int> shared = tf.share();
    std::cout << "packaged_task: " << shared.get() << " (read twice: " << shared.get() << ")\n";
}
''', **T},
takeaways=["A future is a one-shot result channel that also carries exceptions.",
"Use `std::launch::async` explicitly; an ignored `std::async` future blocks in its destructor.",
"`promise` sets a future manually; `packaged_task` ties a callable to a future.",
"`std::future` lacks continuations and composition — bigger systems need more."],
quiz=[("What happens to an exception thrown inside a `std::async` task?", "It's stored in the shared state and rethrown by `get()`."),
("Why might `std::async(f);` (result ignored) not run concurrently?", "The temporary future's destructor blocks until the task finishes, so the statement waits right there."),
("How do several threads read the same result?", "Convert to `std::shared_future` (`share()`); its `get()` can be called multiple times.")]),

dict(title="Latches, barriers, semaphores, and thread_local", std="C++20", minutes=10, area="Concurrency",
features=[("`std::latch`", "C++20"), ("`std::barrier` with completion function", "C++20"), ("`std::counting_semaphore`, `std::binary_semaphore`", "C++20"), ("`thread_local` storage duration", "C++11"), ("Choosing a synchronization primitive", "—")],
why="""
Some coordination patterns are so common C++20 gave them names: "wait until all N workers are ready"
(latch), "everyone finish phase 1 before anyone starts phase 2" (barrier), "at most 3 downloads at once"
(semaphore). Using the named tool is clearer and less bug-prone than building it from a mutex and condition
variable.
""",
body="""
## The tools

| Primitive | Pattern |
|---|---|
| `std::latch` | single-use countdown: workers `count_down()`, someone `wait()`s for zero |
| `std::barrier` | reusable phase sync; optional completion function runs once per phase |
| `std::counting_semaphore<N>` | limit concurrent access to N; `acquire()`/`release()` |
| `std::binary_semaphore` | a lightweight signal between two threads |

{{ex}}

## `thread_local`

A `thread_local` variable has one instance per thread — e.g. a per-thread scratch buffer or random engine,
with no locking. It's constructed on first use in each thread and destroyed when the thread exits.

## Choosing

Start with the highest-level tool that fits: a future for one result, a queue for streams of work, latch/
barrier for phases, a mutex for shared state. Atomics (next week) are the lowest level — reach for them last.
""",
files={"": r'''
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
''', **T},
takeaways=["`latch` = one-shot countdown; `barrier` = reusable phases with a completion step.",
"Semaphores bound concurrency; `binary_semaphore` is a cheap signal.",
"`thread_local` gives each thread its own instance — no locking needed.",
"Prefer the highest-level primitive that fits the pattern."],
quiz=[("Can a `std::latch` be reused after it reaches zero?", "No — it's single-use; use `std::barrier` for repeated phases."),
("What does a barrier's completion function do?", "Runs once per phase, after all threads arrive and before they're released."),
("How many instances of a `thread_local` variable exist with 5 threads?", "One per thread that uses it (up to 5, plus main if it uses it).")]),
],
assignment=dict(title="Parallel file checksum", task="""
Compute a checksum (sum of bytes mod 2^32) of 64 simulated "files" (vectors of bytes generated
deterministically) using a fixed number of worker threads pulling indices from a shared work queue. Use a
`std::latch` to start all workers simultaneously, a mutex-protected result map, and print results in index
order plus the grand total. Must be TSan-clean and give the same output as a sequential computation.
""", solution=r'''
#include <atomic>
#include <cstdint>
#include <iostream>
#include <latch>
#include <map>
#include <mutex>
#include <thread>
#include <vector>

std::vector<std::uint8_t> make_file(int id) {
    std::vector<std::uint8_t> data(1000 + static_cast<std::size_t>(id) * 37);
    for (std::size_t i = 0; i < data.size(); ++i) data[i] = static_cast<std::uint8_t>((i * 31 + static_cast<std::size_t>(id)) & 0xFF);
    return data;
}
std::uint32_t checksum(const std::vector<std::uint8_t>& d) {
    std::uint32_t s = 0;
    for (auto b : d) s += b;
    return s;
}

int main() {
    constexpr int files = 64, workers = 4;
    std::atomic<int> next{0};
    std::latch start{workers + 1};
    std::mutex m;
    std::map<int, std::uint32_t> results;
    {
        std::vector<std::jthread> pool;
        for (int w = 0; w < workers; ++w)
            pool.emplace_back([&] {
                start.arrive_and_wait();
                for (int id; (id = next.fetch_add(1)) < files;) {
                    auto sum = checksum(make_file(id));
                    std::lock_guard lock{m};
                    results[id] = sum;
                }
            });
        start.arrive_and_wait();                      // release everyone at once
    }
    std::uint32_t total = 0, sequential = 0;
    for (auto [id, sum] : results) {
        if (id < 3 || id == files - 1) std::cout << "file " << id << ": " << sum << '\n';
        total += sum;
    }
    for (int id = 0; id < files; ++id) sequential += checksum(make_file(id));
    std::cout << results.size() << " files, total " << total
              << (total == sequential ? " (matches sequential)" : " (MISMATCH)") << '\n';
}
''', san=["thread"]))
