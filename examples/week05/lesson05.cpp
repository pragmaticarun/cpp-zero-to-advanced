#include <chrono>
#include <cstdint>
#include <iostream>
#include <map>
#include <string>
#include <tuple>

struct EncoderConfig {
    std::string codec = "aac";
    int bitrate = 96'000;
    int channels = 2;
    bool vbr = false;
};

struct Hertz { unsigned long long value; };
constexpr Hertz operator""_kHz(unsigned long long v) { return Hertz{v * 1000}; }

class Span2 {                               // a non-aggregate that supports structured bindings
public:
    Span2(int b, int e) : b_{b}, e_{e} {}
    template <std::size_t I> int get() const { if constexpr (I == 0) return b_; else return e_; }
private:
    int b_, e_;
};
template <> struct std::tuple_size<Span2> : std::integral_constant<std::size_t, 2> {};
template <std::size_t I> struct std::tuple_element<I, Span2> { using type = int; };

int main() {
    EncoderConfig cfg{.bitrate = 128'000, .vbr = true};
    std::cout << cfg.codec << ' ' << cfg.bitrate << ' ' << cfg.channels << ' ' << cfg.vbr << '\n';

    struct Rgb { std::uint8_t r, g, b; };
    Rgb teal(0, 128, 128);                   // C++20 parenthesized aggregate init
    auto [r, g, b] = teal;
    std::cout << int{r} << ',' << int{g} << ',' << int{b} << '\n';

    std::map<std::string, int> rates{{"cd", 44'100}, {"dvd", 48'000}};
    for (const auto& [name, rate] : rates) std::cout << name << '=' << rate << ' ';
    std::cout << '\n';

    if (auto [it, inserted] = rates.insert({"cd", 1}); !inserted)
        std::cout << "already had " << it->first << '\n';

    auto [begin, end] = Span2{3, 9};
    std::cout << "span " << begin << ".." << end << '\n';

    using namespace std::chrono_literals;
    auto rate = 48_kHz;
    auto frame = 20ms;
    std::cout << rate.value << " Hz, " << frame.count() << " ms, samples/frame = "
              << rate.value * static_cast<unsigned long long>(frame.count()) / 1000 << '\n';
}
