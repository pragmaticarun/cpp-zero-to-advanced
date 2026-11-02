#include <algorithm>
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Track { std::string title; int seconds; };

class Player {
public:
    auto make_logger() const { return [*this] { std::cout << "player volume " << volume_ << '\n'; }; }  // copy of *this
    int volume_ = 7;
};

int main() {
    std::vector<Track> tracks{{"So What", 562}, {"Blue in Green", 337}, {"All Blues", 693}};

    std::ranges::sort(tracks, [](const Track& a, const Track& b) { return a.seconds < b.seconds; });
    for (const auto& t : tracks) std::cout << t.title << " (" << t.seconds << "s)\n";

    int threshold = 400;
    auto longer = std::ranges::count_if(tracks, [threshold](const Track& t) { return t.seconds > threshold; });
    std::cout << longer << " tracks longer than " << threshold << "s\n";

    auto counter = [n = 0]() mutable { return ++n; };   // init capture + mutable
    auto copy = counter;
    std::cout << counter() << counter() << ' ' << copy() << '\n';

    auto owned = std::make_unique<std::string>("owned buffer");
    auto task = [buf = std::move(owned)] { return buf->size(); };   // move-only capture
    std::cout << "task sees " << task() << " chars\n";

    auto add = [](const auto& a, const auto& b) { return a + b; };   // generic
    std::cout << add(1, 2) << ' ' << add(std::string{"a"}, std::string{"b"}) << '\n';

    auto first_or = []<typename T>(const std::vector<T>& v, T fallback) { return v.empty() ? fallback : v.front(); };
    std::cout << first_or(std::vector<int>{}, -1) << '\n';

    constexpr auto square = [](int x) { return x * x; };
    static_assert(square(5) == 25);

    auto cube = [](int x) static { return x * x * x; };   // C++23: no `this` needed
    std::cout << cube(3) << '\n';

    Player p;
    auto log = p.make_logger();
    p.volume_ = 11;
    log();                                                // still 7: captured a copy

    const std::string mode = [&] { return threshold > 300 ? std::string{"long"} : std::string{"short"}; }();
    std::cout << "mode=" << mode << '\n';
}
