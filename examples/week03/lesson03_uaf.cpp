// Deliberately broken: use-after-free. Compile with -fsanitize=address to see the report.
#include <iostream>

int main() {
    int* p = new int{42};
    delete p;
    std::cout << *p << '\n';   // UB: heap-use-after-free
}
