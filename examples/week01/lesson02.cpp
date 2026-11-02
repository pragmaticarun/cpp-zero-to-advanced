#include <iostream>

// A declaration: tells the compiler the function exists.
int add(int a, int b);

namespace {                 // anonymous namespace => internal linkage
int helper(int x) { return x * 10; }
}

inline int global_counter = 0;   // C++17 inline variable: safe to put in a header

constexpr int square(int x) { return x * x; }  // instead of #define SQUARE(x)

int main() {
    ++global_counter;
    std::cout << add(2, 3) << ' ' << helper(4) << ' ' << square(1 + 2)
              << ' ' << global_counter << '\n';
}

// The definition can come later in the file (or in another file entirely).
int add(int a, int b) { return a + b; }
