#include <array>
#include <iostream>
#include <numeric>
#include <span>
#include <vector>

// One function works for C arrays, std::array and std::vector.
double mean(std::span<const float> xs) {
    if (xs.empty()) return 0.0;
    return std::accumulate(xs.begin(), xs.end(), 0.0) / static_cast<double>(xs.size());
}

void apply_gain(std::span<float> xs, float g) {
    for (auto& x : xs) x *= g;
}

int main() {
    float c_array[4] = {1, 2, 3, 4};
    std::array<float, 4> arr{1, 2, 3, 4};
    std::vector<float> vec{1, 2, 3, 4, 5, 6};

    std::cout << "sizeof(c_array)=" << sizeof(c_array) << " std::size(c_array)=" << std::size(c_array) << '\n';
    std::cout << mean(c_array) << ' ' << mean(arr) << ' ' << mean(vec) << '\n';

    apply_gain(std::span(vec).subspan(2, 2), 10.0f);   // only elements 2 and 3
    for (float x : vec) std::cout << x << ' ';
    std::cout << '\n';

    std::array<float, 4> copy = arr;   // std::array copies like a value
    std::cout << std::boolalpha << (copy == arr) << '\n';
    try {
        std::cout << arr.at(10) << '\n';
    } catch (const std::out_of_range&) {
        std::cout << "at(10) threw out_of_range\n";
    }
}
