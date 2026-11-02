#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string_view>
#include <tuple>
#include <type_traits>

// (1) Reflection today: list fields by hand (C++26: std::meta::nonstatic_data_members_of)
struct Settings { int rate; int bits; double gain; };
template <typename F> void for_each_field(const Settings& s, F f) { f("rate", s.rate); f("bits", s.bits); f("gain", s.gain); }

// (2) Contracts today: a macro (C++26: pre(...) / post(...) / contract_assert)
#define EXPECTS(cond) ((cond) ? void(0) : throw std::logic_error{"precondition failed: " #cond})
double mean(std::span<const double> xs) {
    EXPECTS(!xs.empty());
    double s = 0; for (double x : xs) s += x;
    return s / static_cast<double>(xs.size());
}

// (3) inplace_vector today: array + size (C++26: std::inplace_vector<T, N>)
template <typename T, std::size_t N>
struct FixedVec {
    std::array<T, N> data{}; std::size_t n = 0;
    bool push_back(const T& v) { if (n == N) return false; data[n++] = v; return true; }
    std::size_t size() const { return n; }
};

// (4) Pack indexing today (C++26: Ts...[0])
template <typename... Ts> using first_t = std::tuple_element_t<0, std::tuple<Ts...>>;
static_assert(std::is_same_v<first_t<int, double>, int>);

// (5) Saturating add today (C++26: std::add_sat)
constexpr std::int16_t add_sat16(std::int16_t a, std::int16_t b) {
    int r = a + b;
    return static_cast<std::int16_t>(r > std::numeric_limits<std::int16_t>::max() ? std::numeric_limits<std::int16_t>::max()
                                   : r < std::numeric_limits<std::int16_t>::min() ? std::numeric_limits<std::int16_t>::min() : r);
}

int main() {
    for_each_field(Settings{48000, 24, 0.5}, [](std::string_view name, auto v) { std::cout << name << " = " << v << '\n'; });
    double xs[] = {1, 2, 3};
    std::cout << "mean " << mean(xs) << '\n';
    try { (void)mean({}); } catch (const std::logic_error& e) { std::cout << e.what() << '\n'; }
    FixedVec<int, 2> fv;
    std::cout << std::boolalpha << fv.push_back(1) << ' ' << fv.push_back(2) << ' ' << fv.push_back(3) << " size " << fv.size() << '\n';
    std::cout << "add_sat16(30000, 10000) = " << add_sat16(30000, 10000) << '\n';
}
