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
