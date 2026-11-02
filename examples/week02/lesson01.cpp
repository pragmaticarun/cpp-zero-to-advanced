#include <iostream>
#include <vector>

enum class Level { quiet, normal, loud, clipping };

Level classify(float s) {
    const float a = s < 0 ? -s : s;   // conditional operator
    if (a >= 1.0f) return Level::clipping;
    if (a > 0.7f) return Level::loud;
    if (a > 0.1f) return Level::normal;
    return Level::quiet;
}

int main() {
    std::vector<float> samples{0.05f, 0.4f, -0.8f, 1.2f, 0.3f};

    int index = 0;
    for (const auto& s : samples) {
        if (const Level l = classify(s); l == Level::clipping) {   // if with initializer
            std::cout << "first clip at index " << index << '\n';
            break;
        }
        ++index;
    }

    for (auto& s : samples) s *= 0.5f;   // auto& modifies the elements

    for (std::size_t i = 0; i < samples.size(); ++i) {
        switch (classify(samples[i])) {
        case Level::clipping:
            std::cout << "C";
            [[fallthrough]];          // deliberate: clipping is also "loud"
        case Level::loud:   std::cout << "L "; break;
        case Level::normal: std::cout << "n "; break;
        case Level::quiet:  std::cout << ". "; break;
        }
    }
    std::cout << '\n';
}
