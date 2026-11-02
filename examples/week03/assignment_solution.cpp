#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <span>

struct Record { double temp_c; unsigned humidity, id, flags; };

constexpr std::uint32_t pack(double temp_c, unsigned humidity, unsigned id, unsigned flags) {
    const auto raw_t = static_cast<std::uint32_t>((temp_c + 40.0) * 10.0 + 0.5) & 0xFFFu;
    return raw_t | (std::uint32_t{humidity & 0xFFu} << 12) | (std::uint32_t{id & 0xFFu} << 20)
           | (std::uint32_t{flags & 0xFu} << 28);
}

Record unpack(std::uint32_t r) {
    return {static_cast<double>(r & 0xFFFu) / 10.0 - 40.0, (r >> 12) & 0xFFu, (r >> 20) & 0xFFu, (r >> 28) & 0xFu};
}

int count_flag0(std::span<const std::uint32_t> recs) {
    int n = 0;
    for (auto r : recs) n += static_cast<int>((r >> 28) & 1u);
    return n;
}

int main() {
    constexpr std::array<std::uint32_t, 3> recs{pack(21.5, 40, 7, 0b0001), pack(-5.0, 85, 8, 0b0010),
                                                pack(36.6, 55, 9, 0b1001)};
    static_assert(pack(0.0, 0, 0, 0) == 400);   // checked at compile time
    for (auto r : recs) {
        const auto x = unpack(r);
        std::cout << "id=" << x.id << " temp=" << x.temp_c << "C hum=" << x.humidity
                  << "% flags=" << x.flags << " (" << std::popcount(x.flags) << " set)\n";
    }
    std::cout << "flag0 set in " << count_flag0(recs) << " records\n";
}
