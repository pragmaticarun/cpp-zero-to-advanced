// A readable error: "constraints not satisfied ... std::integral<double>"
#include <concepts>
template <std::integral T> T gcd(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }
int main() { return static_cast<int>(gcd(4.0, 2.0)); }
