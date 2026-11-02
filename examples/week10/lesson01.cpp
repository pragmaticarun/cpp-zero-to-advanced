#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Sample { int t; float v; Sample(int tt, float vv) : t{tt}, v{vv} {} };

int main() {
    std::vector<int> v;
    std::size_t last_cap = v.capacity();
    int reallocs = 0;
    for (int i = 0; i < 1000; ++i) {
        v.push_back(i);
        if (v.capacity() != last_cap) { ++reallocs; last_cap = v.capacity(); }
    }
    std::cout << "size=" << v.size() << " reallocations=" << reallocs << " (geometric growth; count is implementation-specific)\n";

    std::vector<int> r;
    r.reserve(1000);
    const int* before = r.data();
    for (int i = 0; i < 1000; ++i) r.push_back(i);
    std::cout << "with reserve: buffer moved? " << std::boolalpha << (before != r.data()) << '\n';

    std::vector<Sample> samples;
    samples.emplace_back(0, 0.5f);                   // constructed in place
    samples.push_back(Sample{1, 0.25f});
    std::cout << "samples=" << samples.size() << '\n';

    std::vector<int> data{5, 0, 3, 0, 0, 7, 1};
    std::vector<int> copy = data;
    auto removed = std::erase_if(data, [](int x) { return x == 0; });             // C++20
    copy.erase(std::remove(copy.begin(), copy.end(), 0), copy.end());              // classic idiom
    std::cout << "removed " << removed << ": ";
    for (int x : data) std::cout << x << ' ';
    std::cout << "| idiom gives same? " << (data == copy) << '\n';

    std::vector<int> work{1, 0, 2};                  // safe modification while iterating: indices
    for (std::size_t i = 0; i < work.size(); ++i)
        if (work[i] == 0) work.push_back(9);
    std::cout << "work.size()=" << work.size() << '\n';

    std::vector<bool> flags(10);
    flags[3] = true;
    auto proxy = flags[3];                            // a proxy, not bool&
    std::cout << "vector<bool> proxy reads " << static_cast<bool>(proxy) << '\n';
}
