#include <bit>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>
#include <type_traits>
#include <vector>

template <typename T>
void put(std::vector<std::uint8_t>& out, const T& v) {
    using U = std::remove_cvref_t<T>;
    if constexpr (std::is_same_v<U, bool>) out.push_back(v ? 1 : 0);
    else if constexpr (std::is_integral_v<U>) {
        using UU = std::make_unsigned_t<U>;
        const auto u = static_cast<UU>(v);
        for (int i = sizeof(U) - 1; i >= 0; --i) out.push_back(static_cast<std::uint8_t>(u >> (8 * i)));
    } else if constexpr (std::is_floating_point_v<U>) {
        using Bits = std::conditional_t<sizeof(U) == 4, std::uint32_t, std::uint64_t>;
        put(out, std::bit_cast<Bits>(v));
    } else if constexpr (std::is_same_v<U, std::string>) {
        put(out, static_cast<std::uint16_t>(v.size()));
        out.insert(out.end(), v.begin(), v.end());
    } else {
        static_assert(sizeof(U) == 0, "pack: unsupported type");
    }
}

template <typename... Ts>
std::vector<std::uint8_t> pack(const Ts&... values) {
    std::vector<std::uint8_t> out;
    (put(out, values), ...);
    return out;
}

std::string hex(const std::vector<std::uint8_t>& bytes) {
    std::string s;
    char buf[4];
    for (auto b : bytes) { std::snprintf(buf, sizeof buf, "%02x ", b); s += buf; }
    return s;
}

int main() {
    std::cout << hex(pack(std::int16_t{-2}, true, std::string{"ok"}, 1.5f)) << '\n';
    std::cout << hex(pack()) << "(empty)\n";
}
