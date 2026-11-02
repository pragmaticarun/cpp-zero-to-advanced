#include <cstdint>
#include <expected>
#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

enum class ParseError { truncated, too_long, empty_key };
std::string_view to_string(ParseError e) {
    switch (e) {
        case ParseError::truncated: return "truncated";
        case ParseError::too_long: return "too_long";
        case ParseError::empty_key: return "empty_key";
    }
    return "?";
}

using Field = std::pair<std::string, std::string>;

// Format: repeated [klen:u8][key bytes][vlen:u8][value bytes]
std::expected<std::vector<Field>, ParseError> parse(std::span<const std::uint8_t> in) {
    std::vector<Field> out;
    auto take = [&](std::size_t n) -> std::expected<std::span<const std::uint8_t>, ParseError> {
        if (n > in.size()) return std::unexpected{ParseError::truncated};
        auto s = in.first(n);
        in = in.subspan(n);
        return s;
    };
    while (!in.empty()) {
        auto klen = take(1); if (!klen) return std::unexpected{klen.error()};
        if ((*klen)[0] == 0) return std::unexpected{ParseError::empty_key};
        if ((*klen)[0] > 64) return std::unexpected{ParseError::too_long};
        auto key = take((*klen)[0]); if (!key) return std::unexpected{key.error()};
        auto vlen = take(1); if (!vlen) return std::unexpected{vlen.error()};
        auto val = take((*vlen)[0]); if (!val) return std::unexpected{val.error()};
        out.emplace_back(std::string(key->begin(), key->end()), std::string(val->begin(), val->end()));
    }
    return out;
}

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
    (void)parse({data, size});                     // must never crash, whatever the bytes
    return 0;
}

int main() {
    struct Case { const char* name; std::vector<std::uint8_t> bytes; };
    std::vector<Case> cases{
        {"valid", {4, 'r', 'a', 't', 'e', 5, '4', '8', '0', '0', '0', 2, 'c', 'h', 1, '2'}},
        {"empty input", {}},
        {"truncated key", {10, 'a', 'b'}},
        {"value length past end", {1, 'k', 200, 'v'}},
        {"zero-length key", {0, 1, 'x'}},
        {"oversized key", {200}},
    };
    for (const auto& c : cases) {
        auto r = parse(c.bytes);
        std::cout << c.name << ": ";
        if (r) { std::cout << r->size() << " field(s)"; for (auto& [k, v] : *r) std::cout << ' ' << k << '=' << v; }
        else std::cout << "error " << to_string(r.error());
        std::cout << '\n';
    }
    std::uint64_t state = 1;                         // mini fuzz loop: random bytes must never crash
    for (int i = 0; i < 2000; ++i) {
        std::vector<std::uint8_t> buf(state % 40);
        for (auto& b : buf) { state = state * 6364136223846793005ULL + 1442695040888963407ULL; b = static_cast<std::uint8_t>(state >> 56); }
        LLVMFuzzerTestOneInput(buf.data(), buf.size());
    }
    std::cout << "2000 random inputs parsed without crashing\n";
}
