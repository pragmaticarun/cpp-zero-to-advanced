#include <array>
#include <bit>
#include <cstdint>
#include <iostream>

// ---- simulated memory-mapped peripheral ----
struct GpioRegs {
    volatile std::uint32_t mode;
    volatile std::uint32_t out;
    volatile std::uint32_t in;
};
GpioRegs fake_gpio{};                                    // on hardware: *reinterpret_cast<GpioRegs*>(0x48000000)

constexpr std::uint32_t pin(unsigned n) { return 1u << n; }
void led_on(GpioRegs& g, unsigned n) { g.out = g.out | pin(n); }      // not `|=`: deprecated on volatile
void led_off(GpioRegs& g, unsigned n) { g.out = g.out & ~pin(n); }

// ---- Q15 fixed point ----
using q15 = std::int16_t;
constexpr q15 to_q15(double x) { return static_cast<q15>(x * 32768.0 >= 32767.0 ? 32767 : x * 32768.0); }
constexpr q15 q15_mul(q15 a, q15 b) {
    std::int32_t p = (static_cast<std::int32_t>(a) * b) >> 15;
    return static_cast<q15>(p > 32767 ? 32767 : (p < -32768 ? -32768 : p));
}

// ---- compile-time lookup table (lives in flash on an MCU) ----
constexpr auto make_square_table() {
    std::array<std::uint16_t, 16> t{};
    for (std::size_t i = 0; i < t.size(); ++i) t[i] = static_cast<std::uint16_t>(i * i);
    return t;
}
constexpr auto kSquares = make_square_table();
static_assert(kSquares[15] == 225);

// ---- a static pool: fixed number of objects, no heap ----
template <typename T, std::size_t N>
class StaticPool {
public:
    T* acquire() { for (std::size_t i = 0; i < N; ++i) if (!used_[i]) { used_[i] = true; return &items_[i]; } return nullptr; }
    void release(T* p) { used_[static_cast<std::size_t>(p - items_.data())] = false; }
private:
    std::array<T, N> items_{};
    std::array<bool, N> used_{};
};

int main() {
    led_on(fake_gpio, 5);
    led_on(fake_gpio, 0);
    led_off(fake_gpio, 5);
    std::cout << "GPIO out = 0x" << std::hex << fake_gpio.out << std::dec << '\n';

    q15 half = to_q15(0.5), gain = to_q15(0.25);
    std::cout << "0.5 * 0.25 in Q15 = " << q15_mul(half, gain) << " (" << q15_mul(half, gain) / 32768.0 << ")\n";
    std::cout << "saturating -1 * -1 = " << q15_mul(-32768, -32768) << '\n';

    std::cout << "kSquares[12] = " << kSquares[12] << '\n';
    std::cout << "popcount(0xF0F0) = " << std::popcount(0xF0F0u) << ", bit_width(1000) = " << std::bit_width(1000u)
              << ", float bits = 0x" << std::hex << std::bit_cast<std::uint32_t>(1.0f) << std::dec << '\n';

    StaticPool<int, 2> pool;
    int* a = pool.acquire(); int* b = pool.acquire(); int* c = pool.acquire();
    std::cout << "pool: a " << (a ? "ok" : "null") << ", b " << (b ? "ok" : "null") << ", c " << (c ? "ok" : "null") << '\n';
    pool.release(a);
    std::cout << "after release: " << (pool.acquire() ? "ok" : "null") << '\n';
}
