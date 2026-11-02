#include <algorithm>
#include <functional>
#include <iostream>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

std::tuple<int, std::string, double> parse_line() { return {7, "So What", 562.5}; }

struct Mixer {
    Mixer(int ch, std::string n) : channels{ch}, name{std::move(n)} {}
    int channels; std::string name;
};

enum class Codec : unsigned char { pcm = 1, opus = 2 };

void bump(int& x) { ++x; }

int main() {
    auto [id, title, secs] = parse_line();
    std::cout << id << ' ' << title << ' ' << secs << '\n';

    auto t = parse_line();
    std::cout << std::get<std::string>(t) << " / " << std::get<0>(t) << '\n';
    auto bigger = std::tuple_cat(t, std::make_tuple('x'));
    std::cout << "tuple_cat size: " << std::tuple_size_v<decltype(bigger)> << '\n';

    int a = 0; std::string b;
    std::tie(a, b, std::ignore) = parse_line();
    std::cout << "tie: " << a << ' ' << b << '\n';

    auto args = std::make_tuple(3, 4);
    std::cout << "apply: " << std::apply(std::plus<>{}, args) << '\n';
    auto m = std::make_from_tuple<Mixer>(std::make_tuple(2, std::string{"main"}));
    std::cout << "make_from_tuple: " << m.name << ' ' << m.channels << '\n';

    std::vector<int> v{5, 2, 8, 1};
    std::ranges::sort(v, std::greater<>{});
    auto is_even = [](int x) { return x % 2 == 0; };
    std::cout << "first odd: " << *std::ranges::find_if(v, std::not_fn(is_even)) << '\n';

    int counter = 10;
    int old = std::exchange(counter, 0);
    std::cout << "exchange: old " << old << " new " << counter << '\n';
    std::cout << "to_underlying(opus) = " << static_cast<int>(std::to_underlying(Codec::opus)) << '\n';

    int n = 1;
    auto f = std::bind_front(bump, std::ref(n));   // without std::ref, bump would modify a copy
    f(); f();
    std::cout << "n after ref binding: " << n << '\n';
}
