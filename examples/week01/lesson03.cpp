#include <cstdint>
#include <iostream>
#include <limits>

int main() {
    std::cout << "sizeof(int)=" << sizeof(int)
              << " sizeof(long long)=" << sizeof(long long)
              << " sizeof(double)=" << sizeof(double) << '\n';

    std::cout << "int range: " << std::numeric_limits<int>::min() << " .. "
              << std::numeric_limits<int>::max() << '\n';
    std::cout << "uint16_t max: " << std::numeric_limits<std::uint16_t>::max() << '\n';

    int bin = 0b1111'1111;  // binary literal with digit separator
    std::cout << "0b1111'1111 = " << bin << ", 0xFF = " << 0xFF << '\n';

    double x = 0.1 + 0.2;
    std::cout << std::boolalpha << "0.1 + 0.2 == 0.3 ? " << (x == 0.3) << '\n';
    std::cout.precision(17);
    std::cout << "0.1 + 0.2 = " << x << '\n';

    std::uint8_t channels = 65;
    std::cout << "uint8_t printed directly: " << channels
              << ", as int: " << static_cast<int>(channels) << '\n';
}
