#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <string_view>
#include <vector>

constexpr double sin_approx(double x) {           // Taylor series: constexpr-friendly
    double term = x, sum = x;
    for (int n = 1; n < 10; ++n) { term *= -x * x / ((2 * n) * (2 * n + 1)); sum += term; }
    return sum;
}

template <std::size_t N>
constexpr std::array<std::int16_t, N> make_sine_table() {
    std::array<std::int16_t, N> t{};
    constexpr double pi = 3.14159265358979323846;
    for (std::size_t i = 0; i < N; ++i) {
        double x = 2 * pi * static_cast<double>(i) / N;
        if (x > pi) x -= 2 * pi;                  // keep the series accurate
        t[i] = static_cast<std::int16_t>(sin_approx(x) * 32767);
    }
    return t;
}
constexpr auto sine = make_sine_table<256>();    // computed by the compiler
static_assert(sine[64] > 32700);                 // a compile-time test

constexpr int sum_squares(int n) {               // C++20: std::vector in constant evaluation
    std::vector<int> v(static_cast<std::size_t>(n));
    std::iota(v.begin(), v.end(), 1);
    int s = 0;
    for (int x : v) s += x * x;
    return s;
}
static_assert(sum_squares(3) == 14);

consteval std::uint32_t fourcc(std::string_view s) {   // must be compile time
    if (s.size() != 4) throw "fourcc needs exactly 4 chars";   // compile error if hit
    return std::uint32_t(s[0]) | std::uint32_t(s[1]) << 8 | std::uint32_t(s[2]) << 16 | std::uint32_t(s[3]) << 24;
}

constexpr double fast_sqrt(double x) {
    if consteval { double r = x; for (int i = 0; i < 30; ++i) r = 0.5 * (r + x / r); return r; }
    else { return std::sqrt(x); }                // run time: use the library
}

constinit int frame_counter = 0;                 // statically initialized; still mutable

int main() {
    std::cout << "sine[0]=" << sine[0] << " sine[64]=" << sine[64] << " sine[192]=" << sine[192] << '\n';
    std::cout << "sum_squares(10)=" << sum_squares(10) << '\n';
    constexpr auto riff = fourcc("RIFF");
    std::cout << std::hex << "RIFF=0x" << riff << std::dec << '\n';
    constexpr double s2 = fast_sqrt(2.0);
    volatile double two = 2.0;
    std::cout << s2 << ' ' << fast_sqrt(two) << '\n';
    ++frame_counter;
    std::cout << "frame_counter=" << frame_counter << '\n';
}
