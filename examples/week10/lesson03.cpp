#include <cstddef>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <string_view>
#include <unordered_map>

struct NoteKey {
    int octave; char name;
    bool operator==(const NoteKey&) const = default;
    auto operator<=>(const NoteKey&) const = default;
};
template <> struct std::hash<NoteKey> {
    std::size_t operator()(const NoteKey& k) const noexcept {
        std::size_t h = std::hash<int>{}(k.octave);
        h ^= std::hash<char>{}(k.name) + 0x9e3779b9 + (h << 6) + (h >> 2);   // hash_combine
        return h;
    }
};

struct StringHash {                                       // transparent hash (C++20 lookup)
    using is_transparent = void;
    std::size_t operator()(std::string_view s) const { return std::hash<std::string_view>{}(s); }
};

int main() {
    std::map<std::string, int, std::less<>> counts;       // transparent comparator
    for (std::string_view w : {"kick", "snare", "kick", "hat", "kick"}) ++counts[std::string{w}];
    for (const auto& [word, n] : counts) std::cout << word << '=' << n << ' ';   // sorted
    std::cout << '\n';

    std::cout << std::boolalpha << "contains(\"tom\") " << counts.contains("tom")
              << ", size still " << counts.size() << '\n';
    (void)counts["tom"];                                   // the trap: inserts!
    std::cout << "after operator[]: size " << counts.size() << '\n';

    auto [it, inserted] = counts.try_emplace("kick", 100);
    std::cout << "try_emplace kick inserted? " << inserted << " value " << it->second << '\n';
    auto [it2, ins2] = counts.insert_or_assign("hat", 9);
    std::cout << "insert_or_assign hat inserted? " << ins2 << " value " << it2->second << '\n';

    auto lo = counts.lower_bound("j"), hi = counts.upper_bound("s");     // range query
    std::cout << "keys in [j, s]: ";
    for (auto i = lo; i != hi; ++i) std::cout << i->first << ' ';
    std::cout << '\n';

    std::unordered_map<std::string, int, StringHash, std::equal_to<>> bpm{{"techno", 130}, {"house", 124}};
    std::string_view genre = "house";
    if (auto f = bpm.find(genre); f != bpm.end()) std::cout << genre << " -> " << f->second << '\n';   // no temp string

    std::unordered_map<NoteKey, double> freq{{{4, 'A'}, 440.0}, {{5, 'A'}, 880.0}};
    std::cout << "A4=" << freq.at({4, 'A'}) << '\n';

    std::set<int> s1{1, 3, 5}, s2{2, 3, 4};
    s1.merge(s2);                                          // moves nodes; duplicates stay in s2
    std::cout << "merged size " << s1.size() << ", left in s2: " << *s2.begin() << '\n';
    auto node = s1.extract(5);
    node.value() = 50;                                     // change a key without reallocating
    s1.insert(std::move(node));
    std::cout << "largest now " << *s1.rbegin() << '\n';
}
