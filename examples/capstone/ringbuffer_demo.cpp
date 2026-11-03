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
