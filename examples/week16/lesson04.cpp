#include <chrono>
#include <expected>
#include <iostream>
#include <string>
#include <string_view>

namespace mixer {
inline namespace v2 {                                   // default version; v1 kept for old clients

struct Channel { int index; explicit constexpr Channel(int i) : index{i} {} };
struct Gain {
    double linear;
    static constexpr Gain from_percent(double p) { return Gain{p / 100.0}; }
};
using Fade = std::chrono::milliseconds;

enum class Error { bad_channel, out_of_range };
constexpr std::string_view describe(Error e) { return e == Error::bad_channel ? "bad channel" : "gain out of range"; }

class Console {
public:
    [[nodiscard("check whether the change was applied")]]
    std::expected<void, Error> set_volume(Channel ch, Gain g, Fade fade = Fade{0}) {
        if (ch.index < 0 || ch.index >= 8) return std::unexpected{Error::bad_channel};
        if (g.linear < 0 || g.linear > 2) return std::unexpected{Error::out_of_range};
        std::cout << "ch" << ch.index << " -> " << g.linear << " over " << fade.count() << "ms\n";
        return {};
    }
    [[deprecated("use set_volume(Channel, Gain, Fade)")]]
    bool setVol(int ch, double v) { return set_volume(Channel{ch}, Gain{v}).has_value(); }
};

}  // namespace v2
namespace v1 { inline int api_version() { return 1; } }
inline int api_version() { return 2; }
}  // namespace mixer

int main() {
    using namespace std::chrono_literals;
    mixer::Console c;
    // c.set_volume(0.8, 1);                            // won't compile: arguments can't be mixed up
    if (auto r = c.set_volume(mixer::Channel{1}, mixer::Gain::from_percent(80), 250ms); !r)
        std::cout << "error: " << describe(r.error()) << '\n';
    if (auto r = c.set_volume(mixer::Channel{9}, mixer::Gain{0.5}); !r)
        std::cout << "error: " << describe(r.error()) << '\n';
    std::cout << "api v" << mixer::api_version() << " (old clients can call v1: " << mixer::v1::api_version() << ")\n";
}
