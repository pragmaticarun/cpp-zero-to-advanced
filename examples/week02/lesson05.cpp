#include <cstdint>
#include <iostream>
#include <string_view>
#include <utility>

enum class Codec : std::uint8_t { aac, opus, flac };

struct StreamConfig {
    Codec codec = Codec::aac;
    int sample_rate = 48'000;
    int channels = 2;
    bool low_latency = false;
};

std::string_view name(Codec c) {
    switch (c) {
        using enum Codec;            // C++20: no need to write Codec:: below
        case aac:  return "AAC";
        case opus: return "Opus";
        case flac: return "FLAC";
    }
    return "?";
}

[[nodiscard]] bool open_stream(const StreamConfig& cfg) {
    if (cfg.channels <= 0) [[unlikely]] return false;
    std::cout << "open " << name(cfg.codec) << " @" << cfg.sample_rate << "Hz x"
              << cfg.channels << (cfg.low_latency ? " low-latency" : "") << '\n';
    return true;
}

struct Empty {};
struct WithTag {
    int value;
    [[no_unique_address]] Empty tag;   // takes no extra space
};

int main() {
    const bool ok = open_stream({.codec = Codec::opus, .low_latency = true});
    [[maybe_unused]] const bool ignored = open_stream(StreamConfig{});
    std::cout << "ok=" << ok << " underlying(flac)=" << int{std::to_underlying(Codec::flac)}
              << " sizeof(WithTag)=" << sizeof(WithTag) << '\n';
}
