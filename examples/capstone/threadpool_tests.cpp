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
