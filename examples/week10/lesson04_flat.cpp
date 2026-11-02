#include <flat_map>
#include <flat_set>
#include <iostream>
#include <string>

int main() {
    std::flat_map<std::string, int> rates{{"cd", 44100}, {"dvd", 48000}, {"hires", 96000}};
    rates["phone"] = 8000;
    for (const auto& [k, v] : rates) std::cout << k << '=' << v << ' ';   // sorted, contiguous
    std::cout << '\n';
    std::cout << "keys stored contiguously: " << rates.keys().size() << '\n';

    std::flat_set<int> ids{5, 1, 3, 1};
    std::cout << "unique sorted ids: ";
    for (int i : ids) std::cout << i << ' ';
    std::cout << '\n';
}
