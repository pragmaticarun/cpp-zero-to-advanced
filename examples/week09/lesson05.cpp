#include <cassert>
#include <climits>
#include <iostream>
#include <utility>

// The overflow check the optimizer may delete: x + 1 can "never" be smaller than x
bool will_overflow_wrong(int x) { return x + 1 < x; }          // UB when x == INT_MAX
bool will_overflow_right(int x) { return x == INT_MAX; }       // check before doing the operation

constexpr int checked_add(int a, int b) {
    if ((b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b)) return 0;   // saturate-ish: no UB
    return a + b;
}
static_assert(checked_add(INT_MAX, 1) == 0);

enum class Mode { mono, stereo };
int channels(Mode m) {
    switch (m) {
        case Mode::mono: return 1;
        case Mode::stereo: return 2;
    }
    std::unreachable();                       // C++23: promise to the optimizer; UB if reached
}

int average(const int* v, int n) {
    assert(v != nullptr && n > 0 && "average: need at least one value");   // internal invariant
    long long s = 0;
    for (int i = 0; i < n; ++i) s += v[i];
    return static_cast<int>(s / n);
}

int main() {
    std::cout << std::boolalpha << "right check: " << will_overflow_right(INT_MAX) << '\n';
    std::cout << "checked_add(INT_MAX, 1) = " << checked_add(INT_MAX, 1) << '\n';
    std::cout << "channels(stereo) = " << channels(Mode::stereo) << '\n';
    int data[] = {3, 5, 10};
    std::cout << "average = " << average(data, 3) << '\n';
    (void)&will_overflow_wrong;               // shown, never called with INT_MAX
}
