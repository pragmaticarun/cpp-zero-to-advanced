#include <charconv>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

std::optional<int> parse_int(std::string_view s) {
    int v{};
    auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || p != s.data() + s.size()) return std::nullopt;
    return v;
}
std::optional<int> valid_bpm(int bpm) { return bpm >= 20 && bpm <= 300 ? std::optional{bpm} : std::nullopt; }

template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

using Json = std::variant<std::monostate, double, std::string, std::vector<double>>;

std::string describe(const Json& j) {
    return std::visit(overloaded{
        [](std::monostate) { return std::string{"null"}; },
        [](double d) { return "number " + std::to_string(d); },
        [](const std::string& s) { return "string \"" + s + '"'; },
        [](const std::vector<double>& v) { return "array of " + std::to_string(v.size()); },
    }, j);
}

int main() {
    for (std::string_view s : {"120", "12x", "999"}) {
        auto bpm = parse_int(s).and_then(valid_bpm).transform([](int b) { return b * 2; });
        std::cout << s << " -> " << (bpm ? std::to_string(*bpm) + " half-beats/min" : std::string{"invalid"}) << '\n';
    }
    std::cout << "value_or: " << parse_int("oops").value_or(-1) << '\n';
    try { (void)parse_int("x").value(); } catch (const std::bad_optional_access&) { std::cout << "bad_optional_access\n"; }

    std::vector<Json> values{Json{}, 3.5, std::string{"hi"}, std::vector<double>{1, 2, 3}};
    for (const auto& j : values) std::cout << describe(j) << '\n';

    Json j = 2.0;
    std::cout << std::boolalpha << std::holds_alternative<double>(j) << ' ' << j.index() << '\n';
    if (auto* s = std::get_if<std::string>(&j)) std::cout << *s; else std::cout << "not a string\n";
    try { (void)std::get<std::string>(j); } catch (const std::bad_variant_access&) { std::cout << "bad_variant_access\n"; }
}
