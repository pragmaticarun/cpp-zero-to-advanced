#include <cstdio>
#include <cstring>
#include <iostream>

// What a C header would declare; extern "C" disables mangling so C code can link to it
extern "C" {
    int mixer_version(void);
    double mixer_apply_gain(double sample, double gain);
}

namespace {                                    // internal linkage: invisible to other TUs
int helper_calls = 0;
double clamp1(double x) { ++helper_calls; return x > 1.0 ? 1.0 : (x < -1.0 ? -1.0 : x); }
}

extern "C" int mixer_version(void) { return 3; }
extern "C" double mixer_apply_gain(double sample, double gain) { return clamp1(sample * gain); }

inline constexpr int kMaxChannels = 32;        // C++17 inline variable: safe to define in a header

int compare_ints(const void* a, const void* b) {
    int x = *static_cast<const int*>(a), y = *static_cast<const int*>(b);
    return (x > y) - (x < y);
}

int main() {
    std::cout << "C API version " << mixer_version() << ", gain(0.8, 2) = " << mixer_apply_gain(0.8, 2.0) << '\n';
    int v[] = {5, 2, 9, 1};
    std::qsort(v, 4, sizeof(int), compare_ints);  // a C library calling back into C++
    for (int x : v) std::cout << x << ' ';
    std::cout << "\nhelper calls: " << helper_calls << ", max channels " << kMaxChannels << '\n';
}
