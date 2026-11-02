#include <chrono>
#include <iostream>
#include <string>
#include <vector>

template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }

template <typename T>
typename T::value_type sum(const T& c) {          // `typename`: dependent type name
    typename T::value_type total{};
    for (const auto& x : c) total += x;
    return total;
}

void print_all(const auto& c) {                   // abbreviated function template (C++20)
    for (const auto& x : c) std::cout << x << ' ';
    std::cout << '\n';
}

int main() {
    using namespace std::chrono_literals;
    std::cout << clamp_to(15, 0, 10) << '\n';
    std::cout << clamp_to(0.7, 0.0, 1.0) << '\n';
    std::cout << clamp_to<double>(1.7, 0, 1) << '\n';           // explicit T
    std::cout << clamp_to(250ms, 0ms, 100ms).count() << "ms\n";  // works for any type with <
    std::cout << clamp_to(std::string{"m"}, std::string{"a"}, std::string{"k"}) << '\n';

    std::vector<int> v{1, 2, 3, 4};
    std::cout << sum(v) << '\n';
    print_all(v);
    print_all(std::vector<std::string>{"templates", "are", "recipes"});
}
