#include <bit>
#include <cstdint>
#include <iostream>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

template <typename T>
void encode(std::vector<std::uint8_t>& out, const T& value) {
    using U = std::remove_cvref_t<T>;
    if constexpr (std::is_same_v<U, bool>) {
        out.push_back(value ? 1 : 0);
    } else if constexpr (std::is_integral_v<U>) {          // big-endian bytes
        for (int i = sizeof(U) - 1; i >= 0; --i) out.push_back(static_cast<std::uint8_t>(value >> (8 * i)));
    } else if constexpr (std::is_floating_point_v<U>) {
        using Bits = std::conditional_t<sizeof(U) == 4, std::uint32_t, std::uint64_t>;
        encode(out, std::bit_cast<Bits>(value));
    } else if constexpr (std::is_same_v<U, std::string>) {
        encode(out, static_cast<std::uint16_t>(value.size()));
        out.insert(out.end(), value.begin(), value.end());
    } else {
        static_assert(sizeof(U) == 0, "encode: unsupported type");   // fires only if instantiated
    }
}

// Pre-C++20 detection idiom: does T have .size()?
template <typename, typename = void> struct has_size : std::false_type {};
template <typename T> struct has_size<T, std::void_t<decltype(std::declval<const T&>().size())>> : std::true_type {};

// Pre-C++20 SFINAE overloads
template <typename T, std::enable_if_t<has_size<T>::value, int> = 0>
std::size_t length(const T& t) { return t.size(); }
template <typename T, std::enable_if_t<!has_size<T>::value, int> = 0>
std::size_t length(const T&) { return 1; }

int main() {
    std::vector<std::uint8_t> bytes;
    encode(bytes, std::uint16_t{0x1234});
    encode(bytes, true);
    encode(bytes, 1.0f);
    encode(bytes, std::string{"hi"});
    std::cout << std::hex;
    for (auto b : bytes) std::cout << static_cast<int>(b) << ' ';
    std::cout << std::dec << '\n';

    std::cout << "has_size<string>=" << has_size<std::string>::value
              << " has_size<int>=" << has_size<int>::value << '\n';
    std::cout << length(std::string{"abc"}) << ' ' << length(42) << '\n';
    static_assert(std::is_trivially_copyable_v<float>);
}
