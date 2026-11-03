#include <charconv>
#include <format>
#include <iomanip>
#include <iostream>
#include <print>
#include <ranges>
#include <sstream>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

struct Level { double db; };

template <>
struct std::formatter<Level> : std::formatter<double> {        // reuse double's spec parsing
    auto format(const Level& l, std::format_context& ctx) const {
        auto out = std::formatter<double>::format(l.db, ctx);
        return std::format_to(out, " dB");
    }
};

int main() {
    std::println("{:<8}|{:>8}|{:^8}|", "left", "right", "mid");
    std::println("{:08.3f} {:+d} {:#x} {:#b} {:e}", 3.14159, 42, 255, 5, 12345.678);
    std::println("{1} before {0}", "world", "hello");
    std::println("{:>10.1f}", Level{-3.25});
    std::vector<int> v{1, 2, 3};
#if defined(__cpp_lib_format_ranges)
    std::println("ranges: {}", v);                  // C++23 range formatting (GCC 15+, Clang 16+)
#else
    std::println("ranges: [{}, {}, {}]", v[0], v[1], v[2]);   // fallback for GCC 14
#endif
    std::string s = std::format("{}-{:03}", "take", 7);
    std::cout << s << '\n';

    std::cout << std::hex << 255 << ' ' << 16 << std::dec << ' ' << 16 << '\n';   // hex was sticky
    std::cout << std::fixed << std::setprecision(2) << 2.0 / 3 << '\n';
    std::cout.unsetf(std::ios::floatfield);

    std::istringstream in{"48000 2 stereo"};
    int rate = 0, ch = 0; std::string mode;
    in >> rate >> ch >> mode;
    std::cout << rate << '/' << ch << '/' << mode << '\n';

    std::string_view text = "1234abc";
    int value = 0;
    auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), value);
    std::cout << "parsed " << value << ", stopped at '" << ptr << "', ok=" << (ec == std::errc{}) << '\n';
    char buf[32];
    auto res = std::to_chars(buf, buf + sizeof buf, 0.1 + 0.2);       // shortest round-trip repr
    std::cout << "to_chars(0.1+0.2) = " << std::string_view(buf, static_cast<std::size_t>(res.ptr - buf)) << '\n';

    std::u8string_view word = u8"caf\u00e9";
    std::cout << "u8\"cafe-acute\" has " << word.size() << " bytes for 4 characters\n";
}
