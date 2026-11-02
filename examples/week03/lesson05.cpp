#include <bit>
#include <bitset>
#include <cstddef>
#include <cstdint>
#include <iostream>

struct NalHeader { unsigned forbidden, ref_idc, type; };

NalHeader parse(std::uint8_t b) {
    return {static_cast<unsigned>(b >> 7) & 0x1u,
            static_cast<unsigned>(b >> 5) & 0x3u,
            static_cast<unsigned>(b) & 0x1Fu};
}

int main() {
    const std::uint8_t nal = 0x67;   // a typical H.264 SPS header byte
    const auto h = parse(nal);
    std::cout << "bits=" << std::bitset<8>(nal) << " forbidden=" << h.forbidden
              << " ref_idc=" << h.ref_idc << " type=" << h.type << '\n';

    unsigned flags = 0;
    flags |= 1u << 3;        // set bit 3
    flags |= 1u << 0;        // set bit 0
    flags &= ~(1u << 0);     // clear bit 0
    flags ^= 1u << 5;        // toggle bit 5
    std::cout << "flags=" << std::bitset<8>(flags) << " popcount=" << std::popcount(flags) << '\n';

    std::cout << "bit_ceil(600)=" << std::bit_ceil(600u) << " has_single_bit(512)=" << std::has_single_bit(512u)
              << " countr_zero(40)=" << std::countr_zero(40u) << '\n';

    std::cout << std::hex << "bits of 1.0f = 0x" << std::bit_cast<std::uint32_t>(1.0f)
              << " byteswap(0x11223344)=0x" << std::byteswap(0x11223344u) << std::dec << '\n';
    std::cout << "little endian? " << (std::endian::native == std::endian::little) << '\n';

    std::byte b{0b1010'0000};
    b |= std::byte{0x01};
    std::cout << "std::byte as int: " << std::to_integer<int>(b) << '\n';
}
