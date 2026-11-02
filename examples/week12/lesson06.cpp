#include <chrono>
#include <format>
#include <iostream>
#include <thread>

int main() {
    using namespace std::chrono;
    using namespace std::chrono_literals;

    auto timeout = 250ms;
    seconds s = 3min;                                       // lossless: implicit
    auto t = duration_cast<seconds>(1500ms);                 // lossy: explicit (truncates)
    std::cout << timeout.count() << "ms, " << s.count() << "s, " << t.count() << "s, round="
              << round<seconds>(1500ms).count() << "s\n";
    std::cout << std::format("{} + {} = {}\n", 1h, 30min, 1h + 30min);

    auto start = steady_clock::now();
    std::this_thread::sleep_for(20ms);
    auto elapsed = duration_cast<milliseconds>(steady_clock::now() - start);
    std::cout << "slept at least 20ms? " << std::boolalpha << (elapsed >= 20ms) << '\n';

    year_month_day release = 2026y / January / 31;
    auto next_month = release + months{1};                   // 2026-02-31: not a valid date
    std::cout << "valid? " << next_month.ok() << '\n';
    auto clamped = next_month.year() / next_month.month() / last;
    std::cout << "clamped to " << year_month_day{clamped} << '\n';
    auto overflowed = year_month_day{sys_days{next_month}};  // normalizes into March
    std::cout << "overflowed to " << overflowed << '\n';
    std::cout << "weekday of 2026-11-03: " << weekday{sys_days{2026y / November / 3}} << '\n';
    auto days_left = sys_days{2026y / December / 25} - sys_days{2026y / November / 3};
    std::cout << "days until 2026-12-25: " << days_left.count() << '\n';

    sys_seconds stamp = sys_days{2026y / November / 3} + 9h + 30min;
    std::cout << std::format("UTC stamp: {:%Y-%m-%d %H:%M}\n", stamp);
}
