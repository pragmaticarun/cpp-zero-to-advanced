#include <iostream>
#include <string>
#include <vector>

double average(const std::vector<int>& v) {   // read-only, no copy
    if (v.empty()) return 0.0;
    long long sum = 0;
    for (int x : v) sum += x;
    return static_cast<double>(sum) / static_cast<double>(v.size());
}

void normalize(std::vector<int>& v, int maxValue) {  // modifies the caller's vector
    for (int& x : v) x = x > maxValue ? maxValue : x;
}

void print_twice(const std::string& s) { std::cout << s << ' ' << s << '\n'; }

int main() {
    int volume = 5;
    int& alias = volume;
    alias = 7;
    std::cout << "volume=" << volume << '\n';

    std::vector<int> levels{3, 9, 12, 4};
    normalize(levels, 10);
    std::cout << "average=" << average(levels) << '\n';

    print_twice(std::string{"temp"});   // const& binds to a temporary

    const std::string& ref = levels.size() > 2 ? std::string{"many"} : std::string{"few"};
    auto copy = ref;            // auto drops the reference: std::string copy
    const auto& same = ref;     // keeps the reference
    std::cout << copy << ' ' << same << ' ' << std::boolalpha << (&same == &ref) << '\n';
}
