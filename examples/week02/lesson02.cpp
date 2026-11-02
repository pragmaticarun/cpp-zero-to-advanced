#include <iostream>
#include <string>

void describe(int x)                { std::cout << "int " << x << '\n'; }
void describe(double x)             { std::cout << "double " << x << '\n'; }
void describe(const std::string& s) { std::cout << "string \"" << s << "\"\n"; }

// Default argument
std::string pad(const std::string& s, std::size_t width = 8, char fill = '.') {
    if (s.size() >= width) return s;
    return s + std::string(width - s.size(), fill);
}

// Deduced return type and an abbreviated function template (C++20)
auto square(int x) { return x * x; }
auto largest(auto a, auto b) { return a > b ? a : b; }

// Recursion
long long factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }

int main() {
    describe(42);
    describe(2.5f);                  // float -> double is a promotion
    describe('x');                   // char -> int is a promotion
    describe(std::string{"hello"});
    std::cout << '[' << pad("abc") << "] [" << pad("abc", 5, '-') << "]\n";
    std::cout << square(7) << ' ' << largest(3, 9) << ' ' << largest(2.5, 1.5) << '\n';
    std::cout << "20! = " << factorial(20) << '\n';
}
