#include <array>
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>

template <std::size_t N>
struct Fixed { std::array<char, N> buf{}; };

template <auto Value>                                  // auto NTTP
constexpr auto twice = Value * 2;

template <std::size_t N>
struct Name {                                          // structural type usable as an NTTP (C++20)
    char chars[N]{};
    constexpr Name(const char (&s)[N]) { for (std::size_t i = 0; i < N; ++i) chars[i] = s[i]; }
};
template <Name N>
void hello() { std::cout << "hello from " << N.chars << '\n'; }

template <typename... Args>
auto sum(const Args&... args) { return (0 + ... + args); }       // binary left fold, safe if empty

template <typename... Args>
void log(const Args&... args) {
    std::cout << '[' << sizeof...(Args) << " args] ";
    ((std::cout << args << ' '), ...);                              // comma fold
    std::cout << '\n';
}

template <typename T, typename... Args>
bool all_equal(const T& first, const Args&... rest) { return ((first == rest) && ...); }

template <template <typename...> class Container>                 // template template parameter
Container<int> make_ints() { return Container<int>{1, 2, 3}; }

int main() {
    std::cout << sizeof(Fixed<16>) << ' ' << twice<21> << '\n';
    hello<"nttp">();
    std::cout << sum() << ' ' << sum(1, 2, 3) << ' ' << sum(0.5, 1, 2u) << '\n';
    log("rate", 48000, 'k', 1.5);
    std::cout << std::boolalpha << all_equal(3, 3, 3) << ' ' << all_equal(3, 3, 4) << '\n';
    auto v = make_ints<std::vector>();
    std::cout << v.size() << '\n';
}
