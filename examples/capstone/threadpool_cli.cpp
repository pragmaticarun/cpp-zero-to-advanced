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
