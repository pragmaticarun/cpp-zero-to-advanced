#include <algorithm>
#include <execution>
#include <iostream>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> v(1'000'000);
    std::iota(v.begin(), v.end(), 0);
    std::reverse(v.begin(), v.end());

    std::sort(std::execution::par, v.begin(), v.end());
    std::cout << "sorted: " << std::boolalpha << std::is_sorted(v.begin(), v.end()) << '\n';

    long long total = std::reduce(std::execution::par, v.begin(), v.end(), 0LL);
    std::cout << "reduce: " << total << '\n';

    long long sq = std::transform_reduce(std::execution::par_unseq, v.begin(), v.begin() + 1000, 0LL,
                                         std::plus<>{}, [](int x) { return static_cast<long long>(x) * x; });
    std::cout << "sum of squares 0..999: " << sq << '\n';

    std::vector<double> out(v.size());
    std::transform(std::execution::par_unseq, v.begin(), v.end(), out.begin(), [](int x) { return x * 0.5; });
    std::cout << "out[10] = " << out[10] << '\n';
}
