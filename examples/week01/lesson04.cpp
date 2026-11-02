#include <iostream>
#include <string>

constexpr int kSampleRate = 48'000;          // compile-time constant
constexpr int kFrameMs = 20;
constexpr int kSamplesPerFrame = kSampleRate * kFrameMs / 1000;

int main() {
    int buffer[kSamplesPerFrame]{};          // OK: size is a constant expression; {} zero-fills
    const auto user = std::string{"Arun"};   // const: computed at runtime, never modified
    auto volume = 0.8;                       // double
    int level{static_cast<int>(volume * 10)};  // explicit conversion; {} would reject implicit narrowing

    decltype(level) copy = level;            // int
    std::cout << user << ": " << kSamplesPerFrame << " samples/frame, level "
              << copy << ", buffer[0]=" << buffer[0] << '\n';
}
