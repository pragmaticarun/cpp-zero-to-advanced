#include <cstdint>
#include <string>
#include <vector>

template <typename... Ts>
std::vector<std::uint8_t> pack(const Ts&... values) {
    std::vector<std::uint8_t> out;
    // TODO: fold over values, encoding each
    return out;
}

int main() { return static_cast<int>(pack(1, 2).size()); }
