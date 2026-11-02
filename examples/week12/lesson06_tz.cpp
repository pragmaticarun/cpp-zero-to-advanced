#include <chrono>
#include <format>
#include <iostream>

int main() {
    using namespace std::chrono;
    sys_seconds stamp = sys_days{2026y / November / 3} + 9h + 30min;   // 09:30 UTC
    zoned_time india{"Asia/Kolkata", stamp};
    zoned_time ny{"America/New_York", stamp};
    std::cout << std::format("India:    {:%Y-%m-%d %H:%M %Z}\n", india);
    std::cout << std::format("New York: {:%Y-%m-%d %H:%M %Z}\n", ny);
}
