#include <algorithm>
#include <iostream>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

std::string_view level(std::string_view line) {
    auto s = line.substr(line.find(' ') + 1);
    return s.substr(0, s.find(' '));
}
std::string_view message(std::string_view line) {
    auto s = line.substr(line.find(' ') + 1);
    return s.substr(s.find(' ') + 1);
}

int main() {
    std::vector<std::string_view> log{"12:00:01 INFO start", "12:00:02 WARN disk 91%", "12:00:03 ERROR write failed",
                                      "12:00:04 INFO retry", "12:00:05 ERROR write failed again", "12:00:06 WARN fan",
                                      "12:00:07 ERROR giving up"};
    for (std::string_view lv : {"INFO", "WARN", "ERROR"})
        std::cout << lv << ": " << std::ranges::count_if(log, [lv](auto l) { return level(l) == lv; }) << '\n';

    auto errors = log | std::views::filter([](auto l) { return level(l) == "ERROR"; })
                      | std::views::transform([](auto l) { return std::string{message(l)}; })
                      | std::views::take(2)
                      | std::ranges::to<std::vector>();
    for (const auto& e : errors) std::cout << "error: " << e << '\n';

    std::cout << "WARN on lines:";
    for (auto [i, l] : std::views::enumerate(log))
        if (level(l) == "WARN") std::cout << ' ' << i + 1;
    std::cout << '\n';
}
