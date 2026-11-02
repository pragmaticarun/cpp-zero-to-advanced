#include <concepts>
#include <cstddef>
#include <forward_list>
#include <iostream>
#include <iterator>
#include <list>
#include <string>
#include <vector>

template <typename T>
concept Averageable = requires(T a, T b, std::size_t n) {
    { a + b } -> std::convertible_to<T>;
    { a / n } -> std::convertible_to<T>;
    T{};
};

template <Averageable T>
T average(const std::vector<T>& v) {
    T total{};
    for (const auto& x : v) total = total + x;
    return v.empty() ? T{} : total / v.size();
}

template <std::integral T>
T gcd(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }

template <std::input_iterator It>
const char* advance_by(It& it, int n) { while (n-- > 0) ++it; return "step-by-step"; }

template <std::random_access_iterator It>                       // more constrained: wins when it matches
const char* advance_by(It& it, int n) { it += n; return "jump"; }

void print_count(std::unsigned_integral auto n) { std::cout << "count=" << n << '\n'; }

template <typename T>
    requires std::totally_ordered<T> && std::copyable<T>
T largest(T a, T b) { return a < b ? b : a; }

int main() {
    std::cout << average(std::vector<double>{1.0, 2.0, 4.5}) << '\n';
    std::cout << gcd(48, 18) << '\n';

    std::vector<int> v{1, 2, 3, 4, 5};
    std::list<int> l{1, 2, 3, 4, 5};
    auto vi = v.begin();
    auto li = l.begin();
    std::cout << advance_by(vi, 3) << " -> " << *vi << '\n';
    std::cout << advance_by(li, 3) << " -> " << *li << '\n';

    print_count(3u);
    std::cout << largest(std::string{"pear"}, std::string{"apple"}) << '\n';
    static_assert(!Averageable<std::string>);       // no string / size_t
}
