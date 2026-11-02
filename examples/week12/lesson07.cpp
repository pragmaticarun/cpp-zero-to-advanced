#include <bitset>
#include <cmath>
#include <iostream>
#include <limits>
#include <numbers>
#include <random>
#include <regex>
#include <source_location>
#include <string>
#include <string_view>

void log(std::string_view msg, std::source_location loc = std::source_location::current()) {
    std::cout << "[" << loc.function_name() << ":" << loc.line() << "] " << msg << '\n';
}

int main() {
    std::mt19937 rng{12345};                                   // fixed seed: reproducible engine
    std::mt19937 rng2{12345};
    std::cout << std::boolalpha << "same seed, same first value: " << (rng() == rng2()) << '\n';
    std::uniform_int_distribution<int> die{1, 6};
    int counts[7]{};
    for (int i = 0; i < 6000; ++i) ++counts[die(rng)];
    bool roughly_uniform = true;
    for (int f = 1; f <= 6; ++f) roughly_uniform = roughly_uniform && counts[f] > 850 && counts[f] < 1150;
    std::cout << "6000 rolls roughly uniform: " << roughly_uniform << '\n';

    std::regex tag{R"((\w+)=(\d+))"};
    std::string cfg = "rate=48000 bits=24 ch=2";
    for (std::sregex_iterator it{cfg.begin(), cfg.end(), tag}, end; it != end; ++it)
        std::cout << (*it)[1] << " -> " << (*it)[2] << "; ";
    std::cout << '\n';

    std::cout << "pi=" << std::numbers::pi << " hypot(3,4)=" << std::hypot(3.0, 4.0)
              << " lerp(0,10,0.25)=" << std::lerp(0.0, 10.0, 0.25) << '\n';
    std::cout << "int max=" << std::numeric_limits<int>::max()
              << " float min (smallest positive normal)=" << std::numeric_limits<float>::min()
              << " float lowest=" << std::numeric_limits<float>::lowest() << '\n';
    std::cout << "0.1+0.2==0.3? " << (0.1 + 0.2 == 0.3)
              << ", within epsilon? " << (std::abs(0.1 + 0.2 - 0.3) < std::numeric_limits<double>::epsilon()) << '\n';

    std::bitset<8> status{"10010110"};
    status.set(0);
    std::cout << "status=" << status << " count=" << status.count() << " bit7=" << status.test(7) << '\n';

    log("hello from source_location");
}
