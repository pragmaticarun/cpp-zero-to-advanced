#include <iostream>

int main() {
    int a = 0, b = 0;
    if (!(std::cin >> a >> b)) {
        std::cout << "invalid input\n";
        return 1;
    }
    std::cout << "sum=" << a + b << " product=" << a * b << '\n';
}
