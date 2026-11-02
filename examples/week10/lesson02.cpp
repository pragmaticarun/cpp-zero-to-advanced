#include <array>
#include <chrono>
#include <deque>
#include <forward_list>
#include <iostream>
#include <list>
#include <vector>

template <typename C>
long long insert_middle_ms(int n) {
    C c;
    auto t0 = std::chrono::steady_clock::now();
    for (int i = 0; i < n; ++i) {
        auto it = c.begin();
        std::advance(it, static_cast<long>(c.size() / 2));   // find the middle: O(n) either way
        c.insert(it, i);
    }
    auto t1 = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count();
}

int main() {
    constexpr auto coeffs = std::to_array({0.25f, 0.5f, 0.25f});   // no heap, size deduced
    static_assert(coeffs.size() == 3);

    std::deque<int> dq{2, 3};
    dq.push_front(1);
    dq.push_back(4);
    std::cout << "deque: " << dq.front() << ".." << dq.back() << " [2]=" << dq[2] << '\n';

    std::list<int> a{1, 2, 3}, b{10, 20};
    auto keep = a.begin();                                  // iterator to 1
    a.splice(std::next(a.begin()), b);                      // O(1): moves nodes, no copies
    std::cout << "list after splice: ";
    for (int x : a) std::cout << x << ' ';
    std::cout << "| b.size()=" << b.size() << " | iterator still valid: " << *keep << '\n';

    std::forward_list<int> fl{3, 2, 1};
    fl.push_front(4);
    fl.sort();
    std::cout << "forward_list sorted front: " << fl.front() << '\n';

    const int n = 20000;
    std::cout << "insert " << n << " in the middle (your timings will differ):\n";
    std::cout << "  vector: " << insert_middle_ms<std::vector<int>>(n) << " ms\n";
    std::cout << "  list:   " << insert_middle_ms<std::list<int>>(n) << " ms\n";
}
