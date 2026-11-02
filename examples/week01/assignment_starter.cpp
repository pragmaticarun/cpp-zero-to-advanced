#include <array>
#include <cstdint>
#include <iostream>

void put_u32(std::array<std::uint8_t, 44>& h, int pos, std::uint32_t v) {
    // TODO: write 4 bytes, least significant first
}

int main() {
    std::array<std::uint8_t, 44> header{};
    put_u32(header, 24, 48000);  // sample rate lives at offset 24
    std::cout << "TODO\n";
}
