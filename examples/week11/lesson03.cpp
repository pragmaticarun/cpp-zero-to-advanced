#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

struct Take { std::string name; int seconds; bool clipped; };

int main() {
    std::vector<Take> takes{{"intro", 30, false}, {"verse", 62, true}, {"chorus", 45, true},
                            {"bridge", 20, false}, {"outro", 75, true}, {"coda", 15, true}};

    auto upper = [](std::string s) { for (auto& c : s) c = static_cast<char>(std::toupper(static_cast<unsigned char>(c))); return s; };
    auto names = takes | std::views::filter(&Take::clipped)
                       | std::views::transform(&Take::name)
                       | std::views::transform(upper)
                       | std::views::take(3);
    for (const auto& n : names) std::cout << n << ' ';
    std::cout << '\n';

    auto squares = std::views::iota(1) | std::views::transform([](int i) { return i * i; })
                                       | std::views::take_while([](int x) { return x < 50; });
    auto v = squares | std::ranges::to<std::vector>();                  // C++23
    std::cout << "squares < 50: " << v.size() << " values, last " << v.back() << '\n';

    for (auto [i, t] : std::views::enumerate(takes) | std::views::take(2))   // C++23
        std::cout << i << ':' << t.name << ' ';
    std::cout << '\n';

    std::vector<int> left{1, 2, 3}, right{10, 20, 30};
    for (auto [l, r] : std::views::zip(left, right)) std::cout << l + r << ' ';
    std::cout << '\n';

    std::vector<int> samples{1, 2, 3, 4, 5, 6, 7};
    for (auto chunk : samples | std::views::chunk(3)) std::cout << '[' << std::ranges::fold_left(chunk, 0, std::plus<>{}) << ']';
    std::cout << " <- sums of chunks of 3\n";
    for (auto w : samples | std::views::slide(3)) std::cout << w[1] << ' ';
    std::cout << "<- centers of sliding windows\n";

    std::string_view csv = "kick,snare,hat";
    for (auto part : csv | std::views::split(',')) std::cout << std::string_view{part} << '|';
    std::cout << '\n';

    std::map<std::string, int> bpm{{"house", 124}, {"techno", 130}};
    for (const auto& k : bpm | std::views::keys) std::cout << k << ' ';
    for (int b : bpm | std::views::values | std::views::reverse) std::cout << b << ' ';
    std::cout << '\n';

    auto r = std::ranges::find(std::vector<int>{1, 2, 3}, 2);           // temporary: returns `dangling`
    static_assert(std::is_same_v<decltype(r), std::ranges::dangling>);
}
