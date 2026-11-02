#include <algorithm>
#include <cmath>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <string>
#include <vector>

int main() {
    std::vector<double> buf{0.5, -0.25, 0.75, -0.5};
    std::vector<double> loud(buf.size());
    std::ranges::transform(buf, loud.begin(), [](double x) { return x * 2.0; });

    std::vector<double> clipped;
    std::ranges::copy_if(loud, std::back_inserter(clipped), [](double x) { return std::abs(x) > 1.0; });
    std::cout << "samples over full scale after gain: " << clipped.size() << '\n';

    auto wrong = std::accumulate(buf.begin(), buf.end(), 0);       // int init: sums truncated values!
    auto right = std::accumulate(buf.begin(), buf.end(), 0.0);
    std::cout << "accumulate with 0: " << wrong << ", with 0.0: " << right << '\n';

    double rms = std::sqrt(std::transform_reduce(buf.begin(), buf.end(), buf.begin(), 0.0) / static_cast<double>(buf.size()));
    std::cout << "rms = " << rms << '\n';
    std::cout << "fold_left = " << std::ranges::fold_left(buf, 0.0, std::plus<>{}) << '\n';

    std::vector<int> frames{3, 1, 4, 1, 5};
    std::vector<int> offsets(frames.size());
    std::exclusive_scan(frames.begin(), frames.end(), offsets.begin(), 0);     // where each chunk starts
    for (int o : offsets) std::cout << o << ' ';
    std::cout << "(offsets)\n";

    std::vector<int> ids(6);
    std::iota(ids.begin(), ids.end(), 100);
    std::ranges::rotate(ids, ids.begin() + 2);
    std::ranges::reverse(ids);
    std::cout << "ids: ";
    for (int i : ids) std::cout << i << ' ';
    std::cout << '\n';

    std::vector<std::string> tags{"rock", "jazz", "rock", "funk", "jazz"};
    std::ranges::sort(tags);
    auto [first, last] = std::ranges::unique(tags);
    tags.erase(first, last);
    std::cout << "unique tags: " << tags.size() << '\n';

    std::vector<std::string> a{"funk", "jazz", "rock"}, b{"jazz", "pop"}, both;
    std::ranges::set_intersection(a, b, std::back_inserter(both));
    std::cout << "in both: " << both[0] << '\n';

    std::mt19937 rng{42};
    std::ranges::shuffle(ids, rng);                                 // deterministic for a given seed+library
    std::cout << "gcd(48000,44100)=" << std::gcd(48000, 44100) << " lcm=" << std::lcm(48000, 44100)
              << " midpoint(2e9,2.1e9)=" << std::midpoint(2'000'000'000, 2'100'000'000) << '\n';
}
