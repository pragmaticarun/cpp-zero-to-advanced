#include <iostream>
#include <string_view>
#include <vector>

enum class Unit { ms, samples, seconds };

std::string_view suffix(Unit u) {
    switch (u) {
        using enum Unit;
        case ms:      return "ms";
        case samples: return "samples";
        case seconds: return "s";
    }
    return "?";
}

[[nodiscard]] double to_seconds(double v, Unit u, int rate) {
    switch (u) {
        using enum Unit;
        case ms:      return v / 1000.0;
        case samples: return v / rate;
        case seconds: return v;
    }
    return 0.0;
}

[[nodiscard]] double convert(double value, Unit from, Unit to, int sample_rate = 48000) {
    const double s = to_seconds(value, from, sample_rate);
    switch (to) {
        using enum Unit;
        case ms:      return s * 1000.0;
        case samples: return s * sample_rate;
        case seconds: return s;
    }
    return 0.0;
}

struct Result { double value; Unit unit; };

void print(double v) { std::cout << v; }
void print(const Result& r) { print(r.value); std::cout << ' ' << suffix(r.unit) << '\n'; }

struct Job { double value; Unit from; Unit to; };

int main() {
    const std::vector<Job> jobs{{20, Unit::ms, Unit::samples},
                                {44100, Unit::samples, Unit::seconds},
                                {1.5, Unit::seconds, Unit::ms}};
    for (const auto& j : jobs) {
        print(j.value);
        std::cout << ' ' << suffix(j.from) << " -> ";
        print(Result{convert(j.value, j.from, j.to), j.to});
    }
    std::cout << "at 44.1kHz, 20 ms = " << convert(20, Unit::ms, Unit::samples, 44100) << " samples\n";
}
