#include <charconv>
#include <expected>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>

struct Config { int sample_rate = 0; int channels = 0; std::string device; };
struct ConfigError { int line; std::string message; };

std::expected<int, std::string> to_int(std::string_view s, int lo, int hi) {
    int v{};
    auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || p != s.data() + s.size()) return std::unexpected{"not a number: '" + std::string{s} + "'"};
    if (v < lo || v > hi) return std::unexpected{"out of range: " + std::string{s}};
    return v;
}

std::expected<Config, ConfigError> parse(const std::string& text) {
    Config c;
    std::istringstream in{text};
    std::string line;
    int n = 0;
    while (std::getline(in, line)) {
        ++n;
        if (line.empty() || line[0] == '#') continue;
        auto eq = line.find('=');
        if (eq == std::string::npos) return std::unexpected{ConfigError{n, "missing '='"}};
        std::string_view key{line.data(), eq}, value{line.data() + eq + 1, line.size() - eq - 1};
        if (key == "sample_rate") {
            auto v = to_int(value, 8000, 192000);
            if (!v) return std::unexpected{ConfigError{n, v.error()}};
            c.sample_rate = *v;
        } else if (key == "channels") {
            auto v = to_int(value, 1, 8);
            if (!v) return std::unexpected{ConfigError{n, v.error()}};
            c.channels = *v;
        } else if (key == "device") {
            c.device = value;
        } else {
            return std::unexpected{ConfigError{n, "unknown key '" + std::string{key} + "'"}};
        }
    }
    if (c.sample_rate == 0 || c.channels == 0) return std::unexpected{ConfigError{n, "sample_rate and channels are required"}};
    return c;
}

int main() {
    for (const char* text : {"# audio\nsample_rate=48000\nchannels=2\ndevice=hw:0\n",
                             "sample_rate=48k\nchannels=2\n",
                             "sample_rate=48000\nchanels=2\n",
                             "channels=2\n"}) {
        auto r = parse(text);
        if (r) std::cout << "ok: " << r->sample_rate << " Hz, " << r->channels << " ch, device '" << r->device << "'\n";
        else std::cout << "line " << r.error().line << ": " << r.error().message << '\n';
    }
}
