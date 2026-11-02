#include <cstdint>
#include <iostream>
#include <utility>
#include <vector>

int main() {
    std::vector<int> v;  // size() == 0, type std::size_t (unsigned)

    // The trap: -1 is converted to a huge unsigned value.
    // (We cast explicitly here so the example compiles warning-free; the implicit
    //  comparison `-1 < v.size()` would trigger -Wsign-compare.)
    std::cout << std::boolalpha;
    std::cout << "-1 < v.size() (as unsigned): " << (static_cast<std::size_t>(-1) < v.size()) << '\n';
    std::cout << "std::cmp_less(-1, v.size()): " << std::cmp_less(-1, v.size()) << '\n';

    std::uint8_t a = 200, b = 100;
    auto c = a + b;  // promoted to int
    std::cout << "200 + 100 with uint8_t operands = " << c << '\n';

    unsigned int u = 0;
    --u;  // well-defined wrap-around
    std::cout << "0u - 1 = " << u << '\n';

    std::cout << "-7 / 2 = " << -7 / 2 << ", -7 % 2 = " << -7 % 2 << '\n';
    double avg = 7.9;
    std::cout << "static_cast<int>(7.9) = " << static_cast<int>(avg) << '\n';
}
