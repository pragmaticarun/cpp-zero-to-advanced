// Compiled with -fsanitize=undefined in CI: UBSan reports the signed overflow at run time.
#include <climits>
#include <cstdlib>
#include <iostream>
int main(int argc, char**) {
    int x = INT_MAX - 1 + argc;          // INT_MAX, but not a compile-time constant
    int y = x + 1;                       // signed overflow: UB
    std::cout << y << '\n';
    return EXIT_SUCCESS;
}
