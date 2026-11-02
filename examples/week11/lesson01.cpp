#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Take { std::string name; int seconds; double loudness; bool clipped; };

int main() {
    std::vector<Take> takes{{"t1", 45, -14.0, false}, {"t2", 75, -9.5, true}, {"t3", 62, -11.0, false},
                            {"t4", 30, -20.0, false}, {"t5", 90, -8.0, true}, {"t6", 62, -12.5, false}};

    auto first_clip = std::ranges::find_if(takes, &Take::clipped);              // projection as predicate
    std::cout << "first clipped: " << first_clip->name << '\n';
    auto long_ones = std::ranges::count_if(takes, [](int s) { return s > 60; }, &Take::seconds);
    std::cout << "longer than 60s: " << long_ones << '\n';
    std::cout << std::boolalpha << "all under 2 min? "
              << std::ranges::all_of(takes, [](int s) { return s < 120; }, &Take::seconds) << '\n';

    auto by_loud = takes;
    std::ranges::partial_sort(by_loud, by_loud.begin() + 2, std::ranges::greater{}, &Take::loudness);
    std::cout << "top 2 loudest: " << by_loud[0].name << ' ' << by_loud[1].name << '\n';

    std::vector<int> durations;
    for (const auto& t : takes) durations.push_back(t.seconds);
    auto mid = durations.begin() + static_cast<long>(durations.size() / 2);
    std::ranges::nth_element(durations, mid);
    std::cout << "median-ish duration: " << *mid << '\n';

    auto stable = takes;
    std::ranges::stable_sort(stable, {}, &Take::seconds);                    // t3 stays before t6
    for (const auto& t : stable) std::cout << t.name << '(' << t.seconds << ") ";
    std::cout << '\n';

    std::ranges::sort(durations);
    auto [lo, hi] = std::ranges::equal_range(durations, 62);
    std::cout << "takes of exactly 62s: " << (hi - lo) << ", lower_bound(60) -> " << *std::ranges::lower_bound(durations, 60) << '\n';
    auto [mn, mx] = std::ranges::minmax(durations);
    std::cout << "min " << mn << " max " << mx << " clamp(200) " << std::clamp(200, mn, mx) << '\n';
}
