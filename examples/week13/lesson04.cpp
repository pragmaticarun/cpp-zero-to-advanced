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
