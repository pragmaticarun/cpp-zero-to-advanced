#include <cstdint>
#include <expected>
#include <filesystem>
#include <iostream>
#include <string>
#include <system_error>
#include <vector>

enum class ParseError { too_short, bad_magic, bad_channels };

std::string to_string(ParseError e) {
    switch (e) {
        case ParseError::too_short: return "too short";
        case ParseError::bad_magic: return "bad magic";
        case ParseError::bad_channels: return "bad channel count";
    }
    return "?";
}

struct Header { int channels; int rate; };

[[nodiscard]] std::expected<std::vector<std::uint8_t>, ParseError> check_size(std::vector<std::uint8_t> b) {
    if (b.size() < 6) return std::unexpected{ParseError::too_short};
    return b;
}
[[nodiscard]] std::expected<std::vector<std::uint8_t>, ParseError> check_magic(std::vector<std::uint8_t> b) {
    if (b[0] != 'S' || b[1] != 'N') return std::unexpected{ParseError::bad_magic};
    return b;
}
[[nodiscard]] std::expected<Header, ParseError> decode(const std::vector<std::uint8_t>& b) {
    if (b[2] == 0 || b[2] > 8) return std::unexpected{ParseError::bad_channels};
    return Header{b[2], (b[3] << 16) | (b[4] << 8) | b[5]};
}

void report(const std::vector<std::uint8_t>& bytes) {
    auto result = check_size(bytes).and_then(check_magic).and_then(decode)
                      .transform([](Header h) { return std::to_string(h.channels) + "ch @ " + std::to_string(h.rate) + " Hz"; })
                      .transform_error(to_string);
    std::cout << (result ? "ok: " + *result : "error: " + result.error()) << '\n';
}

int main() {
    report({'S', 'N', 2, 0x00, 0xBB, 0x80});
    report({'S', 'N', 2});
    report({'X', 'X', 2, 0, 0, 0});
    report({'S', 'N', 0, 0, 0, 0});

    std::error_code ec;
    auto size = std::filesystem::file_size("/definitely/not/here.wav", ec);   // non-throwing overload
    std::cout << "file_size failed? " << std::boolalpha << static_cast<bool>(ec)
              << " (no_such_file: " << (ec == std::errc::no_such_file_or_directory) << ")\n";
    (void)size;
    try {
        (void)std::filesystem::file_size("/definitely/not/here.wav");           // throwing overload
    } catch (const std::filesystem::filesystem_error& e) {
        std::cout << "filesystem_error code matches: " << (e.code() == std::errc::no_such_file_or_directory) << '\n';
    }
}
