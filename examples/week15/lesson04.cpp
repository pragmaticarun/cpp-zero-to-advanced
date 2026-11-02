#include <chrono>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>

template <typename F>
double time_ms(F&& f, int reps) {
    auto best = std::chrono::duration<double, std::milli>::max();
    for (int r = 0; r < reps; ++r) {                    // take the best of several runs
        auto t0 = std::chrono::steady_clock::now();
        f();
        auto dt = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0);
        if (dt < best) best = dt;
    }
    return best.count();
}

int classify(int x) {
    if (x < 0) [[unlikely]] return -1;
    return x % 3;
}

int main() {
    std::vector<std::int32_t> data(2'000'000);
    std::iota(data.begin(), data.end(), 0);
    volatile std::int64_t sink = 0;                     // keep results observable so work isn't deleted

    double loop_ms = time_ms([&] {
        std::int64_t s = 0;
        for (std::size_t i = 0; i < data.size(); ++i) s += data[i];
        sink = s;
    }, 5);
    double accum_ms = time_ms([&] { sink = std::accumulate(data.begin(), data.end(), std::int64_t{0}); }, 5);

    std::cout << "checksum " << sink << '\n';
    std::cout << "classify(-5)=" << classify(-5) << " classify(7)=" << classify(7) << '\n';
    std::cerr << "loop " << loop_ms << " ms, accumulate " << accum_ms << " ms (machine-dependent)\n";
}
