#include <array>
#include <cstdint>
#include <iostream>

using Header = std::array<std::uint8_t, 44>;

void put_u16(Header& h, std::size_t pos, std::uint16_t v) {
    h[pos] = static_cast<std::uint8_t>(v & 0xFF);
    h[pos + 1] = static_cast<std::uint8_t>(v >> 8);
}
void put_u32(Header& h, std::size_t pos, std::uint32_t v) {
    for (std::size_t i = 0; i < 4; ++i) h[pos + i] = static_cast<std::uint8_t>(v >> (8 * i));
}
std::uint16_t get_u16(const Header& h, std::size_t pos) {
    return static_cast<std::uint16_t>(h[pos] | (h[pos + 1] << 8));
}
std::uint32_t get_u32(const Header& h, std::size_t pos) {
    std::uint32_t v = 0;
    for (std::size_t i = 0; i < 4; ++i) v |= std::uint32_t{h[pos + i]} << (8 * i);
    return v;
}

int main() {
    constexpr std::uint32_t sample_rate = 48'000;
    constexpr std::uint16_t channels = 2, bits = 16;
    constexpr std::uint32_t byte_rate = sample_rate * channels * bits / 8;
    constexpr std::uint32_t data_size = byte_rate * 1;  // one second of audio

    Header h{};
    const char* tags[] = {"RIFF", "WAVE", "fmt ", "data"};
    const std::size_t tag_pos[] = {0, 8, 12, 36};
    for (int t = 0; t < 4; ++t)
        for (std::size_t i = 0; i < 4; ++i) h[tag_pos[t] + i] = static_cast<std::uint8_t>(tags[t][i]);
    put_u32(h, 4, 36 + data_size);
    put_u32(h, 16, 16);      // fmt chunk size
    put_u16(h, 20, 1);       // PCM
    put_u16(h, 22, channels);
    put_u32(h, 24, sample_rate);
    put_u32(h, 28, byte_rate);
    put_u16(h, 32, static_cast<std::uint16_t>(channels * bits / 8));  // block align
    put_u16(h, 34, bits);
    put_u32(h, 40, data_size);

    std::cout << "format=" << get_u16(h, 20) << " channels=" << get_u16(h, 22)
              << " rate=" << get_u32(h, 24) << " byte_rate=" << get_u32(h, 28)
              << " bits=" << get_u16(h, 34) << " data=" << get_u32(h, 40) << '\n';
}
