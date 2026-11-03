#include "ring_buffer.hpp"

#include <iostream>
#include <string>

using embedded::RingBuffer;

// ---- compile-time tests: run by the compiler itself ----
constexpr bool fifo_order() {
    RingBuffer<int, 3> rb;
    (void)rb.push(1); (void)rb.push(2); (void)rb.push(3);
    return !rb.push(4) && rb.pop() == 1 && rb.pop() == 2 && rb.pop() == 3 && !rb.pop();
}
static_assert(fifo_order());

constexpr bool overwrite_policy() {
    RingBuffer<int, 3> rb{RingBuffer<int, 3>::Overflow::overwrite_oldest};
    for (int i = 1; i <= 5; ++i) (void)rb.push(i);
    return rb.size() == 3 && rb[0] == 3 && rb[2] == 5 && rb.overwritten() == 2;
}
static_assert(overwrite_policy());

constexpr int sum_by_iteration() {
    RingBuffer<int, 4> rb;
    for (int i = 1; i <= 4; ++i) (void)rb.push(i);
    (void)rb.pop(); (void)rb.push(10);                    // wrapped
    int s = 0; for (int v : rb) s += v;
    return s;
}
static_assert(sum_by_iteration() == 2 + 3 + 4 + 10);
static_assert(sizeof(RingBuffer<std::uint8_t, 16>) < 64, "no hidden heap pointers or bloat");

int failures = 0;
#define CHECK(c) do { if (!(c)) { ++failures; std::cout << "  FAILED line " << __LINE__ << ": " #c "\n"; } } while (0)

int main() {
    std::cout << "[ RUN ] run-time wrap-around stress\n";
    RingBuffer<int, 7> rb;
    int next_in = 0, next_out = 0;
    for (int round = 0; round < 1000; ++round) {
        for (int k = 0; k < round % 5; ++k) if (rb.push(next_in)) ++next_in;
        for (int k = 0; k < round % 3; ++k) if (auto v = rb.pop()) { CHECK(*v == next_out); ++next_out; }
        CHECK(rb.size() == static_cast<std::size_t>(next_in - next_out));
    }

    std::cout << "[ RUN ] peek / clear\n";
    RingBuffer<int, 2> small;
    CHECK(small.peek() == nullptr);
    (void)small.push(42);
    CHECK(small.peek() && *small.peek() == 42);
    small.clear();
    CHECK(small.empty());

    std::cout << "[ RUN ] non-trivial element type\n";
    RingBuffer<std::string, 2> names;
    CHECK(names.push("kick"));
    CHECK(names.push("snare"));
    CHECK(!names.push("hat"));
    CHECK(names.pop() == std::string{"kick"});

    std::cout << "[ RUN ] SPSC single-threaded semantics\n";
    embedded::SpscRing<int, 4> spsc;
    CHECK(spsc.push(1) && spsc.push(2) && spsc.push(3));
    CHECK(!spsc.push(4));                                // capacity N-1 = 3
    CHECK(spsc.dropped() == 1);
    CHECK(spsc.pop() == 1);

    std::cout << "compile-time tests: 4 passed (static_assert)\n";
    std::cout << (failures == 0 ? "ALL TESTS PASSED\n" : "SOME TESTS FAILED\n");
    return failures == 0 ? 0 : 1;
}
