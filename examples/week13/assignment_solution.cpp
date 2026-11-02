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
