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
