#include <iostream>
#include <limits>

int clamp_add(int a, int b) {
    constexpr int hi = std::numeric_limits<int>::max();
    constexpr int lo = std::numeric_limits<int>::min();
    if (b > 0 && a > hi - b) return hi;   // a + b would exceed hi
    if (b < 0 && a < lo - b) return lo;   // a + b would go below lo
    return a + b;
}

int main() {
    std::cout << clamp_add(2, 3) << ' '
              << clamp_add(std::numeric_limits<int>::max(), 1) << ' '
              << clamp_add(std::numeric_limits<int>::min(), -5) << '\n';
}
