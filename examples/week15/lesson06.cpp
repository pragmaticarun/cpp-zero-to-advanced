#include <cstdint>
#include <iostream>
#include <limits>
#include <span>
#include <stdexcept>
#include <utility>
#include <vector>

template <typename To, typename From>
To narrow_checked(From v) {                            // like gsl::narrow
    if (!std::in_range<To>(v)) throw std::range_error{"narrowing would lose data"};
    return static_cast<To>(v);
}

double average(std::span<const double> xs) {          // pointer+length travel together
    if (xs.empty()) return 0.0;
    double s = 0;
    for (double x : xs) s += x;                        // no index arithmetic to get wrong
    return s / static_cast<double>(xs.size());
}

int main() {
    std::vector<double> levels{0.5, 0.25, 0.75};
    std::cout << "average " << average(levels) << '\n';
    try { (void)levels.at(10); } catch (const std::out_of_range&) { std::cout << "at() caught out-of-bounds\n"; }

    int count = -1;
    std::size_t size = 3;
    std::cout << std::boolalpha << "-1 < 3u with raw compare: " << (static_cast<unsigned>(count) < size)
              << ", with cmp_less: " << std::cmp_less(count, size) << '\n';
    try { (void)narrow_checked<std::uint8_t>(300); } catch (const std::range_error& e) { std::cout << e.what() << '\n'; }
    std::cout << "narrow 200 -> " << int{narrow_checked<std::uint8_t>(200)} << '\n';

    int initialized{};                                 // always initialize
    std::cout << "initialized = " << initialized << '\n';
}
